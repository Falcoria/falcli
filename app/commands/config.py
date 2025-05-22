import typer
from app.config import config, Config, UserConfig
from app.utils import printer

config_app = typer.Typer(no_args_is_help=True)

@config_app.command("list")
def list_config():
    """List current configuration (user-editable values)."""

    user_data = {key: getattr(config, key) for key in UserConfig.model_fields}
    printer.key_value_table(user_data)
    print()


@config_app.command("set")
def set_config(key: str, value: str):
    """Set a configuration value."""
    if key not in UserConfig.model_fields:
        printer.error(f"Invalid configuration key: {key}")
        raise typer.Exit(code=1)

    # Create a new UserConfig with current values and override the key
    current_data = {field: getattr(config, field) for field in UserConfig.model_fields}
    current_data[key] = value
    new_user_config = UserConfig(**current_data)

    # Save the updated config
    new_user_config.save()
    printer.success(f"Configuration '{key}' updated to: {value}")



@config_app.command("test")
def test_config():
    """Test ScanLedger and Tasker connectivity."""
    import requests

    try:
        response = requests.get(config.backend_base_url, timeout=5)
        if response.ok:
            printer.success(f"ScanLedger OK: {config.backend_base_url}")
        else:
            printer.warning(f"ScanLedger responded but with error: {response.status_code}")
    except Exception as e:
        printer.error(f"Cannot connect to ScanLedger: {e}")

    try:
        response = requests.get(config.tasker_base_url, timeout=5)
        if response.ok:
            printer.success(f"Tasker OK: {config.tasker_base_url}")
        else:
            printer.warning(f"Tasker responded but with error: {response.status_code}")
    except Exception as e:
        printer.error(f"Cannot connect to Tasker: {e}")
