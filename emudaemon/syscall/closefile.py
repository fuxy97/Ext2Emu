from emudaemon import fdtable
from fs import inodetable
from emudaemon import user


def close_file(fd):
    if not user.is_user_authenticated():
        raise user.NoAuthUserError()

    inodetable.unload_inode(fdtable.get_inode(int(fd)))
    fdtable.release_fd(int(fd))
    return 0
