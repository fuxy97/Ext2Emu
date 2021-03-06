import sys
from fs import inodetable
import fcntl
import sys_stat
from emudaemon.syscall import openfile


def exec_pipe(args):
    if not sys.stdin.isatty():
        fd = fcntl.open(args.path, openfile.O_WRONLY)

        if fd == -1:
            fd = fcntl.creat(args.path, inodetable.S_IWGRP | inodetable.S_IRGRP | inodetable.S_IWUSR
                             | inodetable.S_IRUSR | inodetable.S_IROTH)

            if fd == -1:
                print("Can't open or create file.")
                return

        for l in sys.stdin:
            buf = l.encode(encoding='utf-8')
            fcntl.write(fd, buf, len(buf))

        fcntl.close(fd)

    fd = fcntl.open(args.path, openfile.O_RDONLY)
    if fd == -1:
        print("Can't open file.")
        return

    filesize = sys_stat.stat(args.path)[4]
    if filesize > 0:
        buf = fcntl.read(fd, filesize)
        print(buf.decode(encoding='utf-8'))
    fcntl.close(fd)
