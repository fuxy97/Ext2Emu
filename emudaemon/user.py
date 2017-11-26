from emudaemon.syscall import openfile
from emudaemon.syscall import readfile
from emudaemon import fdtable
from fs import inodetable
from fs import fs
from emudaemon.syscall import createdir
from emudaemon.syscall import createfile
from emudaemon.syscall import writefile
from emudaemon.syscall import closefile
import hashlib


class AuthError(Exception):
    pass


class NoAuthUserError(Exception):
    pass


def build_user():
    uid, gid = -1, -1

    def create_passwd(root_pass):
        nonlocal uid, gid
        uid, gid = 0, 0

        try:
            createdir.create_dir('/etc', inodetable.S_IXUSR | inodetable.S_IWUSR | inodetable.S_IRUSR
                                 | inodetable.S_IROTH | inodetable.S_IRGRP | inodetable.S_IXOTH
                                 | inodetable.S_IXGRP)
        except createfile.FileAlreadyExistsError:
            pass
        finally:
            try:
                fd = createfile.create_file('/etc/passwd', inodetable.S_IRUSR | inodetable.S_IWUSR |
                                            inodetable.S_IRGRP | inodetable.S_IROTH)
                writefile.write_by_offset(fd, ('root:' + hashlib.sha224(root_pass.encode()).hexdigest()
                                          + ':0:0:\n').encode(encoding='ASCII'), 67)
                closefile.close_file(fd)

                fd = createfile.create_file('/etc/group', inodetable.S_IRUSR | inodetable.S_IWUSR |
                                            inodetable.S_IRGRP | inodetable.S_IROTH)
                writefile.write_by_offset(fd, 'root:0:\n'.encode(encoding='ASCII'), 8)
                closefile.close_file(fd)
            finally:
                uid, gid = -1, -1

    def auth(user, passwd):
        nonlocal uid, gid
        if uid != -1:
            raise AuthError

        uid, gid = 0, 0
        fd = openfile.open_file('/etc/passwd', openfile.O_RDONLY)

        inode = fdtable.get_inode(fd)
        inode_tn = inodetable.get_table_number(inode)
        file_inodetable_block = inodetable.load_inode(inode)
        file_size = fs.bytes_to_int(file_inodetable_block.get_field(inode_tn, file_inodetable_block.i_size))

        lines = readfile.read_by_offset(fd, file_size).decode(encoding='ASCII').splitlines()
        closefile.close_file(fd)
        uid, gid = -1, -1

        digest = hashlib.sha224(passwd.encode()).hexdigest()
        for l in lines:
            if l.lstrip()[0] != '#':
                u = tuple(l.split(':'))
                if u[0] == user:
                    if u[1] == digest and u[4] != 'nologin':
                        uid = int(u[2])
                        gid = int(u[3])

        if uid == -1:
            raise AuthError

        return uid

    def unauth():
        nonlocal uid, gid
        uid, gid = -1, -1
        fdtable.release_fd_table()
        return 0

    def get_uid():
        return uid

    def get_gid():
        return gid

    def is_user_authenticated():
        return uid != -1

    return auth, unauth, get_uid, get_gid, is_user_authenticated, create_passwd


auth, unauth, get_uid, get_gid, is_user_authenticated, create_passwd = build_user()
