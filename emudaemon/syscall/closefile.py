from emudaemon import fdtable
from fs import inodetable


def close_file(fd):
    inodetable.unload_inode(fdtable.get_inode(int(fd)))
    fdtable.release_fd(int(fd))
    return 0
