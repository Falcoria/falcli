from enum import Enum


class ScanCommands(str, Enum):
    START = "start"
    STOP = "stop"
    STATUS = "status"
