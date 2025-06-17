import yaml
from pathlib import Path

def save_dict_to_yaml(data: dict, path: Path):
    # Convert Paths to strings
    serializable_data = {
        k: str(v) if isinstance(v, Path) else v
        for k, v in data.items()
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        yaml.safe_dump(serializable_data, f)


def load_yaml_file(path: Path) -> dict:
    with path.open() as f:
        return yaml.safe_load(f)


def load_lines_from_file(file_path: Path) -> list[str]:
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    with file_path.open("r") as f:
        return [line.strip() for line in f if line.strip()]
