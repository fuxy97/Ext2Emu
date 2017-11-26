from emudaemon.syscall import closefile


def closedir(fd):
    return closefile.close_file(fd)
