__author__ = 'fuxy'

from fs import fs
from fs.superblock import superblock
from fs import balloc


class BufferSizeError(ValueError):
    pass


class DataBlockBuffer:
    def __init__(self):
        self.block_buffer = None
        self.block_size = None
        self.block_number = None

    def check_buffer_size(self, offset, buffer_size):
        if offset + buffer_size >= self.block_size:
            raise BufferSizeError("Buffer (offset = %d, size = %d) couldn't placed in block (size = %d)" %
                                  offset, buffer_size, self.block_size)

    def set_bytes(self, offset, byte_buffer):
        self.check_buffer_size(offset, len(byte_buffer))
        self.block_buffer[offset: offset + len(byte_buffer)] = byte_buffer

    def get_bytes(self, offset, buffer_size):
        self.check_buffer_size(offset, buffer_size)
        return self.block_buffer[offset: offset + buffer_size]

    def load(self, block_number):
        if self.block_size is None:
            self.block_size = fs.bytes_to_int(superblock.get_field(superblock.s_log_block_size)) * 1024
        self.block_number = block_number
        self.block_buffer = bytearray(balloc.read_block(block_number))

    def unload(self, block_number):
        self.block_number = block_number
        balloc.write_block(block_number, bytes(self.block_buffer))


data_block_buffer = DataBlockBuffer()
