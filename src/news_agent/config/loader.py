from pathlib import Path
import tomli
from news_agent.config.models import Config


def load_config(config_path: Path) -> Config:
    """Load and validate configuration from TOML file"""
    with open(config_path, 'rb') as f:
        config_dict = tomli.load(f)

    return Config(**config_dict)
