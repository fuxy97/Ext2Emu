__author__ = 'fuxy'

from fs import sysblock
from fs.sysblock import OFFSET_INDEX
from fs.sysblock import SIZE_INDEX
from fs import fs
from fs.superblock import superblock


class SysTableBlock(sysblock.SysBlock):
    def __init__(self, type_id, offset_bn):
        self.offset_bn = offset_bn
        self.block_buffer_bn = 0
        self.struct_size = fs.STRUCT_SIZES[type_id]
        sysblock.SysBlock.__init__(self, type_id)

    def _check_index(self, index):
        if self.offset_bn + (index * self.struct_size //
                             (fs.bytes_to_int(superblock.get_field(superblock.s_log_block_size)) * 1024)) \
           != self.block_buffer_bn:
            raise IndexError("Can't read structure #{0} in this block. Offset: {1}. Block number: {2}"
                             .format(index, self.offset_bn, self.block_buffer_bn))


    def set_field(self, index, field, value):
        self._check_index(index)
        index %= fs.bytes_to_int(superblock.get_field(superblock.s_log_block_size)) * 1024 // self.struct_size

        self.block_buffer[index * self.struct_size + field[OFFSET_INDEX]:
                          index * self.struct_size + field[OFFSET_INDEX] + field[SIZE_INDEX]] = \
                          sysblock.to_bytes(value, field[SIZE_INDEX])

    def get_field(self, index, field):
        self._check_index(index)
        index %= fs.bytes_to_int(superblock.get_field(superblock.s_log_block_size)) * 1024 // self.struct_size

        return self.block_buffer[index * self.struct_size + field[OFFSET_INDEX]:
                                 index * self.struct_size + field[OFFSET_INDEX] + field[SIZE_INDEX]]

    def load(self, block_number):
        self.block_buffer_bn = block_number
        sysblock.SysBlock.load(self, block_number)

    def unload(self, block_number):
        self.block_buffer_bn = block_number
        sysblock.SysBlock.unload(self, block_number)
