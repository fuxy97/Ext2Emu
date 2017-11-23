from emudaemon.syscall import syscalls
from emudaemon.syscall.errors import MessageType
from emudaemon.syscall.errors import ErrorMessage
from emudaemon.syscall import openfile
from fs import inodetable
import sysv_ipc
import builtins
import hashlib


class UnsupportedOFlagError(ValueError):
    pass


def open_queue():
    with builtins.open('ext2emud.key', 'r') as f:
        key = int(f.read())
    return sysv_ipc.MessageQueue(key)


RETURN_ERROR = {
    ErrorMessage.DIR_NOT_FOUND: -1,
    ErrorMessage.FILE_ALREADY_EXISTS: -1,
    ErrorMessage.FILE_NOT_EXISTS: -1,
    ErrorMessage.WRONG_FILE_TYPE: -1
}


def creat(path, mode):
    mq = open_queue()
    mq.send((path + ' ' + str(mode)).encode(encoding='ASCII'), type=syscalls.FileSysCall.CREATE.value)
    msg_buf, msg_type = mq.receive()
    if msg_type == MessageType.ERROR_MESSAGE.value:
        return RETURN_ERROR[ErrorMessage(msg_buf.decode(encoding='ASCII'))]

    return int(msg_buf)


def mkdir(path, mode):
    mq = open_queue()
    mq.send((path + ' ' + str(mode)).encode(encoding='ASCII'), type=syscalls.DirSysCall.CREATE.value)
    msg_buf, msg_type = mq.receive()
    if msg_type == MessageType.ERROR_MESSAGE.value:
        return RETURN_ERROR[ErrorMessage(msg_buf.decode(encoding='ASCII'))]

    return int(msg_buf)


def open(path, oflag=0, mode=0):
    if oflag != openfile.O_CREAT | openfile.O_EXCL and oflag != 0:
        raise UnsupportedOFlagError('oflag value: ' + str(oflag))

    mq = open_queue()
    mq.send((path + ' ' + str(oflag) + ' ' + str(mode)).encode(encoding='ASCII'),
            type=syscalls.FileSysCall.OPEN.value)
    msg_buf, msg_type = mq.receive()
    if msg_type == MessageType.ERROR_MESSAGE.value:
        return RETURN_ERROR[ErrorMessage(msg_buf.decode(encoding='ASCII'))]

    return int(msg_buf)


def close(fd):
    mq = open_queue()
    mq.send(str(fd), type=syscalls.FileSysCall.CLOSE.value)
    msg_buf, msg_type = mq.receive()
    if msg_type == MessageType.ERROR_MESSAGE.value:
        return RETURN_ERROR[ErrorMessage(msg_buf.decode(encoding='ASCII'))]

    return int(msg_buf)


def unlink(path):
    mq = open_queue()
    mq.send(path.encode(encoding='ASCII'), type=syscalls.FileSysCall.DELETE.value)
    msg_buf, msg_type = mq.receive()
    if msg_type == MessageType.ERROR_MESSAGE.value:
        return RETURN_ERROR[ErrorMessage(msg_buf.decode(encoding='ASCII'))]

    return int(msg_buf)


def rmdir(path):
    mq = open_queue()
    mq.send(path.encode(encoding='ASCII'), type=syscalls.DirSysCall.DELETE.value)
    msg_buf, msg_type = mq.receive()
    if msg_type == MessageType.ERROR_MESSAGE.value:
        return RETURN_ERROR[ErrorMessage(msg_buf.decode(encoding='ASCII'))]

    return int(msg_buf)


def append(fd, buf, nbytes):
    mq = open_queue()
    mq.send(str(fd) + ' ' + buf.decode(encoding='ASCII') + ' ' + str(nbytes),
            type=syscalls.FileSysCall.APPEND.value)
    msg_buf, msg_type = mq.receive()
    if msg_type == MessageType.ERROR_MESSAGE.value:
        return RETURN_ERROR[ErrorMessage(msg_buf.decode(encoding='ASCII'))]

    return int(msg_buf)


def login(user, passwd):
    mq = open_queue()
    mq.send(user + ' ' + passwd, type=syscalls.UserSysCall.AUTH.value)
    msg_buf, msg_type = mq.receive()
    if msg_type == MessageType.ERROR_MESSAGE.value:
        return RETURN_ERROR[ErrorMessage(msg_buf.decode(encoding='ASCII'))]

    return int(msg_buf)


def exit():
    mq = open_queue()
    mq.send('', type=syscalls.UserSysCall.EXIT.value)
    msg_buf, msg_type = mq.receive()
    if msg_type == MessageType.ERROR_MESSAGE.value:
        return RETURN_ERROR[ErrorMessage(msg_buf.decode(encoding='ASCII'))]

    return int(msg_buf)


if __name__ == '__main__':
    print(exit())
