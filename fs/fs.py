__author__ = 'fuxy'

import math

STRUCT_DIR = '.structures'
STRUCT_EXT = '.struct'

SB_TYPE = 0x00
SB_NAME = 'superblock'
SB_SIZE = 66
GD_TYPE = 0x01
GD_NAME = 'groupdescriptor'
GD_SIZE = 32
BB_TYPE = 0x02
IB_TYPE = 0x03
INODE_TYPE = 0x04
INODE_NAME = 'inode'
INODE_SIZE = 128
ADDRESS_SIZE = 4

STRUCT_SIZES = {
    SB_TYPE: SB_SIZE,
    GD_TYPE: GD_SIZE,
    INODE_TYPE: INODE_SIZE
}


def gpn_to_bn(group_number, blocks_per_group):
    return group_number * blocks_per_group


def ign_to_in(group_number, inodes_per_group, inode_in_group_number):
    return group_number * inodes_per_group + inode_in_group_number


def bn_to_igbn(block_number, blocks_per_group):
    return block_number % blocks_per_group


def int_to_bytes(value, size):
    return value.to_bytes(size, 'little')


def bytes_to_int(bytes):
    return int.from_bytes(bytes, 'little')


def find_first_zero_bit(byte):
    # i = int.from_bytes(byte, 'little', signed=False)
    return int(math.log2((~byte & 0xff) & abs(~byte)))


def set_bit(bit_number, byte):
    # i = int.from_bytes(byte, 'little', signed=False)
    return byte | 1 << bit_number


def free_bit(bit_number, byte):
    # i = int.from_bytes(byte, 'little', signed=False)
    # .to_bytes(1, 'little', signed=False)
    return byte & (~(1 << bit_number) & 0xff)


def get_groups_count(blocks_count, blocks_per_group):
    return blocks_count // blocks_per_group

