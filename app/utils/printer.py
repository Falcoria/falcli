from typing import List, Type, Union
from pydantic import BaseModel

from rich import print as rprint

from app.schemas import IP


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
    from .printer import column_table
    column_table(headers, rows)


def info(message: str):
    rprint(f"[cyan]{message}[/cyan]")


def header(message: str):
    rprint(f"[bold]{message}[/bold]")


def success(message: str):
    rprint(f"[bright_green][+] [/bright_green]", end="")
    print(f"{message}")

def warning(message: str):
    rprint(f"[bright_yellow][!] [/bright_yellow]", end="")
    print(f"{message}")


def error(message: str):
    #rprint(f"[red]❌ {message}[/red]")
    rprint(f"[red][-] [/red]", end="")
    print(f"{message}")


def plain(message: str):
    print(message)


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
            column_table(headers, rows)
        else:
            print("No ports.")

        print()
        print()


def column_table_from_models(model_class: Type[BaseModel], items: List[BaseModel]):
    """Print aligned table from a list of Pydantic models."""
    headers = list(model_class.model_fields.keys())
    headers_upper = [h.upper() for h in headers]

    # Build rows from model data
    rows = [[getattr(item, field, "") for field in headers] for item in items]

    # Calculate column widths
    col_widths = [len(h) for h in headers_upper]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    row_format = "  ".join(["{:<" + str(width) + "}" for width in col_widths])

    # Print headers
    print("\033[2m" + row_format.format(*headers_upper) + "\033[0m")

    # Print rows
    for row in rows:
        print(row_format.format(*[str(cell) for cell in row]))