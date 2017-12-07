__author__ = 'fuxy'

import argparse


class MkfsPartitionNameAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if len(values) > 16:
            parser.error('Partition name too long. Length of name should be no more than 16 characters.')
            # raise argparse.ArgumentError('...')

        setattr(namespace, self.dest, values)


class ChmodModeAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if len(values) > 3:
            parser.error('Mode value too long. No more than 3 octal digits.')
        try:
            setattr(namespace, self.dest, int(values, 8))
        except ValueError:
            print("Invalid octal mode's value.")
            exit(0)


class PartmanPartitionNameAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values is not None and len(values) > 16:
            parser.error('Partition name too long. Length of name should be no more than 16 characters.')
            # raise argparse.ArgumentError('...')

        setattr(namespace, self.dest, values)


class MkfsPartitionSizeAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values < 128:
            parser.error('Partition size should be 128Mb at least.')
            # raise argparse.ArgumentError('...')

        blocks_per_group = getattr(namespace, 'blocks_per_group')
        inodes_per_group = getattr(namespace, 'inodes_per_group')
        if blocks_per_group is None:
            setattr(namespace, 'blocks_per_group', getattr(namespace, 'block_size') * 8)
        if inodes_per_group is None:
            setattr(namespace, 'inodes_per_group', getattr(namespace, 'blocks_per_group'))

        setattr(namespace, self.dest, values << 20)


class PartmanPartitionSizeAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values << 20)


class BlocksPerGroupAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        max = getattr(namespace, 'block_size') * 8
        if values > max or values < 1:
            parser.error('Wrong blocks per group value.')
            # raise argparse.ArgumentError('...')

        setattr(namespace, self.dest, values)


class InodesPerGroupAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        max = getattr(namespace, 'blocks_per_group')
        if values > max or values < 1:
            parser.error('Wrong inodes per group value.')
            # raise argparse.ArgumentError('...')

        setattr(namespace, self.dest, values)


parser = argparse.ArgumentParser(prog='Ext2 Emulator', description='Emulates ext2 file system.')
subparsers = parser.add_subparsers(dest='utility')
mkfsparser = subparsers.add_parser('mkfs', prog='Ext2 Emulator mkfs utility', description='Utility for '
                                                                                          'creating file system on '
                                                                                          'partition.')
partmanparser = subparsers.add_parser('partman', prog='Ext2 Emulator partman utility', description='Utility for '
                                                                                                   'managing '
                                                                                                   'partitions.')
ext2emudparser = subparsers.add_parser('ext2emud', prog='Ext2 Emulator daemon', description='Emulator program. It is '
                                                                                            'designed to be as a '
                                                                                            'standalone daemon '
                                                                                            'process.')

subparsers.add_parser('login', prog='Ext2 Emulator login utility', description='Utility for user authorization in '
                                                                               'emulator.')
subparsers.add_parser('exit', prog='Ext2 Emulator exit utility', description='Utility for user quiting from emulator.')

lsparser = subparsers.add_parser('ls', prog='Ext2 Emulator ls utility',
                                 description='List directory contents, information about files.')

pipeparser = subparsers.add_parser('>', prog='Ext2 Emulator pipe utility',
                                   description='Redirect stdin to file and redirect file to stdout.')

rmparser = subparsers.add_parser('rm', prog='Ext2 Emulator rm utility',
                                 description="Remove files. This utility doesn't remove directories. "
                                             "Please use rmdir for this purpose.")

cpparser = subparsers.add_parser('cp', prog='Ext2 Emulator cp utility',
                                 description="Copy files. This utility doesn't copy directories.")

mkdirparser = subparsers.add_parser('mkdir', prog='Ext2 Emulator mkdir utility',
                                    description="Create directories with permissions as in user's umask.")

rmdirparser = subparsers.add_parser('rmdir', prog='Ext2 Emulator rmdir utility',
                                    description="Remove directories. This utility doesn't remove files.")

useraddparser = subparsers.add_parser('useradd', prog='Ext2 Emulator useradd utility',
                                      description="Add users. Creates new record in /etc/passwd file.")

userblockparser = subparsers.add_parser('userblock', prog='Ext2 Emulator userblock utility',
                                        description="Block users. User can't login after blocking.")

chmodparser = subparsers.add_parser('chmod', prog='Ext2 Emulator chmod utility.',
                                    description="Change file's mode. Only owner of file or root can change mode.")


mkfsparser.add_argument('partition_name', action=MkfsPartitionNameAction)
mkfsparser.add_argument('-B', '--block-size', type=int, default=4096, choices=[1024, 2048, 4096], dest='block_size')
mkfsparser.add_argument('-G', '--blocks-per-group', type=int, dest='blocks_per_group', action=BlocksPerGroupAction)
mkfsparser.add_argument('-I', '--inodes-per-group', type=int, dest='inodes_per_group', action=InodesPerGroupAction)
mkfsparser.add_argument('-S', '--partition-size', type=int, dest='partition_size', action=MkfsPartitionSizeAction)

partmanparser.add_argument('action', choices=['d', 'n', 'l', 'delete', 'new', 'list'])
partmanparser.add_argument('partition_name', nargs='?', action=PartmanPartitionNameAction)
partmanparser.add_argument('-S', '--partition-size', type=int, dest='partition_size',
                           action=PartmanPartitionSizeAction)

lsparser.add_argument('-l', '--list', dest='list', action='store_true')
lsparser.add_argument('-a', '--all', dest='all', action='store_true')
lsparser.add_argument('path', type=str)

ext2emudparser.add_argument('-p', '--partition-name', dest='partition_name', action=PartmanPartitionNameAction)
ext2emudparser.add_argument('action', choices=['start', 'stop', 'restart', 'init'])

pipeparser.add_argument('path', type=str)

rmparser.add_argument('path', type=str)
rmparser.add_argument('-r', '--recursive', dest='recursive', action='store_true')

cpparser.add_argument('source', type=str)
cpparser.add_argument('dest', type=str)

mkdirparser.add_argument('path', type=str)
rmdirparser.add_argument('path', type=str)
useraddparser.add_argument('username', type=str)
userblockparser.add_argument('username', type=str)

chmodparser.add_argument('mode', type=str, action=ChmodModeAction)
chmodparser.add_argument('path', type=str)


def parse_args():
    args = parser.parse_args()
    return args

