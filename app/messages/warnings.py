# app/messages/warnings.py

class General:
    REQUEST_RETRYING = "Retrying request due to network issue..."
    DEPRECATED_FEATURE = "Warning: This feature is deprecated and will be removed in future versions."

class Project:
    NOT_FULLY_DELETED = "Some project data could not be fully deleted."

class IPs:
    PARTIAL_IMPORT = "Some IPs could not be imported."
