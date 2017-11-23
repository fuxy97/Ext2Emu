__author__ = 'fuxy'

from fs import systableblock
from fs import fs
from fs.superblock import superblock


def init_gdtable_iter(groups_count):
    for i in range(groups_count):
        gd = systableblock.SysTableBlock(fs.GD_TYPE, 1)
        gd.init_struct(fs.GD_NAME)
        yield gd


gdtable_blocks = None


def init_gdtable(groups_count):
    global gdtable_blocks
    gdtable_blocks = list(init_gdtable_iter(groups_count))


def load_gdtable(group_number):
    group_bn = fs.gpn_to_bn(
        group_number,
        fs.bytes_to_int(superblock.get_field(superblock.s_blocks_per_group))
    )

    for bn, gdtable_block in enumerate(gdtable_blocks):
        gdtable_block.offset_bn = group_bn + 1
        gdtable_block.load(bn + group_bn + 1)


def unload_gdtable(group_number):
    group_bn = fs.gpn_to_bn(
        group_number,
        fs.bytes_to_int(superblock.get_field(superblock.s_blocks_per_group))
    )

    for bn, gdtable_block in enumerate(gdtable_blocks):
        gdtable_block.unload(bn + group_bn + 1)


def get_gdtableblock(index):
    bn = index * fs.GD_SIZE // (fs.bytes_to_int(superblock.get_field(superblock.s_log_block_size)) * 1024)
    return gdtable_blocks[bn]
