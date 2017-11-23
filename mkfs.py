__author__ = 'fuxy'

import partman
from fs.superblock import superblock
from fs import gdtable
from fs import blockbitmap
from fs import inodebitmap
from fs import inodetable
import device
from fs import balloc
from fs import fs
import math
import time
import uuid
from fs import sysblock


def get_blocks_count(partition_size, block_size):
    return partition_size // block_size


def create_superblock(group_number, uuid, **options):
    blocks_count = get_blocks_count(options['partition_size'], options['block_size'])
    groups_count = fs.get_groups_count(blocks_count, options['blocks_per_group'])
    inodes_count = options['inodes_per_group'] * groups_count

    superblock.load(fs.gpn_to_bn(group_number, options['blocks_per_group']))
    superblock.set_field(superblock.s_magic, 0xEF53)
    superblock.set_field(superblock.s_inodes_count, inodes_count)
    superblock.set_field(superblock.s_blocks_count, blocks_count)
    superblock.set_field(superblock.s_free_inodes_count, inodes_count - 1)
    superblock.set_field(superblock.s_free_blocks_count, blocks_count - groups_count *
                         (math.ceil(groups_count * fs.GD_SIZE / options['block_size']) +
                          math.ceil(options['inodes_per_group'] * fs.INODE_SIZE / options['block_size']) + 3) - 1)
    superblock.set_field(superblock.s_first_data_block,
                         math.ceil(groups_count * fs.GD_SIZE / options['block_size']) +
                         math.ceil(options['inodes_per_group'] * fs.INODE_SIZE / options['block_size']) + 3)

    superblock.set_field(superblock.s_log_block_size, options['block_size'] // 1024)
    superblock.set_field(superblock.s_inode_size, fs.INODE_SIZE)
    superblock.set_field(superblock.s_inodes_per_group, options['inodes_per_group'])
    superblock.set_field(superblock.s_blocks_per_group, options['blocks_per_group'])
    superblock.set_field(superblock.s_wtime, int(time.time()))
    superblock.set_field(superblock.s_state, 1)
    superblock.set_field(superblock.s_errors, 1)
    superblock.set_field(superblock.s_volume_name, options['partition_name'])
    superblock.set_field(superblock.s_uuid, uuid)
    superblock.unload(fs.gpn_to_bn(group_number, options['blocks_per_group']))


def create_gdtable(group_number):
    gdtable.load_gdtable(group_number)
    block_size = fs.bytes_to_int(superblock.get_field(superblock.s_log_block_size)) * 1024
    blocks_per_group = fs.bytes_to_int(superblock.get_field(superblock.s_blocks_per_group))
    inodes_per_group = fs.bytes_to_int(superblock.get_field(superblock.s_inodes_per_group))
    groups_count = fs.get_groups_count(fs.bytes_to_int(superblock.get_field(superblock.s_blocks_count)),
                                    fs.bytes_to_int(superblock.get_field(superblock.s_blocks_per_group)))
    gdtable_blocks_count = math.ceil(groups_count * fs.GD_SIZE / block_size)
    itable_blocks_count = math.ceil(inodes_per_group * fs.INODE_SIZE / block_size)
    
    for g in range(groups_count):
        gdtable_block = gdtable.get_gdtableblock(g)
        gdtable_block.set_field(g, gdtable_block.bg_block_bitmap, g * blocks_per_group + gdtable_blocks_count + 1)
        gdtable_block.set_field(g, gdtable_block.bg_inode_bitmap, g * blocks_per_group + gdtable_blocks_count + 2)
        gdtable_block.set_field(g, gdtable_block.bg_inode_table, g * blocks_per_group + gdtable_blocks_count + 3)
        if g == 0:
            gdtable_block.set_field(g, gdtable_block.bg_free_blocks_count, blocks_per_group - gdtable_blocks_count
                                    - itable_blocks_count - 4)
            gdtable_block.set_field(g, gdtable_block.bg_free_inodes_count, inodes_per_group - 1)
            gdtable_block.set_field(g, gdtable_block.bg_used_dirs_count, 1)
        else:
            gdtable_block.set_field(g, gdtable_block.bg_free_blocks_count, blocks_per_group - gdtable_blocks_count
                                    - itable_blocks_count - 3)
            gdtable_block.set_field(g, gdtable_block.bg_free_inodes_count, inodes_per_group)
            gdtable_block.set_field(g, gdtable_block.bg_used_dirs_count, 0)

        gdtable_block.set_field(g, gdtable_block.bg_pad, bytes(gdtable_block.bg_pad[sysblock.SIZE_INDEX]))

    gdtable.unload_gdtable(group_number)


def create_block_bitmap(group_number):
    def fillbitmap(first_data_bn, blocks_per_group):
        remaining_blocks_count = first_data_bn % 8
        for b in range(first_data_bn // 8):
            yield 255
        if remaining_blocks_count != 0:
            yield 255 >> (8 - remaining_blocks_count)
        free_blocks = (blocks_per_group - first_data_bn) // 8
        for b in range(free_blocks):
            yield 0

    gbn = fs.gpn_to_bn(group_number,
                       fs.bytes_to_int(superblock.get_field(superblock.s_blocks_per_group)))
    bitmap_bytes_count = math.ceil(fs.bytes_to_int(superblock.get_field(superblock.s_blocks_per_group)) / 8)
    gdtable_block = gdtable.get_gdtableblock(group_number)
    bitmap_bn = fs.bytes_to_int(gdtable_block.get_field(group_number, gdtable_block.bg_block_bitmap))

    blockbitmap.block_bitmap.load(bitmap_bn)
    blockbitmap.block_bitmap.block_buffer[:bitmap_bytes_count] = bytes(
        fillbitmap(fs.bytes_to_int(superblock.get_field(superblock.s_first_data_block)) + 1 if group_number == 0
                   else fs.bytes_to_int(superblock.get_field(superblock.s_first_data_block)),
                   fs.bytes_to_int(superblock.get_field(superblock.s_blocks_per_group)))
    )
    blockbitmap.block_bitmap.unload(bitmap_bn)


def create_inode_bitmap(group_number):
    bitmap_bytes_count = math.ceil(fs.bytes_to_int(superblock.get_field(superblock.s_inodes_per_group)) / 8)
    gdtable_block = gdtable.get_gdtableblock(group_number)
    bitmap_bn = fs.bytes_to_int(gdtable_block.get_field(group_number, gdtable_block.bg_inode_bitmap))

    inodebitmap.inode_bitmap.load(bitmap_bn)
    inodebitmap.inode_bitmap.block_buffer[:bitmap_bytes_count] = bytes(bitmap_bytes_count)

    if group_number == 0:
        inodebitmap.inode_bitmap.block_buffer[:1] = b'\x01'

    inodebitmap.inode_bitmap.unload(bitmap_bn)


def create_inode_table():
    first_data_block = fs.bytes_to_int(superblock.get_field(superblock.s_first_data_block))
    inodetable_block = inodetable.load_inode(0)
    table_number = inodetable.get_table_number(0)
    inodetable_block.set_field(table_number, inodetable_block.i_mode,
                               inodetable.S_IFDIR | inodetable.S_IXUSR | inodetable.S_IRUSR | inodetable.S_IWUSR)
    inodetable_block.set_field(table_number, inodetable_block.i_uid, 0)
    inodetable_block.set_field(table_number, inodetable_block.i_size, 0)
    inodetable_block.set_field(table_number, inodetable_block.i_atime, 0)
    inodetable_block.set_field(table_number, inodetable_block.i_mtime, 0)
    inodetable_block.set_field(table_number, inodetable_block.i_ctime, int(time.time()))
    inodetable_block.set_field(table_number, inodetable_block.i_dtime, 0)
    inodetable_block.set_field(table_number, inodetable_block.i_gid, 0)
    inodetable_block.set_field(table_number, inodetable_block.i_blocks, 1)
    inodetable_block.set_field(table_number, inodetable_block.i_flags, 0)
    block = bytearray(inodetable_block.i_block[sysblock.SIZE_INDEX])
    block[:superblock.s_first_data_block[sysblock.SIZE_INDEX]] = \
        first_data_block.to_bytes(superblock.s_first_data_block[sysblock.SIZE_INDEX], 'little')
    inodetable_block.set_field(table_number, inodetable_block.i_block, bytes(block))
    inodetable_block.set_field(table_number, inodetable_block.i_pad, bytes(
        inodetable_block.i_pad[sysblock.SIZE_INDEX]))
    inodetable.unload_inode(0)


def exec_mkfs(args):
    if args.partition_size != partman.get_parition_size(args.partition_name):
        raise partman.InvalidPartitionSizeError('Wrong filesystem size for this partition')

    device.init_device(512)
    balloc.init_balloc(args.block_size)
    device.vdevice.bound_partition(args.partition_name)
    uuid_value = uuid.uuid4().bytes
    create_superblock(0, uuid_value, **vars(args))
    gdtable.init_gdtable(fs.get_groups_count(get_blocks_count(args.partition_size, args.block_size),
                         args.blocks_per_group))
    create_gdtable(0)
    create_block_bitmap(0)
    create_inode_bitmap(0)
    create_inode_table()

    for i in range(1, fs.get_groups_count(get_blocks_count(args.partition_size, args.block_size),
                   args.blocks_per_group)):
        create_superblock(i, uuid_value, **vars(args))
        create_gdtable(i)
        create_block_bitmap(i)
        create_inode_bitmap(i)
