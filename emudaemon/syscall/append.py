from fs import fs
from fs.superblock import superblock
from fs import inodetable
from emudaemon import fdtable
from fs.datablockbuffer import data_block_buffer


def write_to_end(fd, buf, nbytes):
    inode = fdtable.get_inode(fd)
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

    last_block_size = file_size % block_size
    if last_block_size == 0:
        last_bn = inodetable.extend_file_blocks(file_inodetable_block, inode, i_block)
    else:
        last_bn = inodetable.get_last_file_bn(i_block)

    data_block_buffer.load(last_bn)
    if last_block_size + nbytes > block_size:
        last_bn = inodetable.extend_file_blocks(file_inodetable_block, inode, i_block)
        remaining_bytes_count = block_size - last_block_size
        data_block_buffer.set_bytes(last_block_size, buf[:remaining_bytes_count])
        data_block_buffer.unload(data_block_buffer.block_number)
        data_block_buffer.load(last_bn)
        data_block_buffer.set_bytes(0, buf[remaining_bytes_count:nbytes])
    else:
        print(last_block_size)
        data_block_buffer.set_bytes(last_block_size, buf[:nbytes])

    file_inodetable_block.set_field(
        inode_tn,
        file_inodetable_block.i_size,
        file_size + nbytes
    )
    data_block_buffer.unload(last_bn)
    inodetable.unload_inode(inode)


def append(fd, buf, nbytes):
    write_to_end(int(fd), buf.encode(encoding='ASCII'), int(nbytes))
    return 0


