__author__ = 'fuxy'

import argparse


class MkfsPartitionNameAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if len(values) > 16:
            parser.error('Partition name too long. Length of name should be no more than 16 characters.')
            # raise argparse.ArgumentError('...')

        setattr(namespace, self.dest, values)


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

mkfsparser.add_argument('partition_name', action=MkfsPartitionNameAction)
mkfsparser.add_argument('-B', '--block-size', type=int, default=4096, choices=[1024, 2048, 4096], dest='block_size')
mkfsparser.add_argument('-G', '--blocks-per-group', type=int, dest='blocks_per_group', action=BlocksPerGroupAction)
mkfsparser.add_argument('-I', '--inodes-per-group', type=int, dest='inodes_per_group', action=InodesPerGroupAction)
mkfsparser.add_argument('-S', '--partition-size', type=int, dest='partition_size', action=MkfsPartitionSizeAction)

partmanparser.add_argument('action', choices=['d', 'n', 'l', 'delete', 'new', 'list'])
partmanparser.add_argument('partition_name', nargs='?', action=PartmanPartitionNameAction)
partmanparser.add_argument('-S', '--partition-size', type=int, dest='partition_size',
                           action=PartmanPartitionSizeAction)

ext2emudparser.add_argument('-p', '--partition-name', dest='partition_name', action=PartmanPartitionNameAction)
ext2emudparser.add_argument('action', choices=['start', 'stop', 'restart'])


def parse_args():
    args = parser.parse_args()
    return args
