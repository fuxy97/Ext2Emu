from fs import fs
from fs.superblock import superblock
from fs import inodetable
from emudaemon import fdtable
from fs.datablockbuffer import data_block_buffer
import base64
import time


def write_by_offset(fd, buf, nbytes):
    inode = fdtable.get_inode(fd)
    offset = fdtable.get_offset(fd)
    inode_tn = inodetable.get_table_number(inode)
    file_inodetable_block = inodetable.load_inode(inode)
    i_block = file_inodetable_block.get_field(
        inode_tn,
        file_inodetable_block.i_block
    )
    file_size = fs.bytes_to_int(file_inodetable_block.get_field(
        inode_tn,
        file_inodetable_block.i_size
    ))
    blocks_count = fs.bytes_to_int(file_inodetable_block.get_field(
        inode_tn,
        file_inodetable_block.i_blocks
    ))
    block_size = fs.bytes_to_int(superblock.get_field(superblock.s_log_block_size)) * 1024

    lbn = offset // block_size
    b_offset = offset % block_size

    if offset + nbytes > file_size:
        if b_offset + nbytes > block_size or lbn == blocks_count:
            inodetable.extend_file_blocks(file_inodetable_block, inode, i_block)
        file_inodetable_block.set_field(inode_tn, file_inodetable_block.i_size, offset + nbytes)

    bn = inodetable.lbn_to_bn(lbn, i_block)
    data_block_buffer.load(bn)
    if b_offset + nbytes > block_size:
        first_bytes_count = block_size - b_offset
        if first_bytes_count != 0:
            data_block_buffer.set_bytes(b_offset, buf[:first_bytes_count])
            data_block_buffer.unload(bn)
        bn = inodetable.lbn_to_bn(lbn + 1, i_block)
        data_block_buffer.load(bn)
        data_block_buffer.set_bytes(0, buf[first_bytes_count: nbytes])
    else:
        data_block_buffer.set_bytes(b_offset, buf)
    data_block_buffer.unload(bn)

    fdtable.set_offset(fd, offset + nbytes)

    file_inodetable_block.set_field(inode_tn, file_inodetable_block.i_mtime, int(time.time()))

    inodetable.unload_inode(inode)


def write(fd, buf, nbytes):
    write_by_offset(int(fd), base64.b64decode(buf.encode(encoding='ASCII')), int(nbytes))
    return 0
