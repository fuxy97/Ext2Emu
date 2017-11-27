from fs import fs
from fs.superblock import superblock
from fs import inodetable
from fs import inodebitmap
from fs import gdtable
import time
from fs import sysblock
from emudaemon import fdtable
from fs.dir import filerecord
from emudaemon import user
from emudaemon import permissions


class DirNotFoundError(ValueError):
    pass


class FileAlreadyExistsError(ValueError):
    pass


def create_file_record(path, mode):
    if path == '/':
        raise FileAlreadyExistsError('/')

    names = [n for n in path.split('/') if n != '']
    bg_block = gdtable.get_gdtableblock(0)
    inodebitmap.inode_bitmap.load(fs.bytes_to_int(bg_block.get_field(0, bg_block.bg_inode_bitmap)))
    inode_ign = inodebitmap.find_first_free_inode()
    inode_n = fs.ign_to_in(
        0,
        fs.bytes_to_int(superblock.get_field(superblock.s_inodes_per_group)),
        inode_ign
    )

    dir_table_in = 0
    dir_inodetable_block = inodetable.load_inode(dir_table_in)
    dir_in = 0

    perm = inodetable.S_IRUSR | inodetable.S_IRGRP | inodetable.S_IROTH
    if not permissions.check_file_permissions(dir_inodetable_block, dir_in, perm):
        raise permissions.PermissionsError(perm)

    if len(names) > 1:
        for n in names[:-1]:
            offset = filerecord.find_file_record(dir_inodetable_block, dir_table_in, n)

            inodetable.unload_inode(dir_in)

            if offset is None:
                raise DirNotFoundError(n)

            dir_in = filerecord.get_record_inode_number(offset)
            dir_table_in = inodetable.get_table_number(dir_in)
            dir_inodetable_block = inodetable.load_inode(dir_in)

            if not permissions.check_file_permissions(dir_inodetable_block, dir_in, perm):
                raise permissions.PermissionsError(perm)

            if fs.bytes_to_int(dir_inodetable_block.get_field(
                    dir_table_in,
                    dir_inodetable_block.i_mode
            )) & inodetable.S_IFDIR != inodetable.S_IFDIR:
                raise DirNotFoundError(n)

    perm = inodetable.S_IWUSR | inodetable.S_IWGRP | inodetable.S_IWOTH
    if not permissions.check_file_permissions(dir_inodetable_block, dir_in, perm):
        raise permissions.PermissionsError(perm)

    offset = filerecord.find_file_record(dir_inodetable_block, dir_table_in, names[-1])
    if offset is None:
        filerecord.create_file_record(dir_inodetable_block, dir_table_in, inode_n, names[-1])
        dir_inodetable_block.set_field(dir_table_in, dir_inodetable_block.i_mtime, int(time.time()))
    else:
        raise FileAlreadyExistsError(names[-1])

    inodetable_block = inodetable.load_inode(inode_n)
    inodetable_block.set_field(inode_ign, inodetable_block.i_mode, mode)
    inodetable_block.set_field(inode_ign, inodetable_block.i_uid, user.get_uid())
    inodetable_block.set_field(inode_ign, inodetable_block.i_size, 0)
    inodetable_block.set_field(inode_ign, inodetable_block.i_atime, 0)
    inodetable_block.set_field(inode_ign, inodetable_block.i_mtime, 0)
    inodetable_block.set_field(inode_ign, inodetable_block.i_ctime, int(time.time()))
    inodetable_block.set_field(inode_ign, inodetable_block.i_dtime, 0)
    inodetable_block.set_field(inode_ign, inodetable_block.i_gid, user.get_gid())
    inodetable_block.set_field(inode_ign, inodetable_block.i_blocks, 0)
    inodetable_block.set_field(inode_ign, inodetable_block.i_flags, 0)
    inodetable_block.set_field(inode_ign, inodetable_block.i_block, bytes(60))
    inodetable_block.set_field(inode_ign, inodetable_block.i_pad, bytes(
        inodetable_block.i_pad[sysblock.SIZE_INDEX]))
    inodebitmap.set_used_inode(inode_ign)
    inodebitmap.inode_bitmap.unload(fs.bytes_to_int(bg_block.get_field(0, bg_block.bg_inode_bitmap)))
    inodetable.unload_inode(inode_n)
    inodetable.unload_inode(0)
    return fdtable.reserve_fd(inode_n)


def create_file(path, mode):
    if not user.is_user_authenticated():
        raise user.NoAuthUserError()

    return create_file_record(path, int(mode) | inodetable.S_IFREG)
