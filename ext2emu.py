__author__ = 'fuxy'

import partman
import mkfs
import ls
import pipe
from emudaemon import ext2emud
from getpass import getpass
import user
import rm
import cp


def user_login(args):
    print('[ext2emud] user authorization:')
    uname = input('Enter username: ')
    upass = getpass('Enter password: ')
    if user.login(uname, upass) == -1:
        print('Wrong username or password or user already logged.')


def user_exit(args):
    user.exit()


utilities = {
    'partman': partman.exec_partman,
    'mkfs': mkfs.exec_mkfs,
    'ext2emud': ext2emud.exec_ext2emud,
    'login': user_login,
    'exit': user_exit,
    'ls': ls.exec_ls,
    '>': pipe.exec_pipe,
    'rm': rm.exec_rm,
    'cp': cp.exec_cp
}

if __name__ == '__main__':
    from emuargparser import parse_args
    args = parse_args()
    utilities[args.utility](args)
