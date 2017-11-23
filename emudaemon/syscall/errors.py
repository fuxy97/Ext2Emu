from enum import Enum


class MessageType(Enum):
    ERROR_MESSAGE = 1
    RESULT_MESSAGE = 2


class ErrorMessage(Enum):
    DIR_NOT_FOUND = 'DIR_NOT_FOUND_ERROR'
    FILE_ALREADY_EXISTS = 'FILE_ALREADY_EXISTS'
    FILE_NOT_EXISTS = 'FILE_NOT_EXISTS'
    WRONG_FILE_TYPE = 'WRONG_FILE_TYPE'