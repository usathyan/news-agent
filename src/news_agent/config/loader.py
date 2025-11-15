from pathlib import Path
import tomli
from pydantic import ValidationError
from news_agent.config.models import Config


def load_config(config_path: Path) -> Config:
    """Load and validate configuration from TOML file"""
    try:
        with open(config_path, 'rb') as f:
            config_dict = tomli.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Configuration file not found at {config_path}. "
            f"Please ensure the file exists and the path is correct."
        )
    except tomli.TOMLDecodeError as e:
        raise tomli.TOMLDecodeError(
            f"Invalid TOML syntax in {config_path}: {str(e)}"
        )

    try:
        return Config(**config_dict)
    except ValidationError as e:
        raise ValidationError.from_exception_data(
            title="Configuration validation failed",
            line_errors=[
                {
                    "type": "value_error",
                    "loc": ("config",),
                    "input": config_dict,
                    "ctx": {"error": f"Invalid configuration in {config_path}: {str(e)}"}
                }
            ]
        )
