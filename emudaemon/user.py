from emudaemon.syscall import openfile
from emudaemon.syscall import readfile
from emudaemon import fdtable
from fs import inodetable
from fs import fs
import hashlib


class AuthError(Exception):
    pass


def build_user():
    uid = -1

    def auth(user, passwd):
        nonlocal uid
        if uid != -1:
            raise AuthError

        fd = openfile.open_file('/etc/passwd', 0)

        inode = fdtable.get_inode(fd)
        inode_tn = inodetable.get_table_number(inode)
        file_inodetable_block = inodetable.load_inode(inode)
        file_size = fs.bytes_to_int(file_inodetable_block.get_field(inode_tn, file_inodetable_block.i_size))

        digest = hashlib.sha224(passwd.encode()).hexdigest()
        for l in readfile.read_by_offset(fd, file_size).decode(encoding='ASCII').splitlines():
            if l.lstrip()[0] != '#':
                u = tuple(l.split(':'))
                if u[0] == user:
                    if u[1] == digest and u[4] != 'nologin':
                        uid = int(u[2])

        if uid == -1:
            raise AuthError

        return uid

    def unauth():
        nonlocal uid
        uid = -1
        return 0

    def get_uid():
        return uid

    return auth, unauth, get_uid


auth, unauth, get_uid = build_user()
