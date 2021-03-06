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
from emudaemon.syscall import readfile
from emudaemon.syscall import writefile
from emudaemon.syscall import opendir
from emudaemon.syscall import closedir
from emudaemon.syscall import readdir
from emudaemon.syscall import getattributes
from emudaemon.syscall import setattributes
from emudaemon.syscall import seekfile
from emudaemon import permissions
from emudaemon import user
from getpass import getpass

SYSCALLS = {FileSysCall.OPEN: openfile.open_file,
            FileSysCall.CLOSE: closefile.close_file,
            FileSysCall.CREATE: createfile.create_file,
            DirSysCall.CREATE: createdir.create_dir,
            FileSysCall.DELETE: deletefile.delete_file,
            DirSysCall.DELETE: deletedir.delete_dir,
            FileSysCall.APPEND: append.append,
            UserSysCall.AUTH: user.auth,
            UserSysCall.EXIT: user.unauth,
            FileSysCall.READ: readfile.read,
            FileSysCall.WRITE: writefile.write,
            DirSysCall.OPEN: opendir.opendir,
            DirSysCall.CLOSE: closedir.closedir,
            DirSysCall.READ: readdir.readdir,
            FileSysCall.GET_ATTRIBUTES: getattributes.stat,
            FileSysCall.SEEK: seekfile.seek,
            FileSysCall.SET_ATTRIBUTES: setattributes.chmod}


class EmulatorDaemon(daemon.Daemon):
    def __init__(self, pidfile, keyfile, partition_name, stdout=os.devnull):
        super().__init__(pidfile, stdout=stdout)
        self.partition_name = partition_name
        self.superblock = superblock.superblock
        self.keyfile = keyfile
        self.mq = None
        self.trace_file = None
        self.snd_sem = None
        self.rcv_sem = None

    def load_bg_table(self):
        gdtable.init_gdtable(fs.get_groups_count(
            fs.bytes_to_int(self.superblock.get_field(self.superblock.s_blocks_count)),
            fs.bytes_to_int(self.superblock.get_field(self.superblock.s_blocks_per_group))
        ))
        gdtable.load_gdtable(0)

    def init_daemon(self):
        superblock.load_superblock(self.partition_name)
        self.load_bg_table()
        try:
            print('[ext2emud] password for root:')
            rpass = getpass('Enter new root password: ')
            rpass_re = getpass('Retype new root password: ')
            while rpass != rpass_re:
                print('You typed password incorrectly. Type again:')
                rpass = getpass('Enter new root password: ')
                rpass_re = getpass('Retype new root password: ')

            user.create_passwd(rpass)
        except createfile.FileAlreadyExistsError:
            print("'/etc/passwd' already exists.")
        finally:
            superblock.superblock.unload(0)
            gdtable.unload_gdtable(0)

    def run(self):
        superblock.load_superblock(self.partition_name)
        self.load_bg_table()

        key = ipc.get_ipc_key(self.superblock)
        with open(self.keyfile, 'w+') as f:
            f.write('%d\n' % key)

        self.snd_sem = sysv_ipc.Semaphore(key, sysv_ipc.IPC_CREAT)
        self.rcv_sem = sysv_ipc.Semaphore(key + 1, sysv_ipc.IPC_CREAT)
        self.mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)

        while True:
            self.snd_sem.acquire()
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
        except readfile.OffsetError:
            self.mq.send(ErrorMessage.WRONG_OFFSET.value.encode(encoding='ASCII'),
                         type=MessageType.ERROR_MESSAGE.value)
        except user.NoAuthUserError:
            self.mq.send(ErrorMessage.NO_USER_IN_SYSTEM.value.encode(encoding='ASCII'),
                         type=MessageType.ERROR_MESSAGE.value)
        except user.AuthError:
            self.mq.send(ErrorMessage.USER_ALREADY_IN_SYSTEM.value.encode(encoding='ASCII'),
                         type=MessageType.ERROR_MESSAGE.value)
        except permissions.PermissionsError:
            self.mq.send(ErrorMessage.NO_PERMISSIONS.value.encode(encoding='ASCII'),
                         type=MessageType.ERROR_MESSAGE.value)
        except deletefile.DirIsNotEmpty:
            self.mq.send(ErrorMessage.DIR_IS_NOT_EMPTY.value.encode(encoding='ASCII'),
                         type=MessageType.ERROR_MESSAGE.value)
        self.rcv_sem.release()

    def finalize(self):
        self.mq.remove()
        self.snd_sem.remove()
        self.rcv_sem.remove()
        os.remove(self.keyfile)
        self.trace_file.close()
        superblock.superblock.unload(0)
        gdtable.unload_gdtable(0)
