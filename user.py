from ipc import open_queue
from emudaemon.syscall import syscalls
from emudaemon.syscall.errors import ErrorMessage
from emudaemon.syscall.errors import MessageType

RETURN_ERROR = {
    ErrorMessage.DIR_NOT_FOUND: -1,
    ErrorMessage.FILE_ALREADY_EXISTS: -1,
    ErrorMessage.FILE_NOT_EXISTS: -1,
    ErrorMessage.WRONG_FILE_TYPE: -1
}


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
