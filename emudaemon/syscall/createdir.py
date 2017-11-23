__author__ = 'fuxy'

from emudaemon.syscall import createfile
from emudaemon.syscall import closefile
from fs import inodetable


def create_dir(path, mode):
    closefile.close_file(createfile.create_file_record(path, int(mode) | inodetable.S_IFDIR))
    return 0
