from enum import Enum


class MessageType(Enum):
    ERROR_MESSAGE = 1
    RESULT_MESSAGE = 2


class ErrorMessage(Enum):
    DIR_NOT_FOUND = 'DIR_NOT_FOUND_ERROR'
    FILE_ALREADY_EXISTS = 'FILE_ALREADY_EXISTS'
    FILE_NOT_EXISTS = 'FILE_NOT_EXISTS'
    WRONG_FILE_TYPE = 'WRONG_FILE_TYPE'
    WRONG_OFFSET = 'WRONG_OFFSET'
    NO_USER_IN_SYSTEM = 'NO_USER_IN_SYSTEM'
    USER_ALREADY_IN_SYSTEM = 'USER_ALREADY_IN_SYSTEM'
    NO_PERMISSIONS = 'NO_PERMISSIONS'
    DIR_IS_NOT_EMPTY = 'DIR_IS_NOT_EMPTY'

