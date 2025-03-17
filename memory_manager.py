import ctypes
from mem_block import MemoryBlock
import uuid

class MemoryManager:
    def __init__(self, size=16):
        self.size = size
        self.blocks = {}
    
    def allocate(self):
        "Allocate mem block, return id of block"
        
        # Create/store new block
        new_block = MemoryBlock(self.size)
        blockid = uuid.uuid4().hex[:15] # if you're wondering why .hex, just know it removes the hypens in generating uuids
        self.blocks[blockid] = new_block

        return blockid
    
    def write(self, bit, block, next_block = None): # block/next_block refers to keys in self.blocks
        "Writes bit to block, stores next bit location"
        if block not in self.blocks:
            raise KeyError(f"Memory Block with ID {block} not found")
        
        curr_block = self.blocks[block]
        curr_block.write(bit, 0)
        
        next_addr = b'\x00' * 15 # null address, useful when writing last bit
        if next_block:
            next_addr = next_block.encode('utf-8')[:15]
        
        curr_block.write(next_addr, 1)
        
        return True
    
    def read(self, block_id):
        """Returns + recreates data given an initial block (id)"""
        
        # Old Code, had to move/re-write this into engine.py and re-write this section to be able to save data to disk :')
        # data = ""
        # curr_block = block_id
        # while curr_block:
        #     try:
        #         block = self.blocks[curr_block]
        #         bit = block.read(0, 1).decode('utf-8') # Current blocks bit
        #         data += bit
        #         next_block = block.read(1,15).rstrip(b'\x00').decode('utf-8', errors='ignore')
        #         curr_block = next_block
        #     except Exception as error:
        #         print(f"Error retrieving data: {error}")
        #         break
        # return data
        block = self.blocks[block_id]
        bit = block.read(0,1).decode('utf-8')
        next_block = block.read(1,15).rstrip(b'\x00').decode('utf-8', errors='ignore')
        if next_block:
            return bit, next_block
        return bit, None
    
    def free(self, block):
        """Delete mem block"""
        if block not in self.blocks:
            return False
        
        del self.blocks[block] # Thanks garbage collector!
        return True
    
    def get_block_addr(self, block):
        """Get block address"""
        return hex(self.blocks[block].addr)
    
    def status(self):
        "Status"
        return {
            "allocated_blocks": len(self.blocks),
            "total_memory_bytes": len(self.blocks) * self.size,
            "block_addresses": {block_id: hex(block.addr) for block_id, block in list(self.blocks.items())[:5]}
        }
