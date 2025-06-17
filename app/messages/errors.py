class Errors:
    class General:
        PARSE_FAILED = "Failed to parse value: {error}"

    class Profile:
        NOT_FOUND = "Profile '{name}' does not exist."
        NO_ACTIVE_PROFILE = "No active profile set. Please set an active profile first."
        INVALID_FIELD = "Invalid field '{field}'. Allowed fields: {allowed_fields}."
        PARSE_FAILED = "Failed to parse value for field '{field}': {error}."
        MISSING_FIELD = "Missing required fields in profile '{name}': {missing_fields}"
        PROFILE_FILE_NOT_FOUND = "Profile file not found: {file_path}"
        FAILED_TO_LOAD = "Failed to load profile '{name}': {error}"
        MISSING_REQUIRED_FIELDS = "Profile '{name}' is missing required fields: {missing_fields}."

    class Config:
        MISSING_VALUES = (
            "Missing or invalid values in profile. "
            "Fields 'scanledger_base_url', 'tasker_base_url', and 'token' are required."
        )

    class Project:
        CANNOT_CREATE = "Cannot create project."
        ID_REQUIRED = "Project ID required but not provided."
        NOT_FOUND = "Project not found."
        CURRENT_NOT_SET = "Current project is not set. Use 'falcli profile set-default-project <project_id>' to set it."
    
    class IP:
        ADD_FAILED = "Failed to add IP(s) to project '{project}'. IP(s): {ip}."
        FAILED_DOWNLOAD = "Failed to download IPs for project '{project}'."
        DELETE_FAILED = "Failed to delete IP(s) '{ip}' from project '{project}'."
        NOT_FOUND = "IP '{ip}' not found in project."
    
    class Worker:
        FAILED_TO_GET_IPS = "Failed to retrieve worker IPs. Please check the tasker service."

    class Scan:
        NO_HOSTS_PROVIDED = "No hosts provided. Use --hosts, --targets-file, or --from-config."
        NO_TARGETS_FOUND = "No targets found to scan."
        CONFIG_NOT_FOUND = "Scan config file not found: {path}"
        CONFIG_READ_FAILED = "Failed to read scan config file: {error}"
        CONFIG_VALIDATION_FAILED = "Scan config validation failed: {error}"
        TARGETS_FILE_NOT_FOUND = "Targets file not found: {path}"
        START_FAILED = "Scan start failed for project {project}."
        STOP_FAILED = "Failed to stop scan for project {project_id}."
        GET_STATUS_FAILED = "Failed to get scan status for project {project}."
        