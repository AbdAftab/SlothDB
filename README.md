# SlothDB

SlothDB is a purposefully simple, terrible, and slow "database" engine. Created for the purpose of learning new things

## Overview

SlothDB is a "database" system that:
- Stores strings as binary (bit) patterns, each bit is stored in it's own memory block (16 bytes by default)
- Only allows for a string to start with a unique character ONCE! (This means you can't have "hello" and "hey" in the same database)
- Continuing the above point, if a duplicate starting character is found, it gets overwritten.
- Includes a simple query language (SlothQL)
- Manages memory with a custom memory manager
- Persists data to disk (re-writes anything on your memory to disk after every insert or deletion)
- Uses Python

### Core Engine

The system consists of three main components:

1. **SlothDB Engine** (`engine.py`): The core database engine, handles everything.
2. **Memory Manager** (`memory_manager.py`): Manages memory allocation and deallocation.
3. **Memory Block** (`mem_block.py`): Represents a block of memory and provides read/write operations.

## Usage

### Basic API

```python
from slothdb import SlothDB

# Initialize the database
db = SlothDB()

# Store a string
db.store("hello world")

# Retrieve a string by its first character
result = db.retrieve("h")
print(result)  # Returns "hello world"

# Delete an entry
db.delete("h")

# List all entries
entries = db.list_entries()

# Get database status
status = db.status()

# Synchronize data to disk
db.sync()

# Close the database
db.close()
```

### Command Line Interface

SlothDB comes with a command-line interface with basic query commands:

Available commands:

- `SELECT <bit_pattern>`: Search for strings containing the specified bit pattern
- `INSERT "<string>"`: Store a new string in the database
- `DELETE <char>`: Delete an entry by its first character
- `LIST`: List all entries in the database (shows binary representation)
- `STATUS`: Show database statistics
- `HELP`: Display help information
- `EXIT` or `QUIT`: Exit the program

## Example Session

```
     _       _   _     
    | |     | | | |    
 ___| | ___ | |_| |__  
/ __| |/ _ \| __| '_ \ 
\__ \ | (_) | |_| | | |
|___/_|\___/ \__|_| |_|  
    
SlothQL Interface
Type HELP for available commands or EXIT to quit

SlothQL> INSERT "hello"
Successfully inserted 'hello'

SlothQL> INSERT "world"
Successfully inserted 'world'

SlothQL> SELECT 1010
Found 1 match(es) for bit pattern 1010:
1. Entry 'h': 'hello'
>>> Pattern found at: bit 8, bit 24

SlothQL> LIST
Entries in database:
0110100001100101011011000110110001101111      (Yes, it only shows you the binary)
0111011101101111011100100110110001100100

SlothQL> STATUS
{'entries': 2, 'in_memory': {'allocated_blocks': 80, 'total_memory_bytes': 1280}, 'on_disk': {'files': 80, 'total_bytes': '320 bytes'}}

SlothQL> DELETE h
Successfully deleted entry with first character 'h'

SlothQL> EXIT
```

## Use Cases
- None
