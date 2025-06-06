# app/messages/info.py

class HTTP:
    SUCCESS = "Request completed successfully."

class Project:
    CREATED = "Project '{name}' created successfully ({id})."
    DELETED = "Project '{project_id}' deleted."
    FETCHED = "Retrieved project '{name}'."
    CREATED_SIMPLE = "Project created successfully."
    DELETED_SIMPLE = "Project deleted successfully."
    PROJECTS_AVAILABLE = "Available projects:"
    NO_PROJECTS_FOUND = "No projects found."
    DETAILS = "Project details:"
    #DETAILS = "PROJECT DETAILS"

    FIRST_PROJECT_SAVED = "This project has been saved as the default for future commands."
    EXISTING_PROJECT = "A project is already saved in memory: {project_name},  ({project_id})"
    CONFIRM_REPLACE = "Do you want to replace it with the new project?"
    MEMORY_UPDATED = "Memory updated with the new project."
    MEMORY_NOT_UPDATED = "The new project was NOT saved in memory."


class IPs:
    """Class for group IPs-related messages."""
    CREATED = "Added {count} IP(s) to project '{project}'."
    DELETED = "Deleted all IPs from project '{project}'."
    FETCHED = "Retrieved IPs for project '{project}'."
    IMPORTED = "Imported IPs report into project '{project}'. Result: {result}."
    DOWNLOADED = "Downloaded IPs report for project '{project}'."
    NO_IPS_FOUND = "No IPs found in project '{project}'"
    NO_NEW_IPS = "No new IPs added in project '{project}'"


class IP:
    """Class for single IP-related messages."""
    FETCHED = "IP '{ip}' found in project '{project}'."
    NOT_FOUND = "IP '{ip}' not found in project '{project}'."
    ADDED = "IP '{ip}' added to project '{project}'."
    DELETED = "IP '{ip}' deleted from project '{project}'."
    IMPORTED = "Imported IPs report into project '{project}'."


class Other:
    FILE_SAVED = "File saved to '{path}'."
    OPEN_PORTS_CMD = "Phase 1 — Open Ports Command"
    SERVICE_CMD = "Phase 2 — Service Command. Runs once the open ports phase is complete."
    OPEN_PORTS_OPTS_HEADER = "[Open Ports Phase]"
    SERVICE_OPTS_HEADER = "[Service Discovery Phase]"



class Scan:
    STARTED = "Scan started successfully for project {project}"
    STOPPED = "Scan stopped for project {project}"
    COMPLETED = "Scan completed for project {project}"
    STATUS = "Scan status for project {project}: {status}"
    TARGETS_SENT = "Scan targets sent for project {project}."
