from emudaemon.syscall import readfile
from fs.dir import filerecord
from emudaemon import fdtable
import struct

REC_HEADER_LENGTH = filerecord.IN_FIELD_SIZE + filerecord.RL_FIELD_SIZE + filerecord.NL_FIELD_SIZE


def read_record(fd):
    rec_header = readfile.read_by_offset(fd, REC_HEADER_LENGTH)
    ino, reclen, nlen = struct.unpack('IHB', rec_header)
    name = readfile.read_by_offset(fd, nlen).decode(encoding='ASCII')
    return ino, reclen, name


def readdir(fd):
    ino, reclen, name = read_record(int(fd))
    while ino == 0:
        ino, reclen, name = read_record(int(fd))
    return ino, reclen, name
