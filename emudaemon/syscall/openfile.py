from fs import fs
from fs.superblock import superblock
from fs import inodetable
from fs import inodebitmap
from fs import gdtable
import time
from fs import sysblock
from emudaemon import fdtable
from fs.dir import filerecord
from emudaemon.syscall import deletefile
from emudaemon.syscall import createfile


class DirNotFoundError(ValueError):
    pass


class FileAlreadyExistsError(ValueError):
    pass


O_CREAT = 0x0001
O_EXCL = 0x0002


def create_file_descriptor(path, mode):
    names = [n for n in path.split('/') if n != '']

    dir_table_in = 0
    dir_inodetable_block = inodetable.load_inode(dir_table_in)
    dir_in = 0

    if len(names) > 1:
        for n in names[:-1]:
            offset = filerecord.find_file_record(dir_inodetable_block, dir_table_in, n)

            inodetable.unload_inode(dir_in)

            if offset is None:
                raise createfile.DirNotFoundError(n)

            dir_in = filerecord.get_record_inode_number(offset)
            dir_table_in = inodetable.get_table_number(dir_in)
            dir_inodetable_block = inodetable.load_inode(dir_in)

            if fs.bytes_to_int(dir_inodetable_block.get_field(
                    dir_table_in,
                    dir_inodetable_block.i_mode
            )) & inodetable.S_IFDIR != inodetable.S_IFDIR:
                raise createfile.DirNotFoundError(n)

    offset = filerecord.find_file_record(dir_inodetable_block, dir_table_in, names[-1])

    if offset is None:
        raise deletefile.FileNotExistsError(names[-1])

    inode_n = filerecord.get_record_inode_number(offset)
    inode_table_n = inodetable.get_table_number(inode_n)
    file_inodetable_block = inodetable.load_inode(inode_n)

    if fs.bytes_to_int(file_inodetable_block.get_field(
            inode_table_n,
            file_inodetable_block.i_mode
    )) & mode != mode:
        raise deletefile.WrongFileTypeError(names[-1])

    inodetable.unload_inode(dir_in)
    inodetable.unload_inode(0)
    return fdtable.reserve_fd(inode_n)[0]


def open_file(path, oflag, mode='0'):
    if int(oflag) == 0:
        return create_file_descriptor(path, inodetable.S_IFREG)
    elif int(oflag) == O_CREAT | O_EXCL:
        return createfile.create_file(path, mode)
