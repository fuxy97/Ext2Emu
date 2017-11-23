__author__ = 'fuxy'

import device


class InvalidBlockBufferError(ValueError):
    pass


fs_block_size = None
lba_block_size = None


def check_block_buffer(block_buffer):
    if len(block_buffer) != fs_block_size:
        raise InvalidBlockBufferError('Wrong block buffer size')


def write_block(block_number, block_buffer):
    check_block_buffer(block_buffer)
    for i in range(lba_block_size):
        device.vdevice.write_lba_block(block_number * lba_block_size + i,
                                block_buffer[i * device.vdevice.block_size:(i + 1) * device.vdevice.block_size])


def read_block(block_number):
    block_buffer = bytearray()
    for i in range(lba_block_size):
        block_buffer[i * device.vdevice.block_size:(i + 1) * device.vdevice.block_size] = device.vdevice.read_lba_block(
                                                                                      block_number * lba_block_size + i)
    return bytes(block_buffer)


def init_balloc(block_size):
    global fs_block_size
    global lba_block_size
    fs_block_size = block_size
    lba_block_size = fs_block_size // device.vdevice.block_size

