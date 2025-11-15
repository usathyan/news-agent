import tempfile
from pathlib import Path
import pytest
import tomli
from pydantic import ValidationError
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


def test_file_not_found_error():
    """Test that FileNotFoundError is raised with helpful message"""
    non_existent_path = Path("/tmp/non_existent_config_file_12345.toml")

    with pytest.raises(FileNotFoundError) as exc_info:
        load_config(non_existent_path)

    assert "Configuration file not found" in str(exc_info.value)
    assert str(non_existent_path) in str(exc_info.value)


def test_invalid_toml_syntax():
    """Test that TOMLDecodeError is raised with helpful message for invalid TOML"""
    invalid_toml = """
[llm]
provider = "anthropic
model = "claude-3-5-sonnet-20241022"
api_key_env = "ANTHROPIC_API_KEY"
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write(invalid_toml)
        config_path = Path(f.name)

    try:
        with pytest.raises(tomli.TOMLDecodeError) as exc_info:
            load_config(config_path)

        assert "Invalid TOML syntax" in str(exc_info.value)
    finally:
        config_path.unlink()


def test_missing_required_fields():
    """Test that ValidationError is raised when required fields are missing"""
    # Missing required llm section
    incomplete_config = """
[analysis]
depth = "medium"
top_n = 25
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write(incomplete_config)
        config_path = Path(f.name)

    try:
        with pytest.raises(ValidationError):
            load_config(config_path)
    finally:
        config_path.unlink()


def test_weight_sum_validation():
    """Test that weights must sum to 1.0"""
    invalid_weights = """
[llm]
provider = "anthropic"
model = "claude-3-5-sonnet-20241022"
api_key_env = "ANTHROPIC_API_KEY"

[ranking.weights]
relevance = 0.5
popularity = 0.3
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write(invalid_weights)
        config_path = Path(f.name)

    try:
        with pytest.raises(ValueError) as exc_info:
            load_config(config_path)

        assert "Weights must sum to 1.0" in str(exc_info.value)
    finally:
        config_path.unlink()


def test_top_n_boundary_value_1():
    """Test that top_n accepts boundary value of 1"""
    config_content = """
[llm]
provider = "anthropic"
model = "claude-3-5-sonnet-20241022"
api_key_env = "ANTHROPIC_API_KEY"

[analysis]
top_n = 1
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write(config_content)
        config_path = Path(f.name)

    try:
        config = load_config(config_path)
        assert config.analysis.top_n == 1
    finally:
        config_path.unlink()


def test_top_n_boundary_value_100():
    """Test that top_n accepts boundary value of 100"""
    config_content = """
[llm]
provider = "anthropic"
model = "claude-3-5-sonnet-20241022"
api_key_env = "ANTHROPIC_API_KEY"

[analysis]
top_n = 100
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write(config_content)
        config_path = Path(f.name)

    try:
        config = load_config(config_path)
        assert config.analysis.top_n == 100
    finally:
        config_path.unlink()


def test_top_n_boundary_value_0_invalid():
    """Test that top_n rejects value of 0"""
    config_content = """
[llm]
provider = "anthropic"
model = "claude-3-5-sonnet-20241022"
api_key_env = "ANTHROPIC_API_KEY"

[analysis]
top_n = 0
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write(config_content)
        config_path = Path(f.name)

    try:
        with pytest.raises(ValidationError):
            load_config(config_path)
    finally:
        config_path.unlink()


def test_top_n_boundary_value_101_invalid():
    """Test that top_n rejects value of 101"""
    config_content = """
[llm]
provider = "anthropic"
model = "claude-3-5-sonnet-20241022"
api_key_env = "ANTHROPIC_API_KEY"

[analysis]
top_n = 101
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write(config_content)
        config_path = Path(f.name)

    try:
        with pytest.raises(ValidationError):
            load_config(config_path)
    finally:
        config_path.unlink()
