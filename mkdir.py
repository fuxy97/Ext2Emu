import dcntl
from fs import inodetable


def mkdir_exec(args):
    if dcntl.mkdir(args.path, inodetable.S_IRUSR | inodetable.S_IWUSR | inodetable.S_IXUSR
                   | inodetable.S_IWGRP | inodetable.S_IRGRP | inodetable.S_IXGRP
                   | inodetable.S_IROTH | inodetable.S_IXOTH) == -1:
        print("Can't create directory " + args.path)
