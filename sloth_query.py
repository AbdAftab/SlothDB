#!/usr/bin/env python3
# sloth_query.py - A query language for SlothDB

import argparse
import re
import sys
from engine import SlothDB

class SlothQuery:

    def __init__(self, db_path="sloth_db_data"):
        self.db = SlothDB(db_path)
        self.commands = {
            "HELP": self._handle_help,
            "SELECT": self._handle_select,
            "INSERT": self._handle_insert,
            "DELETE": self._handle_delete,
            "LIST": self._handle_list,
            "STATUS": self._handle_status,
            "EXIT": self._handle_exit,
        }
    
    def _handle_help(self, arg):
        text = """
SlothDB Query Language Commands:
-------------------------------
SELECT <bit_pattern>
    Search for strings that contain the specified bit pattern
    Example: SELECT BITS 1010

INSERT "<string>"
    Store a new string in the database
    Example: INSERT "hello"

DELETE <char>
    Delete an entry by its first character
    Example: DELETE h

LIST
    List all entries in the database

STATUS
    Show database statistics

HELP
    Display this help message

EXIT or QUIT
    Exit the program
"""
        return text
    def _handle_select(self, args):
        """Select statements, only shows bits :)"""
        bit_pattern = args.strip()
        
        if not bit_pattern or not all(bit in '01' for bit in bit_pattern):
            return "Invalid SELECT syntax. Use 'SELECT 1011' where 1011 is a binary pattern."

        results = []
        for char in self.db.list_entries():
            data = self.db.retrieve(char)
            if data:
                binary = ''.join(format(ord(c), '08b') for c in data)
                if bit_pattern in binary:
                    results.append((char, data, binary))
        if not results:
            return f"No matches found for bit pattern {bit_pattern}"
        
        output = f"Found {len(results)} match(es) for bit pattern {bit_pattern}:\n"
        for idx, (char, text, binary) in enumerate(results, 1):
            output += f"{idx}. Entry '{char}': '{text}'\n"
            positions = [m.start() for m in re.finditer(f'(?={bit_pattern})', binary)]
            pos_str = ", ".join(f"bit {p}" for p in positions)
            output += f">>> Pattern found at: {pos_str}\n"
        
        return output
    
    def _handle_insert(self, args):
        match = re.match(r'(?:INTO)?\s*(?:["\'](.*?)["\']|(\S+))', args) # bless AI for this
        if not match:
            return "Invalid INSERT syntax. Use 'INSERT \"your string\"' or 'INSERT your_string'"
        data = match.group(1) if match.group(1) is not None else match.group(2)
        
        if not data:
            return "Cannot insert empty string"
        
        try:
            self.db.store(data)
            return f"Successfully inserted '{data}'"
        except ValueError as e:
            return f"Error: {str(e)}"
    
    def _handle_delete(self, args):
        if not args or len(args.strip()) != 1:
            return "Invalid DELETE syntax. Use 'DELETE x' where x is the first character of the entry"
        
        char = args.strip()
        if self.db.delete(char):
            return f"Successfully deleted entry with first character '{char}'"
        else:
            return f"No entry found with the starting char: {char}"
    
    def _handle_list(self, args):
        """You can see all the data you have stored! In binary!"""
        entries = self.db.list_entries()
        if not entries:
            return "Database is empty"
        output = "Entries in database:\n"
        for idx, char in enumerate(sorted(entries), 1):
            data = self.db.retrieve(char)
            binary = ''.join(format(ord(c), '08b') for c in data)
            output += f"{binary}\n"
            # output += f"{data}\n"
        
        return output
    
    def _handle_status(self, args):
        return self.db.status()
    
    def _handle_exit(self):
        self.db.close()
        sys.exit(0)
    
    def execute_query(self, query):
        if not query.strip():
            return ""
        parts = query.strip().split(maxsplit=1)
        command = parts[0].upper()
        args = parts[1] if len(parts) > 1 else ""
        
        if command in self.commands:
            return self.commands[command](args)
        else:
            return f"Unknown command: {command}. Type HELP for available commands."
    
    

def run_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="sloth_db_data")
    args = parser.parse_args()
    
    query_engine = SlothQuery(args.db)
    print(r"""
     _       _   _     
    | |     | | | |    
 ___| | ___ | |_| |__  
/ __| |/ _ \| __| '_ \ 
\__ \ | (_) | |_| | | |
|___/_|\___/ \__|_| |_|  
    """)
    print("SlothQL Interface")
    print("Type HELP for available commands or EXIT to quit")
    
    while True:
        query = input("SlothQL> ")
        if query.upper() in ("EXIT", "QUIT"):
            query_engine._handle_exit()
        
        res = query_engine.execute_query(query)
        print(res)

if __name__ == "__main__":
    run_cli()