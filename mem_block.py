import ctypes

class MemoryBlock:

    def __init__(self, size=16):
        self.size = size
        # Reserving memory so we can yoink the address, 16 bytes
        self.memory = ctypes.create_string_buffer(size)
        self.addr = ctypes.addressof(self.memory)

    def write(self, data, offset):
        "Write data to memory block, starting from offset bytes"
        if len(data) + offset > self.size:
            raise MemoryError("Data bigger than block size")
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        ctypes.memmove(self.addr + offset, data, len(data))
        return True
    
    def read(self, offset, length):
        "Return bytes from me block"
        if offset + length > self.size:
            raise IndexError("Read falls outside of mem block")
        res = ctypes.create_string_buffer(length)
        ctypes.memmove(res, self.addr + offset, length)

        return res.raw