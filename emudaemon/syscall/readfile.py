from fs import fs
from fs.superblock import superblock
from fs import inodetable
from emudaemon import fdtable
from fs.datablockbuffer import data_block_buffer
import base64
import time


class OffsetError(IndexError):
    pass


def read_by_offset(fd, nbytes):
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
    block_size = fs.bytes_to_int(superblock.get_field(superblock.s_log_block_size)) * 1024

    if offset >= file_size:
        raise OffsetError(offset)

    lbn = offset // block_size
    b_offset = offset % block_size

    buf = bytearray()
    if b_offset + nbytes > block_size:
        first_bytes_count = block_size - b_offset
        data_block_buffer.load(inodetable.lbn_to_bn(lbn, i_block))
        buf[:first_bytes_count] = data_block_buffer.get_bytes(b_offset, first_bytes_count)
        data_block_buffer.load(inodetable.lbn_to_bn(lbn + 1, i_block))
        buf[first_bytes_count: nbytes] = data_block_buffer.get_bytes(0, nbytes - first_bytes_count)
    else:
        data_block_buffer.load(inodetable.lbn_to_bn(lbn, i_block))
        buf[:] = data_block_buffer.get_bytes(b_offset, nbytes)

    fdtable.set_offset(fd, offset + nbytes)

    file_inodetable_block.set_field(inode_tn, file_inodetable_block.i_atime, int(time.time()))

    inodetable.unload_inode(inode)
    return bytes(buf)


def read(fd, nbytes):
    return base64.b64encode(read_by_offset(int(fd), int(nbytes))).decode(encoding='ASCII')
