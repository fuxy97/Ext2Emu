MAX_FD = 2000


def build_fd_table():
    released_fd = []
    fd_table = []

    fd = 0

    def release_fd_table():
        nonlocal fd
        fd = 0
        del fd_table[:]
        del released_fd[:]

    def reserve_fd(inode_number):
        nonlocal fd
        if not released_fd:
            fd_table.append((0, inode_number))
            fd += 1
            return fd - 1
        else:
            free_fd = released_fd.pop()
            fd_table[free_fd] = (0, inode_number)
            return free_fd

    def release_fd(fd_to_release):
        released_fd.append(fd_to_release)

    def get_offset(fd):
        return fd_table[fd][0]

    def set_offset(fd, offset):
        fd_table[fd] = (offset, fd_table[fd][1])

    def get_inode(fd):
        return fd_table[fd][1]

    return reserve_fd, release_fd, get_inode, get_offset, set_offset, release_fd_table


reserve_fd, release_fd, get_inode, get_offset, set_offset, release_fd_table = build_fd_table()
