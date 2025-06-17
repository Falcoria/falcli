# app/config.py

from pathlib import Path
from pydantic import BaseModel, ValidationError

from app.utils.io_utils import save_dict_to_yaml, load_yaml_file
from app.utils.printer import Printer
from app.messages.errors import Errors
from app.core.profile.models import FalcoriaProfile


BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
PROFILE_DIR = DATA_DIR / "profiles"
ACTIVE_PROFILE_FILE = PROFILE_DIR / "active_profile.txt"


class Config(BaseModel):
    scanledger_base_url: str
    tasker_base_url: str
    token: str

    memory_file: Path = DATA_DIR / "memory.json"
    report_dir: Path = DATA_DIR / "reports"
    scan_config_dir: Path = DATA_DIR / "scan_configs"
    profile_dir: Path = PROFILE_DIR

    def save(self, profile_name: str):
        path = PROFILE_DIR / f"{profile_name}.yaml"
        save_dict_to_yaml(self.model_dump(), path)


def get_active_profile_name() -> str:
    if not ACTIVE_PROFILE_FILE.exists():
        ACTIVE_PROFILE_FILE.parent.mkdir(parents=True, exist_ok=True)
        ACTIVE_PROFILE_FILE.write_text("default")
    return ACTIVE_PROFILE_FILE.read_text().strip()


def load_config_safe() -> Config | None:
    try:
        profile_name = get_active_profile_name()
        path = PROFILE_DIR / f"{profile_name}.yaml"
        data = load_yaml_file(path)
        profile = FalcoriaProfile(**data)
        return Config(
            scanledger_base_url=profile.scanledger_base_url,
            tasker_base_url=profile.tasker_base_url,
            token=profile.token,
        )
    except (FileNotFoundError, ValidationError, Exception) as e:
        Printer.error(
            Errors.Config.MISSING_VALUES
            + f"\nCheck profile file: {path}\nDetails: {e}"
        )
        return None


config = load_config_safe()
