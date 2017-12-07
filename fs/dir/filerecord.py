from fs import fs
from fs.datablockbuffer import data_block_buffer
from fs import sysblock
from fs import blockbitmap
from fs import inodetable
from fs import gdtable
import time


IN_FIELD_SIZE = 4
RL_FIELD_SIZE = 2
NL_FIELD_SIZE = 1


def create_file_record(inode_block, inode_table_number, file_inode_number, filename):
    file_size = fs.bytes_to_int(inode_block.get_field(inode_table_number, inode_block.i_size))

    if file_size == 0:
        inode_block.set_field(
            inode_table_number, inode_block.i_size,
            IN_FIELD_SIZE + RL_FIELD_SIZE + NL_FIELD_SIZE + len(filename)
        )
        if fs.bytes_to_int(inode_block.get_field(inode_table_number, inode_block.i_blocks)) == 0:
            inode_block.set_field(inode_table_number, inode_block.i_blocks, 1)
            gn = inodetable.get_group_number(inode_block.first_inode_number)
            bg_block = gdtable.get_gdtableblock(gn)
            blockbitmap.block_bitmap.load(fs.bytes_to_int(bg_block.get_field(gn, bg_block.bg_block_bitmap)))
            free_bn = blockbitmap.find_first_free_block()
            blockbitmap.set_used_block(free_bn)
            inode_block.set_field(
                inode_table_number, inode_block.i_block,
                fs.int_to_bytes(free_bn, inode_block.i_block[sysblock.SIZE_INDEX])
            )
            blockbitmap.block_bitmap.unload(fs.bytes_to_int(bg_block.get_field(gn, bg_block.bg_block_bitmap)))
            inode_block.set_field(inode_table_number, inode_block.i_ctime, int(time.time()))
        bn = fs.bytes_to_int(inode_block.get_field(inode_table_number, inode_block.i_block)[:fs.ADDRESS_SIZE])
        data_block_buffer.load(bn)
        create_file_record_in_block(0, file_inode_number, filename)
        inode_block.set_field(inode_table_number, inode_block.i_mtime, int(time.time()))
        data_block_buffer.unload(bn)
        return None

    blocks_count = fs.bytes_to_int(inode_block.get_field(inode_table_number, inode_block.i_blocks))
    i_block = inode_block.get_field(inode_table_number, inode_block.i_block)

    bn, offset = 0, 0
    filename_encoded = filename.encode(encoding='ASCII')
    for lbn in range(blocks_count):
        bn = inodetable.lbn_to_bn(lbn, i_block)
        data_block_buffer.load(bn)

        if lbn == blocks_count - 1:
            rlength, offset = find_first_free_record_in_block(file_size)
            while rlength and len(filename_encoded) > rlength - IN_FIELD_SIZE - NL_FIELD_SIZE - RL_FIELD_SIZE:
                    rlength, offset = find_first_free_record_in_block(file_size, offset + rlength)
        else:
            rlength, offset = find_first_free_record_in_block()
            while rlength and len(filename_encoded) > rlength - IN_FIELD_SIZE - NL_FIELD_SIZE - RL_FIELD_SIZE:
                    rlength, offset = find_first_free_record_in_block(offset + rlength)
        if offset:
            break

    if not rlength:
        extend_dir_file(inode_block, inode_table_number,
                        IN_FIELD_SIZE + RL_FIELD_SIZE + NL_FIELD_SIZE + len(filename_encoded))
        create_file_record_in_block(file_size, file_inode_number, filename)
    else:
        create_file_record_in_block(offset, file_inode_number, filename)
    inode_block.set_field(inode_table_number, inode_block.i_mtime, int(time.time()))
    data_block_buffer.unload(bn)


def extend_dir_file(inode_block, inode_table_number, rlength):
    file_size = fs.bytes_to_int(inode_block.get_field(inode_table_number, inode_block.i_size))
    inode_block.set_field(inode_table_number, inode_block.i_size, file_size + rlength)
    inode_block.set_field(inode_table_number, inode_block.i_ctime, int(time.time()))


