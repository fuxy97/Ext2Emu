__author__ = 'fuxy'

import partman
import mkfs
from emudaemon import ext2emud

utilities = {
    'partman': partman.exec_partman,
    'mkfs': mkfs.exec_mkfs,
    'ext2emud': ext2emud.exec_ext2emud
}

if __name__ == '__main__':
    from emuargparser import parse_args
    args = parse_args()
    utilities[args.utility](args)
