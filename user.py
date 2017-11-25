from ipc import syscall
from emudaemon.syscall import syscalls


def login(user, passwd):
    return syscall(user + ' ' + passwd, syscalls.UserSysCall.AUTH.value, int)


def exit():
    return syscall('', syscalls.UserSysCall.EXIT.value, int)
