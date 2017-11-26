import fcntl


def exec_rm(args):
    if fcntl.unlink(args.path) == -1:
        print("Can't remove " + args.path)
