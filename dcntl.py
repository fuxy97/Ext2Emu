from ipc import syscall
from emudaemon.syscall import syscalls
from ast import literal_eval


def mkdir(path, mode):
    return syscall(path + ' ' + str(mode), syscalls.DirSysCall.CREATE.value, int)


def rmdir(path):
    return syscall(path, syscalls.DirSysCall.DELETE.value, int)


def opendir(path):
    return syscall(path, syscalls.DirSysCall.OPEN.value, int)


def closedir(fd):
    return syscall(str(fd), syscalls.DirSysCall.CLOSE.value, int)


def readdir(fd):
    return syscall(str(fd), syscalls.DirSysCall.READ.value, literal_eval)