def create_file_record_in_block(offset, inode_number, filename):
    data_block_buffer.set_bytes(offset, fs.int_to_bytes(inode_number, IN_FIELD_SIZE))
    filename_encoded = filename.encode(encoding='ASCII')
    data_block_buffer.set_bytes(
        offset + IN_FIELD_SIZE,
        fs.int_to_bytes(len(filename_encoded) + IN_FIELD_SIZE + RL_FIELD_SIZE + NL_FIELD_SIZE,
                        RL_FIELD_SIZE)
    )
    data_block_buffer.set_bytes(
        offset + IN_FIELD_SIZE + RL_FIELD_SIZE,
        fs.int_to_bytes(len(filename_encoded), NL_FIELD_SIZE)
    )
    data_block_buffer.set_bytes(offset + IN_FIELD_SIZE + RL_FIELD_SIZE + NL_FIELD_SIZE, filename_encoded)


def find_first_free_record_in_block(file_size=None, offset=0):
    rlength = None
    length = file_size % data_block_buffer.block_size if file_size else data_block_buffer.block_size
    while offset < length:
        inode = fs.bytes_to_int(data_block_buffer.get_bytes(offset, IN_FIELD_SIZE))
        rlength = fs.bytes_to_int(data_block_buffer.get_bytes(offset + IN_FIELD_SIZE, RL_FIELD_SIZE))

        if inode == 0:
            return rlength, offset

        offset += rlength

    if rlength is not None:
        return None, offset - rlength
    else:
        return None, 0


def find_file_record(inode_block, inode_table_number, filename):
    file_size = fs.bytes_to_int(inode_block.get_field(inode_table_number, inode_block.i_size))

    if file_size == 0:
        return

    blocks_count = fs.bytes_to_int(inode_block.get_field(inode_table_number, inode_block.i_blocks))
    i_block = inode_block.get_field(inode_table_number, inode_block.i_block)

    offset = 0
    for lbn in range(blocks_count):
        bn = inodetable.lbn_to_bn(lbn, i_block)
        data_block_buffer.load(bn)

        if lbn == blocks_count - 1:
            offset = find_record_in_block(filename, file_size)
        else:
            offset = find_record_in_block(filename)
        if offset:
            break

    return offset


def find_record_in_block(filename, file_size=None):
    offset = 0
    length = file_size % data_block_buffer.block_size if file_size else data_block_buffer.block_size
    while offset < length:
        rlength = fs.bytes_to_int(data_block_buffer.get_bytes(offset + IN_FIELD_SIZE, RL_FIELD_SIZE))
        nlength = fs.bytes_to_int(data_block_buffer.get_bytes(offset + IN_FIELD_SIZE + RL_FIELD_SIZE, NL_FIELD_SIZE))
        rname = data_block_buffer.get_bytes(offset + IN_FIELD_SIZE + RL_FIELD_SIZE + NL_FIELD_SIZE, nlength)
        inode = fs.bytes_to_int(data_block_buffer.get_bytes(offset, IN_FIELD_SIZE))

        if filename == rname.decode(encoding='ASCII') and inode != 0:
            return offset
        else:
            offset += rlength


def remove_file_record(offset):
    inode = get_record_inode_number(offset)
    inode_table_block = inodetable.load_inode(inode)
    inode_tn = inodetable.get_table_number(inode)
    i_block = inode_table_block.get_field(inode_tn, inode_table_block.i_block)
    inodetable.free_file_blocks(inode_table_block, inode, i_block)

    data_block_buffer.set_bytes(offset, fs.int_to_bytes(0, IN_FIELD_SIZE))


def get_record_inode_number(offset):
    return fs.bytes_to_int(data_block_buffer.get_bytes(offset, IN_FIELD_SIZE))
