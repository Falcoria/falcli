
class Info:
    class General:
        ABORTED = "Aborted."
        SAVED_TO = "Saved to: {path}"

    class Profile:
        CREATED = "Profile '{name}' created."
        DELETED = "Profile '{name}' deleted."
        ACTIVE_SET = "Active profile set to: {name}."
        DEFAULT_PROJECT_SET = "Set default project '{project_id}' in active profile '{profile_name}'."
        AVAILABLE_PROFILES = "Available profiles:"
        ACTIVE_PROFILE = "Active profile: {name}."
        FIELD_UPDATED = "Field '{field}' updated in profile '{name}'."
        PROFILE_VALID = "Profile '{name}' is valid."
        PROFILE_HEADER = "Profile: {name}\n"

    class Project:
        CREATED = "Project '{name}' created successfully ({id})."
        DELETED = "Project '{project_id}' deleted."
        FETCHED = "Retrieved project '{name}'."
        NO_PROJECTS_FOUND = "No projects found."
        DETAILS = "Project details:"
        FIRST_PROJECT_SAVED = "First project saved."
        EXISTING_PROJECT = "Existing saved project: '{project_name}' ({project_id})."
        CONFIRM_REPLACE = "Do you want to replace the saved project?"
        MEMORY_UPDATED = "Saved project updated."
        MEMORY_NOT_UPDATED = "Saved project not updated."
        PROJECT_SET = "Default project set to '{project_id}'."
    
    class IPs:
        FETCHED = "Fetched IPs for project '{project}'."
        CREATED = "Added {count} IP(s) to project '{project}'."
        IMPORTED = "Imported IPs to project '{project}': {result}."
        NO_NEW_IPS = "No new IPs imported for project '{project}'."
        DOWNLOADED = "Downloaded IPs report for project '{project}'."
        DELETED = "Deleted IP(s) for project '{project}'."
        NO_IPS_FOUND = "No IPs found in project '{project_name}' ({project_id})."
    
    class Worker:
        FETCHED_WORKER_IPS = "Fetched external IP addresses of active workers."
    
    class Scan:
        TARGETS_SENT = "Scan initiated for project: '{project_name}' ({project_id})."
        STOP_SUCCESS = "Scan stopped successfully for project: '{project_name}' ({project_id})."
        STATUS_FETCHED = "Scan status for project '{project_name}' ({project_id}) fetched successfully."
        NO_TASKS = "No tasks found for project '{project_name}' ({project_id})."
        REVOKED_COUNT = "Revoked {count} tasks."
        PRINT_CONFIG = "Using scan configuration: {config}"