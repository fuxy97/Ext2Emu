import fcntl
from fs import inodetable
import sys_stat


def exec_cp(args):
    src_fd = fcntl.open(args.source)

    if src_fd == -1:
        print("Can't open " + args.source)
        return

    fcntl.unlink(args.dest)
    dst_fd = fcntl.creat(args.dest, inodetable.S_IRUSR | inodetable.S_IWUSR |
                         inodetable.S_IRGRP | inodetable.S_IWGRP | inodetable.S_IROTH)
    if dst_fd == -1:
        print("Can't open or create " + args.dest)
        return

    buf = fcntl.read(src_fd, sys_stat.stat(args.source)[4])
    fcntl.write(dst_fd, buf, len(buf))

    fcntl.close(dst_fd)
    fcntl.close(src_fd)
