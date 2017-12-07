from emudaemon.syscall import openfile
from emudaemon.syscall import closefile
from emudaemon import fdtable
from emudaemon import user
from emudaemon import permissions
from fs import inodetable
from fs import fs


def chmod(path, mode):
    fd = openfile.create_file_descriptor(path, openfile.O_RDONLY, 0)
    ino = fdtable.get_inode(fd)
    inode_tn = inodetable.get_table_number(ino)
    inode_block = inodetable.load_inode(ino)
    i_mode = fs.bytes_to_int(inode_block.get_field(inode_tn, inode_block.i_mode))
    i_uid = fs.bytes_to_int(inode_block.get_field(inode_tn, inode_block.i_uid))

    try:
        if user.get_uid() != i_uid and user.get_uid() != 0:
            raise permissions.PermissionsError(i_mode)

        if i_mode & inodetable.S_IFREG == inodetable.S_IFREG:
            inode_block.set_field(inode_tn, inode_block.i_mode, inodetable.S_IFREG | int(mode))
        else:
            inode_block.set_field(inode_tn, inode_block.i_mode, inodetable.S_IFDIR | int(mode))
    finally:
        inodetable.unload_inode(ino)
        closefile.close_file(fd)
    return 0
