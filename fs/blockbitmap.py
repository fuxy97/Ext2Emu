__author__ = 'fuxy'

from fs import fs
from fs import sysblock
import math

block_bitmap = sysblock.SysBlock(fs.BB_TYPE)


def find_first_free_block():
    for i, b in enumerate(block_bitmap.block_buffer):
        if b != 255:
            return fs.find_first_zero_bit(b) + i * 8


def set_used_block(group_bn):
    byte = group_bn // 8
    block_bitmap.block_buffer[byte] = fs.set_bit(group_bn % 8, block_bitmap.block_buffer[byte])


def set_free_block(group_bn):
    byte = group_bn // 8
    block_bitmap.block_buffer[byte] = fs.free_bit(group_bn % 8, block_bitmap.block_buffer[byte])
