MAX_FD = 2000


def build_fd_table():
    released_fd = []
    fd_table = []

    fd = 0

    def reserve_fd(inode_number):
        nonlocal fd
        if not released_fd:
            fd_table.append((fd, 0, inode_number))
            fd += 1
        else:
            fd_table.append((released_fd.pop(), 0, inode_number))
        return fd_table[-1]

    def release_fd(fd_to_release):
        for i, t in enumerate(fd_table):
            fd = t[0]
            if fd == fd_to_release:
                released_fd.append(fd_table.pop(i)[0])

    def get_offset(fd):
        return fd_table[fd][1]

    def set_offset(fd, offset):
        fd_table[fd] = (fd, offset, fd_table[fd][2])

    def get_inode(fd):
        return fd_table[fd][2]

    return reserve_fd, release_fd, get_inode, get_offset, set_offset


reserve_fd, release_fd, get_inode, get_offset, set_offset = build_fd_table()
