from fs import fs
from fs import inodetable
from fs import inodebitmap
from fs import gdtable
from emudaemon import fdtable
from fs.dir import filerecord
from emudaemon.syscall import createfile
from fs.datablockbuffer import data_block_buffer
from emudaemon import user
from emudaemon import permissions


class FileNotExistsError(ValueError):
    pass


class WrongFileTypeError(ValueError):
    pass


def delete_file_record(path, mode):
    names = [n for n in path.split('/') if n != '']
    bg_block = gdtable.get_gdtableblock(0)
    inodebitmap.inode_bitmap.load(fs.bytes_to_int(bg_block.get_field(0, bg_block.bg_inode_bitmap)))

    dir_table_in = 0
    dir_inodetable_block = inodetable.load_inode(dir_table_in)
    dir_in = 0

    perm = inodetable.S_IRUSR | inodetable.S_IRGRP | inodetable.S_IROTH
    if not permissions.check_file_permissions(dir_inodetable_block, dir_in, perm):
        raise PermissionError(perm)

    if len(names) > 1:
        for n in names[:-1]:
            offset = filerecord.find_file_record(dir_inodetable_block, dir_table_in, n)
            if dir_in != 0:
                inodetable.unload_inode(dir_in)

            if offset is None:
                raise createfile.DirNotFoundError(n)

            dir_in = filerecord.get_record_inode_number(offset)
            dir_table_in = inodetable.get_table_number(dir_in)
            dir_inodetable_block = inodetable.load_inode(dir_in)

            if not permissions.check_file_permissions(dir_inodetable_block, dir_in, perm):
                raise PermissionError(perm)

            if fs.bytes_to_int(dir_inodetable_block.get_field(
                    dir_table_in,
                    dir_inodetable_block.i_mode
            )) & inodetable.S_IFDIR != inodetable.S_IFDIR:
                raise createfile.DirNotFoundError(n)

    perm = inodetable.S_IWUSR | inodetable.S_IWGRP | inodetable.S_IWGRP
    if not permissions.check_file_permissions(dir_inodetable_block, dir_in, perm):
        raise PermissionError(perm)

    offset = filerecord.find_file_record(dir_inodetable_block, dir_table_in, names[-1])

    if offset is None:
        raise FileNotExistsError(names[-1])

    inode_n = filerecord.get_record_inode_number(offset)
    inode_table_n = inodetable.get_table_number(inode_n)
    file_inodetable_block = inodetable.load_inode(inode_n)

    if fs.bytes_to_int(file_inodetable_block.get_field(
            inode_table_n,
            file_inodetable_block.i_mode
    )) & mode != mode:
        raise WrongFileTypeError(names[-1])

    filerecord.remove_file_record(offset)
    inodebitmap.set_free_inode(inode_table_n)
    inodebitmap.inode_bitmap.unload(fs.bytes_to_int(bg_block.get_field(0, bg_block.bg_inode_bitmap)))
    inodetable.unload_inode(inode_n)
    inodetable.unload_inode(dir_in)
    inodetable.unload_inode(0)
    data_block_buffer.unload(data_block_buffer.block_number)


def delete_file(path):
    if not user.is_user_authenticated():
        raise user.NoAuthUserError()

    delete_file_record(path, inodetable.S_IFREG)
    return 0
