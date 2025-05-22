# app/messages/errors.py

class HTTP:
    ERROR = "HTTP error: {status} - {message}"
    REQUEST_FAILED = "Request failed: {error}"
    UNEXPECTED_ERROR = "Unexpected error occurred: {error}"
    FAILED_JSON_PARSE = "Failed to parse JSON response: {error}"

class Project:
    NOT_FOUND = "Project '{project}' not found."
    CREATION_FAILED = "Failed to create project '{project}'."
    DELETE_FAILED = "Failed to delete project '{project}'."
    CANNOT_CREATE = "Cannot create project."
    CANNOT_DELETE = "Cannot delete project."
    ID_REQUIRED = "Project ID is required."
    PROJECT_ID_REQUIRED = "Project ID is required for this operation."

class IP:
    NOT_FOUND = "IP '{ip}' not found in project '{project}'."
    ADD_FAILED = "Failed to add IP '{ip}' to project '{project}'."
    DELETE_FAILED = "Failed to remove IP '{ip}' from project '{project}'."
    FAILED_DOWNLOAD = "Failed to download IPs from project '{project}'."
    

class Port:
    NOT_FOUND = "Port '{port}' not found for IP '{ip}'."

class Check:
    NOT_FOUND = "Check '{check}' not found for port '{port}' on IP '{ip}'."

class Auth:
    UNAUTHORIZED = "Unauthorized. Please check your API token."

class Config:
    MISSING_VALUES = (
        "Configuration error: Missing or invalid values in config.yaml. "
        "Please make sure to set 'backend_base_url', 'tasker_base_url', and 'token'."
    )

class Scan:
    CONFIG_NOT_FOUND = "Scan configuration file not found: {path}"
    CONFIG_READ_FAILED = "Failed to read scan config: {error}"
    CONFIG_VALIDATION_FAILED = "Validation error in scan config: {error}"
    TARGETS_FILE_NOT_FOUND = "Targets file not found: {path}"
    NO_TARGETS_FOUND = "No targets found in the provided file."
    START_FAILED = "Failed to start scan for project {project}"
    STOP_FAILED = "Failed to stop scan for project {project}"
    STATUS_FAILED = "Failed to get scan status for project {project}"


class Worker:
    FAILED_TO_GET_IPS = "Failed to retrieve worker IPs."