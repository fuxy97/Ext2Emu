__author__ = 'fuxy'

from fs import sysblock
from fs import fs
import device
from fs import balloc

superblock = sysblock.SysBlock(fs.SB_TYPE)
superblock.init_struct(fs.SB_NAME)


def load_superblock(partition_name):
    device.init_device(512)
    device.vdevice.bound_partition(partition_name)

    # block size loading hack
    balloc.init_balloc(512)  # 512b - minimum block size (sector's size)
    superblock.load(0)

    balloc.init_balloc(fs.bytes_to_int(superblock.get_field(superblock.s_log_block_size)) * 1024)
    superblock.load(0)

