__author__ = 'fuxy'

from fs import fs
from fs import sysblock

inode_bitmap = sysblock.SysBlock(fs.IB_TYPE)


def find_first_free_inode():
    for i, b in enumerate(inode_bitmap.block_buffer):
        if b != 255:
            return fs.find_first_zero_bit(b) + i * 8


def set_used_inode(group_in):
    byte = group_in // 8
    inode_bitmap.block_buffer[byte] = fs.set_bit(group_in % 8,  inode_bitmap.block_buffer[byte])


def set_free_inode(group_in):
    byte = group_in // 8
    inode_bitmap.block_buffer[byte] = fs.free_bit(group_in % 8, inode_bitmap.block_buffer[byte])
