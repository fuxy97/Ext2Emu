from emudaemon import fdtable


def seek(fd, offset):
    fdtable.set_offset(int(fd), int(offset))
    return 0
