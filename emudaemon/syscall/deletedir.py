__author__ = 'fuxy'

from emudaemon.syscall import deletefile
from fs import inodetable


def delete_dir(path):
    deletefile.delete_file_record(path, inodetable.S_IFDIR)
    return 0

