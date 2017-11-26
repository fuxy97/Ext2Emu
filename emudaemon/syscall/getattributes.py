from emudaemon.syscall import openfile
from emudaemon.syscall import closefile
from emudaemon import fdtable
from fs import inodetable
from fs import fs


def stat(path):
    fd = openfile.create_file_descriptor(path, openfile.O_RDONLY, 0)
    ino = fdtable.get_inode(fd)
    inode_tn = inodetable.get_table_number(ino)

    inode_block = inodetable.load_inode(ino)
    mode = fs.bytes_to_int(inode_block.get_field(inode_tn, inode_block.i_mode))
    uid = fs.bytes_to_int(inode_block.get_field(inode_tn, inode_block.i_uid))
    gid = fs.bytes_to_int(inode_block.get_field(inode_tn, inode_block.i_gid))
    size = fs.bytes_to_int(inode_block.get_field(inode_tn, inode_block.i_size))
    atime = fs.bytes_to_int(inode_block.get_field(inode_tn, inode_block.i_atime))
    mtime = fs.bytes_to_int(inode_block.get_field(inode_tn, inode_block.i_mtime))
    ctime = fs.bytes_to_int(inode_block.get_field(inode_tn, inode_block.i_ctime))
    blocks = fs.bytes_to_int(inode_block.get_field(inode_tn, inode_block.i_blocks))
    inodetable.unload_inode(ino)

    closefile.close_file(fd)

    return ino, mode, uid, gid, size, atime, mtime, ctime, blocks
