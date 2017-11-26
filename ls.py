import dcntl
import sys_stat
import fcntl
import time
from fs import inodetable

verbose = False
show_hidden = False


def show_dir_record(name, path, users, groups):
    st = sys_stat.stat(path + '/' + name)
    print('d' if sys_stat.is_dir(st[1]) else '-', end='')
    print('r' if st[1] & inodetable.S_IRUSR else '-', end='')
    print('w' if st[1] & inodetable.S_IWUSR else '-', end='')
    print('x' if st[1] & inodetable.S_IXUSR else '-', end='')
    print('r' if st[1] & inodetable.S_IRGRP else '-', end='')
    print('w' if st[1] & inodetable.S_IWGRP else '-', end='')
    print('x' if st[1] & inodetable.S_IXGRP else '-', end='')
    print('r' if st[1] & inodetable.S_IROTH else '-', end='')
    print('w' if st[1] & inodetable.S_IWOTH else '-', end='')
    print('x' if st[1] & inodetable.S_IXOTH else '-', end=' ')

    print('{0:4} {1:4} {2:4} {3:12} {4}'.format(next(u[0] for u in users if int(u[2]) == st[2]),
          next(g[0] for g in groups if int(g[1]) == st[3]), st[4],
          time.strftime('%b %d %H:%M', time.gmtime(st[6])).lower(), name))


def show_dir_list(path):
    fd = dcntl.opendir(path)

    if fd == -1:
        print('Unable to open directory ' + path)
        return

    users = None
    groups = None
    if verbose:
        passwd_fd = fcntl.open('/etc/passwd')

        buf = fcntl.read(passwd_fd, sys_stat.stat('/etc/passwd')[4])
        users = tuple(tuple(l.split(':')) for l in buf.decode(encoding='ASCII').splitlines()
                      if l.lstrip()[0] != '#')
        fcntl.close(passwd_fd)

        group_fd = fcntl.open('/etc/group')

        buf = fcntl.read(group_fd, sys_stat.stat('/etc/group')[4])
        groups = tuple(tuple(l.split(':')) for l in buf.decode(encoding='ASCII').splitlines()
                       if l.lstrip()[0] != '#')
        fcntl.close(group_fd)

    r = dcntl.readdir(fd)
    while r != -1:
        ino, reclen, name = r
        if verbose:
            show_dir_record(name, path, users, groups)
        else:
            print(name, end='\t')
            print()
        r = dcntl.readdir(fd)

    dcntl.closedir(fd)


def exec_ls(args):
    global verbose, show_hidden
    verbose = args.list
    show_hidden = args.all
    show_dir_list(args.path)
