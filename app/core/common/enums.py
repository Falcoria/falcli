from enum import Enum


class ImportMode(str, Enum):
    INSERT = "insert"
    REPLACE = "replace"
    UPDATE = "update"
    APPEND = "append"


class DownloadReportFormat(str, Enum):
    JSON = "json"
    XML = "xml"
