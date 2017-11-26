from fs import fs
import sysv_ipc
from emudaemon.syscall.errors import ErrorMessage
from emudaemon.syscall.errors import MessageType

IPC_KEY_SIZE = 4


def open_queue_semaphore():
    with open('ext2emud.key', 'r') as f:
        key = int(f.read())
    return sysv_ipc.MessageQueue(key), sysv_ipc.Semaphore(key), sysv_ipc.Semaphore(key + 1)


def get_ipc_key(superblock):
    s_uuid = superblock.get_field(superblock.s_uuid)

    key = 0
    for i in range(len(s_uuid) // IPC_KEY_SIZE):
        key ^= fs.bytes_to_int(s_uuid[i * IPC_KEY_SIZE: (i+1) * IPC_KEY_SIZE])
    return key


RETURN_ERROR = {
    ErrorMessage.DIR_NOT_FOUND: -1,
    ErrorMessage.FILE_ALREADY_EXISTS: -1,
    ErrorMessage.FILE_NOT_EXISTS: -1,
    ErrorMessage.WRONG_FILE_TYPE: -1,
    ErrorMessage.WRONG_OFFSET: -1,
    ErrorMessage.NO_USER_IN_SYSTEM: -1,
    ErrorMessage.USER_ALREADY_IN_SYSTEM: -1
}


def syscall(mq_msg, mq_msg_type, return_type):
    mq, snd_sem, rcv_sem = open_queue_semaphore()
    mq.send(mq_msg.encode(encoding='ASCII'), type=mq_msg_type)
    snd_sem.release()
    rcv_sem.acquire()
    msg_buf, msg_type = mq.receive()
    if msg_type == MessageType.ERROR_MESSAGE.value:
        return RETURN_ERROR[ErrorMessage(msg_buf.decode(encoding='ASCII'))]

    return return_type(msg_buf.decode(encoding='ASCII'))
