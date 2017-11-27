import fcntl
from emudaemon.syscall import openfile
import sys_stat
import hashlib
from getpass import getpass


def useradd_exec(args):
    passwd_fd = fcntl.open('/etc/passwd', openfile.O_RDWR)
    group_fd = fcntl.open('/etc/group', openfile.O_RDWR)

    if passwd_fd == -1:
        print('Only root can add users.')
        return

    print('[useradd] password for ' + args.username + ':')
    upass = getpass('Enter new ' + args.username + ' password:')
    re_upass = getpass('Retype new ' + args.username + ' password:')

    while upass != re_upass:
        print('You typed password incorrectly. Type again:')
        upass = getpass('Enter new ' + args.username + ' password:')
        re_upass = getpass('Retype new ' + args.username + ' password:')

    filesize = sys_stat.stat('/etc/passwd')[4]
    f = fcntl.read(passwd_fd, filesize).decode(encoding='ASCII')
    users = tuple(tuple(l.split(':')) for l in f.splitlines() if l[0] != '#')
    last_uid = int(users[-1][2])

    filesize = sys_stat.stat('/etc/group')[4]
    f = fcntl.read(group_fd, filesize).decode(encoding='ASCII')
    groups = tuple(tuple(l.split(':')) for l in f.splitlines() if l[0] != '#')
    last_gid = int(groups[-1][1])

    userline = (':'.join([args.username, hashlib.sha224(upass.encode()).hexdigest(), str(last_uid + 1),
                         str(last_gid + 1)]) + ':\n').encode(encoding='ASCII')
    fcntl.write(passwd_fd, userline, len(userline))

    groupline = (':'.join([args.username, str(last_gid + 1)]) + ':\n').encode(encoding='ASCII')
    fcntl.write(group_fd, groupline, len(groupline))

    fcntl.close(passwd_fd)
    fcntl.close(group_fd)
