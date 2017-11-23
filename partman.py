__author__ = 'fuxy'

import os

PARTITIONS_DIRNAME = '.partitions'
PARTITION_EXTENSION = '.prt'


class InvalidPartitionNameError(ValueError):
    pass


class InvalidPartitionSizeError(ValueError):
    pass


def get_partition_filename(name):
    filename = os.path.join(PARTITIONS_DIRNAME, name + PARTITION_EXTENSION)
    if not os.path.isfile(filename):
        raise InvalidPartitionNameError("Partition doesn't exists")
    return filename


def get_parition_size(name):
    return os.path.getsize(get_partition_filename(name))


def add_partition(name, size):
    if size is None:
        raise InvalidPartitionSizeError('Partition size required')

    if name is None:
        raise InvalidPartitionNameError('Partition name required')

    filename = os.path.join(PARTITIONS_DIRNAME, name + PARTITION_EXTENSION)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    if os.path.isfile(filename):
        raise InvalidPartitionNameError('Partition already exists')
    else:
        with open(filename, 'w+b') as file:
            file.write(os.urandom(size))


def delete_partition(name, size):
    if name is None:
        raise InvalidPartitionNameError('Partition name required')
    os.remove(get_partition_filename(name))


def list_partition(name, size):
    os.makedirs(PARTITIONS_DIRNAME, exist_ok=True)
    partitions = [(os.path.splitext(p)[0], os.path.getsize(os.path.join(PARTITIONS_DIRNAME, p)) >> 20)
                  for p in os.listdir(PARTITIONS_DIRNAME)]

    if not partitions:
        print('Partition table is empty.')
    else:
        print('Partition'.rjust(15), 'Size (Mb)'.rjust(12))
        for p in partitions:
            print('{0:>15}{1:12d}'.format(p[0], p[1]))


commands = {
    'n': add_partition,
    'new': add_partition,
    'd': delete_partition,
    'delete': delete_partition,
    'l': list_partition,
    'list': list_partition
}


def exec_partman(args):
    commands[args.action](args.partition_name, args.partition_size)

