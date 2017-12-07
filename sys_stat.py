from ipc import syscall
from emudaemon.syscall import syscalls
from ast import literal_eval
from fs import inodetable


def is_dir(mode):
    return bool(mode & inodetable.S_IFDIR)


def is_reg_file(mode):
    return bool(mode & inodetable.S_IFREG)


def stat(path):
    return syscall(path, syscalls.FileSysCall.GET_ATTRIBUTES.value, literal_eval)


def chmod(path, mode):
    return syscall(path + ' ' + str(mode), syscalls.FileSysCall.SET_ATTRIBUTES.value, int)
