from emudaemon import daemon
from fs import fs
from fs import superblock
from fs import gdtable
import sysv_ipc
import ipc
import os
from emudaemon.syscall.syscalls import FileSysCall
from emudaemon.syscall.syscalls import DirSysCall
from emudaemon.syscall.syscalls import UserSysCall
from emudaemon.syscall.errors import MessageType
from emudaemon.syscall.errors import ErrorMessage
from emudaemon.syscall import createfile
from emudaemon.syscall import openfile
from emudaemon.syscall import createdir
from emudaemon.syscall import deletefile
from emudaemon.syscall import deletedir
from emudaemon.syscall import closefile
from emudaemon.syscall import append
from emudaemon import user

SYSCALLS = {FileSysCall.OPEN: openfile.open_file,
            FileSysCall.CLOSE: closefile.close_file,
            FileSysCall.CREATE: createfile.create_file,
            DirSysCall.CREATE: createdir.create_dir,
            FileSysCall.DELETE: deletefile.delete_file,
            DirSysCall.DELETE: deletedir.delete_dir,
            FileSysCall.APPEND: append.append,
            UserSysCall.AUTH: user.auth,
            UserSysCall.EXIT: user.unauth}


class EmulatorDaemon(daemon.Daemon):
    def __init__(self, pidfile, keyfile, partition_name, stdout=os.devnull):
        super().__init__(pidfile, stdout=stdout)
        self.partition_name = partition_name
        self.superblock = superblock.superblock
        self.keyfile = keyfile
        self.mq = None
        self.trace_file = None

    def load_bg_table(self):
        gdtable.init_gdtable(fs.get_groups_count(
            fs.bytes_to_int(self.superblock.get_field(self.superblock.s_blocks_count)),
            fs.bytes_to_int(self.superblock.get_field(self.superblock.s_blocks_per_group))
        ))
        gdtable.load_gdtable(0)

    def run(self):
        superblock.load_superblock(self.partition_name)
        self.load_bg_table()

        key = ipc.get_ipc_key(self.superblock)
        with open(self.keyfile, 'w+') as f:
            f.write('%d\n' % key)

        self.mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)

        while True:
            msg_buf, msg_type = self.mq.receive()
            self.handle_message(msg_buf, msg_type)

    def handle_message(self, msg_buf, msg_type):
        params = msg_buf.decode(encoding='ASCII').split()
        try:
            if msg_type < len(FileSysCall) + 1:
                self.mq.send(str(SYSCALLS[FileSysCall(msg_type)](*params)).encode(encoding='ASCII'),
                             type=MessageType.RESULT_MESSAGE.value)
            elif msg_type < len(FileSysCall) + len(DirSysCall) + 1:
                self.mq.send(str(SYSCALLS[DirSysCall(msg_type)](*params)).encode(encoding='ASCII'),
                             type=MessageType.RESULT_MESSAGE.value)
            else:
                self.mq.send(str(SYSCALLS[UserSysCall(msg_type)](*params)).encode(encoding='ASCII'),
                             type=MessageType.RESULT_MESSAGE.value)
        except createfile.DirNotFoundError:
            self.mq.send(ErrorMessage.DIR_NOT_FOUND.value.encode(encoding='ASCII'),
                         type=MessageType.ERROR_MESSAGE.value)
        except createfile.FileAlreadyExistsError:
            self.mq.send(ErrorMessage.FILE_ALREADY_EXISTS.value.encode(encoding='ASCII'),
                         type=MessageType.ERROR_MESSAGE.value)
        except deletefile.FileNotExistsError:
            self.mq.send(ErrorMessage.FILE_NOT_EXISTS.value.encode(encoding='ASCII'),
                         type=MessageType.ERROR_MESSAGE.value)
        except deletefile.WrongFileTypeError:
            self.mq.send(ErrorMessage.WRONG_FILE_TYPE.value.encode(encoding='ASCII'),
                         type=MessageType.ERROR_MESSAGE.value)

    def finalize(self):
        self.mq.remove()
        os.remove(self.keyfile)
        self.trace_file.close()
        superblock.superblock.unload(0)
        gdtable.unload_gdtable(0)

