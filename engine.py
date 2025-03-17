import os
from memory_manager import MemoryManager

class SlothDB:
    MAX_STRING_LENGTH = 255
    def __init__(self, path="sloth_db_data"):
        self.path = path
        self.bit_path = os.path.join(path, 'bit_data')
        self.index_path = os.path.join(path, 'index.txt')
        self.memory = MemoryManager(16)

        os.makedirs(self.bit_path, exist_ok=True)

        self.index = {}
        if os.path.exists(self.index_path):
            with open(self.index_path, 'r') as f:
                for line in f.readlines():
                    self.index[line[0]] = line[2:] # Each line has format "{chr}:{address}"

            self._load_mem_from_data()

    def store(self, data):
        """Stores data into mem blocks"""
        if not isinstance(data, str) or not data or len(data) > self.MAX_STRING_LENGTH:
            raise ValueError("Error storing data: {data} is not a string or is too long.")
        
        binary = ''.join(format(ord(char), '08b') for char in data) # converts to 8 bits, using bin() breaks my program for some reason?
        prev_addr = None
        index_addr = None
        
        for bit in binary:
            current_addr = self.memory.allocate()
            # print(current_addr)
            if index_addr is None:
                index_addr = current_addr # I'll use this later to save the index
            if prev_addr is not None:
                self.memory.write(prev_bit, prev_addr,  current_addr)
            
            prev_addr = current_addr
            prev_bit = bit

        self.memory.write(prev_bit, prev_addr)
        self.index[data[0]] = index_addr
        self._save_data_to_disk()
        return True

    def retrieve(self, char):
        """Retrieve a string from the database by its first character"""
        if char not in self.index:
            return None
        addr = self.index[char]
        binary = ""
        while addr is not None:
            bit, addr = self.memory.read(addr)
            binary += bit
        
        byte_chunks = [binary[i:i+8] for i in range(0, len(binary), 8)]
        result = ''
        for chunk in byte_chunks:
            if len(chunk) == 8:
                result += chr(int(chunk, 2))
        
        return result
    
    def delete(self, char):
        """Delete an entry from the database"""
        if char not in self.index:
            return 
        addr = self.index[char]
        deletion_addrs = []
        while addr is not None:
            deletion_addrs.append(addr)
            try:
                bit, addr = self.memory.read(addr)
            except Exception:
                break

        for addr in deletion_addrs:
            self.memory.free(addr)
        
        del self.index[char]
        self._save_data_to_disk()
        
        return True
    
    def _load_mem_from_data(self):
        # Load all data from files, and then we have to link them
        # Create blocks for each piece of data first, LINK AFTER OR ELSE THEY DON'T EXIST

        for chr, init_addr in self.index.items():
            addr = init_addr.strip()
            mem_map = {}
            
            while addr:
                file = os.path.join(self.bit_path, addr)
                with open(file, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        bit = lines[0].strip()
                        next_addr = lines[1].strip() if len(lines) > 1 else None
                if not lines:
                    break
                new_block = self.memory.allocate()
                self.memory.write(bit, new_block) # No next_block param here, I update the addresses after (in the for loop below)
                mem_map[addr] = new_block
                addr = next_addr

            # Link all the blocks, I can do it now because every block has been allocated
            for addr, block in mem_map.items():
                file = os.path.join(self.bit_path, addr)
                with open(file,'r') as f:
                    lines = f.readlines()
                    bit = lines[0].strip()
                    next_addr = lines[1].strip() if len(lines) > 1 else None
                next_block = mem_map.get(next_addr) if next_addr else None
                self.memory.write(bit, block, next_block)
            
            self.index[chr] = mem_map[init_addr.strip()]
    
    def _save_index(self):
        with open(self.index_path, 'w') as f:
            for chr, addr in self.index.items():
                f.write(f"{chr}:{addr}\n")

    def _save_data_to_disk(self):
        for file in os.listdir(self.bit_path):
            os.remove(os.path.join(self.bit_path, file))
        
        for char, init_addr in self.index.items():
            addr = init_addr
            while addr:
                bit, block = self.memory.read(addr)

                with open(os.path.join(self.bit_path, addr), 'w') as f:
                    if block:
                        f.write(f"{bit}\n{block}")
                    else:
                        f.write(f"{bit}")
                
                addr = block
        self._save_index()
    
    
    def list_entries(self):
        return list(self.index.keys())
    
    def sync(self):
        self._save_data_to_disk()
    
    def status(self):
        memory_stats = self.memory.status()
        files = 0
        size = 0
        
        for file in os.listdir(self.bit_path):
            file_path = os.path.join(self.bit_path, file)
            if os.path.isfile(file_path):
                files += 1
                size += os.path.getsize(file_path)
        
        return {
            "entries": len(self.index),
            "in_memory": {
                "allocated_blocks": memory_stats["allocated_blocks"],
                "total_memory_bytes": memory_stats["total_memory_bytes"],
            },
            "on_disk": {
                "files": files,
                "total_bytes": f"{size} bytes",
            }
        }
    
    def close(self):
        self.sync()