import dcntl


def rmdir_exec(args):
    if dcntl.rmdir(args.path) == -1:
        print("Can't remove directory " + args.path)
