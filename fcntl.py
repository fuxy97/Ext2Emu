from emudaemon.syscall import syscalls
from emudaemon.syscall import openfile
from ipc import syscall
import base64


class UnsupportedOFlagError(ValueError):
    pass


def creat(path, mode):
    return syscall(path + ' ' + str(mode), syscalls.FileSysCall.CREATE.value, int)


def mkdir(path, mode):
    return syscall(path + ' ' + str(mode), syscalls.DirSysCall.CREATE.value, int)


def open(path, oflag=0, mode=0):
    if oflag != openfile.O_CREAT | openfile.O_EXCL and oflag != openfile.O_RDONLY and \
       oflag != openfile.O_RDWR and oflag != openfile.O_WRONLY:
        raise UnsupportedOFlagError('oflag value: ' + str(oflag))

    return syscall(path + ' ' + str(oflag) + ' ' + str(mode), syscalls.FileSysCall.OPEN.value, int)


def close(fd):
    return syscall(str(fd), syscalls.FileSysCall.CLOSE.value, int)


def unlink(path):
    return syscall(path, syscalls.FileSysCall.DELETE.value, int)


def rmdir(path):
    return syscall(path, syscalls.DirSysCall.DELETE.value, int)


def append(fd, buf, nbytes):
    return syscall(str(fd) + ' ' + buf.decode(encoding='ASCII') + ' ' + str(nbytes),
                   syscalls.FileSysCall.APPEND.value, int)


def read(fd, nbytes):
    return syscall(str(fd) + ' ' + str(nbytes), syscalls.FileSysCall.READ.value, base64.b64decode)


def write(fd, buf, nbytes):
    return syscall((str(fd) + ' ' + base64.b64encode(buf).decode(encoding='ASCII') + ' ' + str(nbytes)),
                   syscalls.FileSysCall.WRITE.value, int)

