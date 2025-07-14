from typing import List, Type, Union

from datetime import datetime, timezone, timedelta

from rich import print as rprint
from pydantic import BaseModel

from app.core.ips.models import IP
from app.core.scan.models import ScanStartSummary, RunNmapRequest
from app.utils.io_utils import get_display_path
from app.core.profile.models import FalcoriaProject

from falcoria_common.schemas.nmap import NmapTaskSummary


class Printer:
    @staticmethod
    def header(message: str):
        rprint(f"[bold]{message}[/bold]")

    @staticmethod
    def success(message: str):
        rprint(f"[bright_green][+] [/bright_green]", end="")
        print(f"{message}")

    @staticmethod
    def warning(message: str):
        rprint(f"[bright_yellow][!] [/bright_yellow]", end="")
        print(f"{message}")
    
    @staticmethod
    def error(message: str):
        rprint(f"[red][-] [/red]", end="")
        print(f"{message}")

    @staticmethod
    def plain(message: str):
        print(message)

    @staticmethod
    def column_table(headers: list, rows: list):
        """Print aligned table like 'docker ps'."""
        headers_upper = [h.upper() for h in headers]

        col_widths = [len(h) for h in headers_upper]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))

        row_format = "  ".join(["{:<" + str(width) + "}" for width in col_widths])

        # Print headers in grey (\033[2m ... \033[0m)
        print("\033[2m" + row_format.format(*headers_upper) + "\033[0m")

        for row in rows:
            print(row_format.format(*[str(cell) for cell in row]))

    @staticmethod
    def print_model_table(model: Type[BaseModel], data: List[dict]) -> None:
        """
        Parses and prints a table of items from raw dictionaries using a given Pydantic model.
        """
        if not data:
            print("(No data)")
            return

        # Parse raw data into models
        objects = [model.model_validate(obj) for obj in data]

        # Build headers from model fields
        headers = [field.upper() for field in model.model_fields.keys()]

        # Build rows
        rows = []
        for obj in objects:
            row = []
            for field in model.model_fields.keys():
                value = getattr(obj, field)
                if isinstance(value, list):
                    row.append(", ".join(map(str, value)))
                elif value is None:
                    row.append("-")
                else:
                    row.append(str(value))
            rows.append(tuple(row))

        # Use existing printer
        Printer.column_table(headers, rows)

    @staticmethod
    def key_value_table(data: Union[dict, BaseModel], indent: int = 2):
        """Print key-value pairs with aligned columns. Supports both dict and Pydantic models."""
        if isinstance(data, BaseModel):
            data = data.model_dump()

        longest_key = max(len(str(key)) for key in data.keys())
        padding = " " * indent

        for key, value in data.items():
            if isinstance(value, list):
                value = ", ".join(map(str, value))
            elif value is None:
                value = "-"
            spaces = " " * (longest_key - len(str(key)) + 2)
            print(f"{padding}\033[2m{key}\033[0m{spaces}: {value}")

    @staticmethod
    def grouped_ip_table(ips: list[IP]):
        """Print IPs with ports grouped under each IP (using validated models)."""
        for ip in ips:
            rprint(f"[bold]IP:[/bold] {ip.ip}")
            print(f"Status   : {ip.status or '-'}")
            print(f"OS       : {ip.os or '-'}")
            print(f"Hostnames: {', '.join(ip.hostnames or []) or '-'}\n")

            if ip.ports:
                headers = ["PORT", "PROTO", "STATE", "SERVICE", "BANNER"]
                rows = [
                    (
                        port.number,
                        port.protocol.value,
                        port.state.value,
                        port.service or "-",
                        port.banner or "-"
                    )
                    for port in ip.ports
                ]
                Printer.column_table(headers, rows)
            else:
                print("No ports.")

            print()
            print()

    @staticmethod
    def scan_summary_table(summary: ScanStartSummary):
        """Print condensed scan summary with grouped reasons."""
        Printer.header("Scan Summary")

        ref = summary.refused

        total_skipped = ref.already_in_scanledger + ref.already_in_queue
        total_rejected = ref.forbidden + ref.private_ip + ref.unresolvable + ref.other

        data = {
            "Targets provided"       : summary.provided,
            "Duplicates removed"     : summary.duplicates_removed,
            "Skipped (already known)": total_skipped,
            "Rejected"               : total_rejected,
            "Accepted and sent"      : summary.sent_to_scan,
        }

        Printer.key_value_table(data)

        if total_skipped:
            Printer.plain("  Skipped reasons:")
            skip_data = {
                "In ScanLedger"    : ref.already_in_scanledger,
                "Already in queue" : ref.already_in_queue,
            }
            Printer.key_value_table(skip_data, indent=4)

        if total_rejected:
            Printer.plain("  Rejected reasons:")
            reject_data = {
                "Private IP"       : ref.private_ip,
                "Unresolvable"     : ref.unresolvable,
                "Forbidden"        : ref.forbidden,
                "Other"            : ref.other,
            }
            Printer.key_value_table(reject_data, indent=4)


    @staticmethod
    def task_summary_table(summary: NmapTaskSummary):
        """Print project scan task status summary."""
        Printer.header("Scan Status Summary")

        data = {
            "Tasks total"  : summary.active_or_queued,
            "Tasks running": summary.running,
            "Tasks queued" : summary.active_or_queued - summary.running,
        }
        Printer.key_value_table(data)

        if summary.running_targets:
            print()
            Printer.plain("Running Targets:")
            headers = ["IP", "HOSTNAMES", "WORKER", "STARTED_AT (UTC)", "ELAPSED"]
            rows = []
            now = datetime.now(timezone.utc)

            for target in summary.running_targets:
                started_at = datetime.fromtimestamp(target.started_at, tz=timezone.utc)
                elapsed = now - started_at
                # Format elapsed as HH:MM:SS
                elapsed_str = str(timedelta(seconds=int(elapsed.total_seconds())))
                rows.append((
                    target.ip,
                    ", ".join(target.hostnames),
                    target.worker,
                    started_at.strftime("%Y-%m-%d %H:%M:%S"),
                    elapsed_str,
                ))

            Printer.column_table(headers, rows)
        else:
            Printer.plain("  No running targets.")

    @staticmethod
    def scan_start_header(scan_request: RunNmapRequest, project_id: str, scan_config_path: str):
        #Printer.header(f"Scan initiated for project {project_id}\n")
        print()
        Printer.header("Scan Settings")

        open_ports_flags = " ".join(scan_request.open_ports_opts.to_nmap_args())
        service_flags = (
            " ".join(scan_request.service_opts.to_nmap_args())
            if scan_request.include_services else "not performed"
        )

        data = {
            "Import mode"     : scan_request.mode.value,
            "Nmap (open ports)" : open_ports_flags,
            "Nmap (services)"   : service_flags,
            "Scan config"     : get_display_path(scan_config_path),
        }

        Printer.key_value_table(data)
        print()
    
    @staticmethod
    def print_active_project(project: FalcoriaProject):
        #Printer.plain(f"[Active Project] {project.name} ({project.project_id})")
        Printer.plain(f"[Active Project]: '{project.name}' ({project.project_id})")