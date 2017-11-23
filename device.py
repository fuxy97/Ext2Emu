__author__ = 'fuxy'

import partman
import os


class UnboundPartitionError(UnboundLocalError):
    pass


class VirtualMemoryDevice:
    def __init__(self, sector_size):
        self.block_size = sector_size
        self.device_size = 0
        self.device_file = None

    def bound_partition(self, partition_name):
        filename = partman.get_partition_filename(partition_name)
        self.device_size = partman.get_parition_size(partition_name)
        self.device_file = open(filename, 'r+b')

    def write_lba_block(self, address, block):
        if self.device_file is None:
            raise UnboundPartitionError("Partition unbound to device")

        self.device_file.seek(address * self.block_size, os.SEEK_SET)
        self.device_file.write(block)

    def read_lba_block(self, adress):
        if self.device_file is None:
            raise UnboundPartitionError("Partition unbound to device")

        self.device_file.seek(adress * self.block_size, os.SEEK_SET)
        return self.device_file.read(self.block_size)


vdevice = None


def init_device(sector_size):
    global vdevice
    vdevice = VirtualMemoryDevice(sector_size)
