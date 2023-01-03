from enum import Enum

class ExecutionMethodEnum(str, Enum):
    START = 'start'     
    STOP = 'stop'     
    RESTART = 'restart'
