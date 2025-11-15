import os
import pytest
from news_agent.llm.provider import LLMProvider
from news_agent.config.models import LLMConfig


@pytest.fixture
def llm_config():
    return LLMConfig(
        provider="anthropic",
        model="claude-3-5-sonnet-20241022",
        api_key_env="ANTHROPIC_API_KEY"
    )


def test_llm_provider_initialization(llm_config):
    """Test LLM provider initializes correctly"""
    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    provider = LLMProvider(llm_config)
    assert provider.model == "claude-3-5-sonnet-20241022"


def test_llm_provider_missing_api_key():
    """Test provider raises error when API key missing"""
    config = LLMConfig(
        provider="anthropic",
        model="claude-3-5-sonnet-20241022",
        api_key_env="MISSING_KEY"
    )
    if "MISSING_KEY" in os.environ:
        del os.environ["MISSING_KEY"]

    with pytest.raises(ValueError, match="API key not found"):
        LLMProvider(config)
