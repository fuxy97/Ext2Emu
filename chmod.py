import sys_stat


def chmod_exec(args):
    if sys_stat.chmod(args.path, args.mode) == -1:
        print("Can't change mode for " + args.path + 'file')
