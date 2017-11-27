import fcntl
import dcntl
import sys_stat


class StopRecursiveRemove(Exception):
    pass


def recursive_remove_dir(path):
    fd = dcntl.opendir(path)
    rec = dcntl.readdir(fd)
    try:
        while rec != -1:
            rec_path = path + '/' + rec[2]
            mode = sys_stat.stat(rec_path)[1]
            if sys_stat.is_dir(mode):
                recursive_remove_dir(rec_path)
            else:
                if fcntl.unlink(rec_path) == -1:
                    raise StopRecursiveRemove(rec_path)
            rec = dcntl.readdir(fd)
    finally:
        dcntl.closedir(fd)
    dcntl.rmdir(path)


def exec_rm(args):
    if not args.recursive:
        if fcntl.unlink(args.path) == -1:
            print("Can't remove " + args.path)
    else:
        st = sys_stat.stat(args.path)
        if st != -1:
            if sys_stat.is_dir(st[1]):
                try:
                    recursive_remove_dir(args.path)
                except StopRecursiveRemove as e:
                    print("Can't remove " + str(e) + ' file.')
            else:
                fcntl.unlink(args.path)
        else:
            print("Can't remove " + args.path)
