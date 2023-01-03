from enum import Enum 

class ServerStatusEnum(str,Enum):
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"