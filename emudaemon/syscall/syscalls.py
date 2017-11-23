from enum import Enum


class FileSysCall(Enum):
    CREATE = 1
    DELETE = 2
    OPEN = 3
    CLOSE = 4
    READ = 5
    WRITE = 6
    APPEND = 7
    SEEK = 8
    GET_ATTRIBUTES = 9
    SET_ATTRIBUTES = 10
    RENAME = 11


class DirSysCall(Enum):
    CREATE = 12
    DELETE = 13
    OPEN = 14
    CLOSE = 15
    READ = 16
    RENAME = 17
    LINK = 18
    UNLINK = 19


class UserSysCall(Enum):
    AUTH = 20
    EXIT = 21
