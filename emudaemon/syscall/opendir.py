from emudaemon.syscall import openfile
from fs import inodetable
from emudaemon import user


def opendir(path):
    if not user.is_user_authenticated():
        raise user.NoAuthUserError()

    return openfile.create_file_descriptor(path, openfile.O_RDONLY, inodetable.S_IFDIR)
