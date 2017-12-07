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
from emudaemon import permissions
from emudaemon import user

O_CREAT = 0x0200
O_EXCL = 0x0800
O_RDONLY = 0x0
O_WRONLY = 0x1
O_RDWR = 0x2
O_STAT = 0x3


class DirNotFoundError(ValueError):
    pass


class FileAlreadyExistsError(ValueError):
    pass


def create_file_descriptor(path, oflag, mode):
    names = [n for n in path.split('/') if n != '']

    dir_table_in = 0
    dir_inodetable_block = inodetable.load_inode(dir_table_in)
    dir_in = 0

    perm = inodetable.S_IRUSR | inodetable.S_IRGRP | inodetable.S_IROTH

    if not permissions.check_file_permissions(dir_inodetable_block, dir_in, perm):
        raise permissions.PermissionsError(perm)

    if path != '/':
        if len(names) > 1:
            for n in names[:-1]:
                offset = filerecord.find_file_record(dir_inodetable_block, dir_table_in, n)

                inodetable.unload_inode(dir_in)

                if offset is None:
                    raise createfile.DirNotFoundError(n)

                dir_in = filerecord.get_record_inode_number(offset)
                dir_table_in = inodetable.get_table_number(dir_in)
                dir_inodetable_block = inodetable.load_inode(dir_in)

                if not permissions.check_file_permissions(dir_inodetable_block, dir_in, perm):
                    raise permissions.PermissionsError(perm)

                if fs.bytes_to_int(dir_inodetable_block.get_field(
                        dir_table_in,
                        dir_inodetable_block.i_mode
                )) & inodetable.S_IFDIR != inodetable.S_IFDIR:
                    raise createfile.DirNotFoundError(n)

        offset = filerecord.find_file_record(dir_inodetable_block, dir_table_in, names[-1])

        if oflag == O_WRONLY:
            perm = inodetable.S_IWUSR | inodetable.S_IWGRP | inodetable.S_IWOTH
        if oflag == O_RDWR:
            perm |= inodetable.S_IWUSR | inodetable.S_IWGRP | inodetable.S_IWOTH

        if offset is None:
            raise deletefile.FileNotExistsError(names[-1])

        inode_n = filerecord.get_record_inode_number(offset)
        inode_table_n = inodetable.get_table_number(inode_n)
        file_inodetable_block = inodetable.load_inode(inode_n)
    else:
        if oflag == O_WRONLY:
            perm = inodetable.S_IWUSR | inodetable.S_IWGRP | inodetable.S_IWOTH
        if oflag == O_RDWR:
            perm |= inodetable.S_IWUSR | inodetable.S_IWGRP | inodetable.S_IWOTH

        inode_n = dir_in
        inode_table_n = dir_table_in
        file_inodetable_block = dir_inodetable_block

    if fs.bytes_to_int(file_inodetable_block.get_field(
            inode_table_n,
            file_inodetable_block.i_mode
    )) & mode != mode:
        raise deletefile.WrongFileTypeError(names[-1])

    if oflag != O_STAT:
        if not permissions.check_file_permissions(file_inodetable_block, inode_n, perm):
            raise permissions.PermissionsError(perm)

    inodetable.unload_inode(dir_in)
    inodetable.unload_inode(0)
    return fdtable.reserve_fd(inode_n)


def open_file(path, oflag, mode='0'):
    if not user.is_user_authenticated():
        raise user.NoAuthUserError()
    if int(oflag) & (O_CREAT | O_EXCL) == 0:
        return create_file_descriptor(path, int(oflag), inodetable.S_IFREG)
    else:
        return createfile.create_file(path, mode)
