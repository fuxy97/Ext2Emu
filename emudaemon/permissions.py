from emudaemon import user
from fs import inodetable

UMASK = 0o700
GMASK = 0o070
OMASK = 0o007


class PermissionsError(Exception):
    pass


def check_file_permissions(inode_block, inode_n, perm):
    uid = user.get_uid()
    gid = user.get_gid()

    if uid == 0 or gid == 0:
        return True

    if inodetable.check_uid(inode_block, inode_n, uid):
        return inodetable.check_file_permissions(inode_block, inode_n, perm & UMASK)

    if inodetable.check_gid(inode_block, inode_n, gid):
        return inodetable.check_file_permissions(inode_block, inode_n, perm & GMASK)

    return inodetable.check_file_permissions(inode_block, inode_n, perm & OMASK)
