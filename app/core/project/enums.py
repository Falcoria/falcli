from enum import Enum


class ProjectCommands(str, Enum):
    CREATE = "create"
    GET = "get"
    LIST = "list"
    DELETE = "delete"
    SET_ACTIVE = "set-active"