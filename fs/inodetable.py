__author__ = 'fuxy'

from fs import fs
from fs.superblock import superblock
from fs import gdtable
from fs import systableblock
from fs import blockbitmap
from fs import gdtable

inodetable_blocks_list = []

S_IROTH = 0x4
S_IRGRP = 0x20
S_IRUSR = 0x100
S_IWUSR = 0x80
S_IWGRP = 0x10
S_IWOTH = 0x2
S_IXUSR = 0x40
S_IXGRP = 0x8
S_IXOTH = 0x1
S_IFDIR = 0x4000
S_IFREG = 0x8000


def load_inode(number):
    block_size = fs.bytes_to_int(superblock.get_field(superblock.s_log_block_size)) * 1024
    for block in inodetable_blocks_list:
        if block.first_inode_number <= number <= block.first_inode_number + block_size // fs.INODE_SIZE:
            block.loads_count += 1
            return block

    gn = number // fs.bytes_to_int(superblock.get_field(superblock.s_inodes_per_group))
    table_number = get_table_number(number)
    gdtable_block = gdtable.get_gdtableblock(gn)
    inode_table_bn = fs.bytes_to_int(gdtable_block.get_field(gn, gdtable_block.bg_inode_table))
    inode_bn = inode_table_bn + table_number * fs.INODE_SIZE // block_size

    inode_table_block = systableblock.SysTableBlock(fs.INODE_TYPE, inode_table_bn)
    inode_table_block.init_struct(fs.INODE_NAME)
    inode_table_block.load(inode_bn)
    inode_table_block.first_inode_number = (inode_bn - inode_table_bn) * block_size // fs.INODE_SIZE \
                            + gn * fs.bytes_to_int(superblock.get_field(superblock.s_inodes_per_group))
    inode_table_block.loads_count = 1
    inodetable_blocks_list.append(inode_table_block)
    return inode_table_block


def get_table_number(number):
    return number % fs.bytes_to_int(superblock.get_field(superblock.s_inodes_per_group))


def get_group_number(number):
    return number // fs.bytes_to_int(superblock.get_field(superblock.s_inodes_per_group))


def unload_inode(number):
    block_size = fs.bytes_to_int(superblock.get_field(superblock.s_log_block_size)) * 1024
    for i, block in enumerate(inodetable_blocks_list):
        if block.first_inode_number <= number < block.first_inode_number + block_size // fs.INODE_SIZE:
            block.unload(block.block_buffer_bn)
            if block.loads_count <= 1:
                del inodetable_blocks_list[i]
            else:
                block.loads_count -= 1
            break


def check_file_permissions(inode_block, inode_n, perm):
    inode_tn = get_table_number(inode_n)
    i_mode = fs.bytes_to_int(inode_block.get_field(inode_tn, inode_block.i_mode))
    return i_mode & perm == perm


def check_uid(inode_block, inode_n, uid):
    inode_tn = get_table_number(inode_n)
    i_uid = fs.bytes_to_int(inode_block.get_field(inode_tn, inode_block.i_uid))
    return i_uid == uid


def check_gid(inode_block, inode_n, gid):
    inode_tn = get_table_number(inode_n)
    i_gid = fs.bytes_to_int(inode_block.get_field(inode_tn, inode_block.i_gid))
    return i_gid == gid



I_BLOCK_SIZE = 60


def lbn_to_bn(lbn, i_block):
    first_blocks = [fs.bytes_to_int(i_block[i: i + fs.ADDRESS_SIZE]) for i in
                    range(0, (I_BLOCK_SIZE // fs.ADDRESS_SIZE - 3) * fs.ADDRESS_SIZE,
                          fs.ADDRESS_SIZE)]
    return first_blocks[lbn]


def get_last_file_bn(i_block):
    first_blocks = [bn for bn in [fs.bytes_to_int(i_block[i: i + fs.ADDRESS_SIZE]) for i in
                    range(0, (I_BLOCK_SIZE // fs.ADDRESS_SIZE - 3) * fs.ADDRESS_SIZE,
                          fs.ADDRESS_SIZE)] if bn != 0]
    return first_blocks[-1]


def free_file_blocks(inode_block, inode, i_block):
    blocks_per_group = fs.bytes_to_int(superblock.get_field(superblock.s_blocks_per_group))
    inode_tn = get_table_number(inode)
    gpn = get_group_number(inode)
    blocks_count = fs.bytes_to_int(inode_block.get_field(
        inode_tn,
        inode_block.i_blocks
    ))

    if blocks_count > 0:
        bg_block = gdtable.get_gdtableblock(gpn)
        blockbitmap.block_bitmap.load(fs.bytes_to_int(bg_block.get_field(gpn, bg_block.bg_block_bitmap)))
        first_blocks = [fs.bytes_to_int(i_block[i: i + fs.ADDRESS_SIZE]) for i in
                        range(0, blocks_count * fs.ADDRESS_SIZE, fs.ADDRESS_SIZE)]

        for bn in first_blocks:
            blockbitmap.set_free_block(fs.bn_to_igbn(bn, blocks_per_group))
        blockbitmap.block_bitmap.unload(fs.bytes_to_int(bg_block.get_field(gpn, bg_block.bg_block_bitmap)))


def extend_file_blocks(inode_block, inode, i_block):
    inode_tn = get_table_number(inode)
    gpn = get_group_number(inode)
    bg_block = gdtable.get_gdtableblock(gpn)
    blockbitmap.block_bitmap.load(fs.bytes_to_int(bg_block.get_field(gpn, bg_block.bg_block_bitmap)))
    igbn = blockbitmap.find_first_free_block()
    blocks_count = fs.bytes_to_int(inode_block.get_field(
        inode_tn,
        inode_block.i_blocks
    ))

    i_block[blocks_count * fs.ADDRESS_SIZE: (blocks_count+1) * fs.ADDRESS_SIZE] = fs.int_to_bytes(
        igbn + gpn * fs.bytes_to_int(superblock.get_field(superblock.s_blocks_per_group)),
        fs.ADDRESS_SIZE
    )
    inode_block.set_field(inode_tn, inode_block.i_block, i_block)
    inode_block.set_field(inode_tn, inode_block.i_blocks, blocks_count + 1)

    blockbitmap.set_used_block(igbn)
    blockbitmap.block_bitmap.unload(fs.bytes_to_int(bg_block.get_field(gpn, bg_block.bg_block_bitmap)))
    return igbn + gpn * fs.bytes_to_int(superblock.get_field(superblock.s_blocks_per_group))
