import yaml
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict, YamlConfigSettingsSource
from pydantic import BaseModel, Field


from app.messages import errors
from app.utils import printer


class UserConfig(BaseModel):
    backend_base_url: str
    tasker_base_url: str
    token: str

    def save(self):
        config_file = Path("data/user_config.yaml")
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with config_file.open("w") as f:
            yaml.safe_dump(self.model_dump(), f)


class Config(BaseSettings):
    backend_base_url: str
    tasker_base_url: str
    token: str

    memory_file: Path = Path("data/memory.json")
    report_dir: Path = Path("scan_reports")

    model_config = SettingsConfigDict(
        env_prefix="",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        return (
            init_settings,
            YamlConfigSettingsSource(settings_cls, Path("data/user_config.yaml")),
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )

    def save(self):
        import yaml

        config_data = self.model_dump()

        # Convert Paths to strings
        for key, value in config_data.items():
            if isinstance(value, Path):
                config_data[key] = str(value)

        config_file = Path("data/user_config.yaml")
        config_file.parent.mkdir(parents=True, exist_ok=True)

        with config_file.open("w") as f:
            yaml.safe_dump(config_data, f)

try:
    config = Config()
except Exception:
    printer.error(errors.Config.MISSING_VALUES)
    raise SystemExit(1)
