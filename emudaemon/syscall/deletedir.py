__author__ = 'fuxy'

from emudaemon.syscall import deletefile
from fs import inodetable
from emudaemon import user


def delete_dir(path):
    if not user.is_user_authenticated():
        raise user.NoAuthUserError()

    deletefile.delete_file_record(path, inodetable.S_IFDIR)
    return 0

