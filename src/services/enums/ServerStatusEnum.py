from enum import Enum 

class ServerStatusEnum(str,Enum):
    STARTED = "STARTED"
    STOPPED = "STOPPED"
    NOT_INSTALLED = "NOT INSTALLED"