from enum import Enum 

class ServerCommandsResponse(int,Enum):
    OK = 0
    NOT_RUNNING = 1
    INFO = 2