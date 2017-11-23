__author__ = 'fuxy'

from fs import fs
from fs import balloc
import csv
import os.path

OFFSET_INDEX = 0
SIZE_INDEX = 1


class SysBlock:
    def __init__(self, type_id):
        self.type_id = type_id
        self.block_buffer = None

    def init_struct(self, structname):
        filename = os.path.join(fs.STRUCT_DIR, structname + fs.STRUCT_EXT)
        with open(filename, 'r', newline='') as structfile:
            csvreader = csv.reader(structfile, delimiter=' ')
            for row in csvreader:
                setattr(self, row[0], (int(row[1]), int(row[2])))

    def set_field(self, field, value):
        self.block_buffer[field[OFFSET_INDEX]:field[OFFSET_INDEX] + field[SIZE_INDEX]] = to_bytes(value,
                                                                                      field[SIZE_INDEX])

    def get_field(self, field):
        return self.block_buffer[field[OFFSET_INDEX]:field[OFFSET_INDEX] + field[SIZE_INDEX]]

    def load(self, block_number):
        self.block_buffer = bytearray(balloc.read_block(block_number))

    def unload(self, block_number):
        balloc.write_block(block_number, bytes(self.block_buffer))


def to_bytes(value, size):
    if isinstance(value, int):
        return value.to_bytes(size, 'little')
    elif isinstance(value, str):
        return value.ljust(16, '\0').encode('ASCII')
    else:
        return value[:size]
