import fcntl
from emudaemon.syscall import openfile
import sys_stat


def userblock_exec(args):
    passwd_fd = fcntl.open('/etc/passwd', openfile.O_RDWR)

    if passwd_fd == -1:
        print('Only root can block users.')
        return

    filesize = sys_stat.stat('/etc/passwd')[4]
    f = fcntl.read(passwd_fd, filesize).decode(encoding='ASCII')
    users = [l.split(':') for l in f.splitlines() if l[0] != '#']

    for u in users:
        if u[0] == args.username:
            u[4] = 'nologin'

    fcntl.seek(passwd_fd, 0)
    userslines = [':'.join(u) + '\n' for u in users]
    for l in userslines:
        buf = l.encode(encoding='ASCII')
        fcntl.write(passwd_fd, buf, len(buf))

    fcntl.close(passwd_fd)
