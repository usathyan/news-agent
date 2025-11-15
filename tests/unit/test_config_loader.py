import tempfile
from pathlib import Path
import pytest
from news_agent.config.loader import load_config
from news_agent.config.models import Config


def test_load_config_from_toml():
    """Test loading configuration from TOML file"""
    config_content = """
[llm]
provider = "anthropic"
model = "claude-3-5-sonnet-20241022"
api_key_env = "ANTHROPIC_API_KEY"

[analysis]
depth = "medium"
top_n = 25
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write(config_content)
        config_path = Path(f.name)

    try:
        config = load_config(config_path)
        assert config.llm.provider == "anthropic"
        assert config.analysis.depth == "medium"
        assert config.analysis.top_n == 25
    finally:
        config_path.unlink()


def test_config_validation_fails_on_invalid_depth():
    """Test config validation catches invalid depth values"""
    config_content = """
[llm]
provider = "anthropic"
model = "claude-3-5-sonnet-20241022"
api_key_env = "ANTHROPIC_API_KEY"

[analysis]
depth = "invalid"
top_n = 25
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write(config_content)
        config_path = Path(f.name)

    try:
        with pytest.raises(ValueError):
            load_config(config_path)
    finally:
        config_path.unlink()
