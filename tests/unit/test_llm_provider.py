import os
import pytest
from unittest.mock import Mock, patch
from news_agent.llm.provider import LLMProvider, SUPPORTED_PROVIDERS
from news_agent.config.models import LLMConfig
from litellm.exceptions import (
    AuthenticationError,
    RateLimitError,
    Timeout,
    APIError,
    BadRequestError
)


@pytest.fixture
def llm_config():
    return LLMConfig(
        provider="anthropic",
        model="claude-3-5-sonnet-20241022",
        api_key_env="ANTHROPIC_API_KEY"
    )


@pytest.fixture
def mock_response():
    """Create a mock LiteLLM response"""
    response = Mock()
    response.choices = [Mock()]
    response.choices[0].message.content = "Test response"
    response.usage = Mock()
    response.usage.prompt_tokens = 10
    response.usage.completion_tokens = 20
    response.usage.total_tokens = 30
    return response


def test_llm_provider_initialization(llm_config):
    """Test LLM provider initializes correctly"""
    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    provider = LLMProvider(llm_config)
    assert provider.model == "claude-3-5-sonnet-20241022"
    assert provider._api_key == "test-key"
    assert provider.config == llm_config


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


def test_llm_provider_unsupported_provider():
    """Test provider raises error for unsupported provider"""
    config = LLMConfig(
        provider="unsupported_provider",
        model="some-model",
        api_key_env="SOME_API_KEY"
    )
    os.environ["SOME_API_KEY"] = "test-key"

    with pytest.raises(ValueError, match="Unsupported provider"):
        LLMProvider(config)


def test_supported_providers_constant():
    """Test that SUPPORTED_PROVIDERS contains expected providers"""
    assert "anthropic" in SUPPORTED_PROVIDERS
    assert "openai" in SUPPORTED_PROVIDERS
    assert "azure" in SUPPORTED_PROVIDERS
    assert "cohere" in SUPPORTED_PROVIDERS
    assert "bedrock" in SUPPORTED_PROVIDERS


@patch('news_agent.llm.provider.completion')
def test_complete_success(mock_completion, llm_config, mock_response):
    """Test successful completion call"""
    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    mock_completion.return_value = mock_response

    provider = LLMProvider(llm_config)
    messages = [{"role": "user", "content": "Hello"}]

    result = provider.complete(messages, temperature=0.5, max_tokens=512)

    assert result == "Test response"
    mock_completion.assert_called_once_with(
        model="claude-3-5-sonnet-20241022",
        messages=messages,
        temperature=0.5,
        max_tokens=512,
        api_key="test-key"
    )


@patch('news_agent.llm.provider.completion')
def test_complete_json_success(mock_completion, llm_config, mock_response):
    """Test successful JSON completion call"""
    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    mock_response.choices[0].message.content = '{"key": "value"}'
    mock_completion.return_value = mock_response

    provider = LLMProvider(llm_config)
    messages = [{"role": "user", "content": "Generate JSON"}]

    result = provider.complete_json(messages, temperature=0.3, max_tokens=1024)

    assert result == '{"key": "value"}'
    mock_completion.assert_called_once()
    call_kwargs = mock_completion.call_args[1]
    assert call_kwargs["response_format"] == {"type": "json_object"}
    assert call_kwargs["temperature"] == 0.3
    assert call_kwargs["max_tokens"] == 1024


@patch('news_agent.llm.provider.completion')
def test_complete_empty_choices_error(mock_completion, llm_config):
    """Test error when API returns empty choices"""
    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    mock_response = Mock()
    mock_response.choices = []
    mock_completion.return_value = mock_response

    provider = LLMProvider(llm_config)
    messages = [{"role": "user", "content": "Hello"}]

    with pytest.raises(ValueError, match="API returned empty choices list"):
        provider.complete(messages)


@patch('news_agent.llm.provider.completion')
def test_complete_none_content_error(mock_completion, llm_config):
    """Test error when API returns None content"""
    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = None
    mock_completion.return_value = mock_response

    provider = LLMProvider(llm_config)
    messages = [{"role": "user", "content": "Hello"}]

    with pytest.raises(ValueError, match="API returned None content in message"):
        provider.complete(messages)


@patch('news_agent.llm.provider.completion')
def test_complete_authentication_error(mock_completion, llm_config):
    """Test handling of authentication error"""
    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    mock_completion.side_effect = AuthenticationError(
        message="Invalid API key",
        llm_provider="anthropic",
        model="claude-3-5-sonnet-20241022"
    )

    provider = LLMProvider(llm_config)
    messages = [{"role": "user", "content": "Hello"}]

    with pytest.raises(ValueError, match="Authentication failed. Please check your API key"):
        provider.complete(messages)


@patch('news_agent.llm.provider.completion')
def test_complete_rate_limit_error(mock_completion, llm_config):
    """Test handling of rate limit error"""
    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    mock_completion.side_effect = RateLimitError(
        message="Rate limit exceeded",
        llm_provider="anthropic",
        model="claude-3-5-sonnet-20241022"
    )

    provider = LLMProvider(llm_config)
    messages = [{"role": "user", "content": "Hello"}]

    with pytest.raises(ValueError, match="Rate limit exceeded.*Please try again later"):
        provider.complete(messages)


@patch('news_agent.llm.provider.completion')
def test_complete_timeout_error(mock_completion, llm_config):
    """Test handling of timeout error"""
    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    mock_completion.side_effect = Timeout(
        message="Request timed out",
        model="claude-3-5-sonnet-20241022",
        llm_provider="anthropic"
    )

    provider = LLMProvider(llm_config)
    messages = [{"role": "user", "content": "Hello"}]

    with pytest.raises(ValueError, match="Request to.*timed out. Please try again"):
        provider.complete(messages)


@patch('news_agent.llm.provider.completion')
def test_complete_bad_request_error(mock_completion, llm_config):
    """Test handling of bad request error"""
    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    mock_completion.side_effect = BadRequestError(
        message="Invalid request format",
        model="claude-3-5-sonnet-20241022",
        llm_provider="anthropic"
    )

    provider = LLMProvider(llm_config)
    messages = [{"role": "user", "content": "Hello"}]

    with pytest.raises(ValueError, match="Invalid request to"):
        provider.complete(messages)


@patch('news_agent.llm.provider.completion')
def test_complete_api_error(mock_completion, llm_config):
    """Test handling of general API error"""
    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    mock_completion.side_effect = APIError(
        status_code=500,
        message="General API error",
        llm_provider="anthropic",
        model="claude-3-5-sonnet-20241022"
    )

    provider = LLMProvider(llm_config)
    messages = [{"role": "user", "content": "Hello"}]

    with pytest.raises(ValueError, match="API error from"):
        provider.complete(messages)


@patch('news_agent.llm.provider.completion')
def test_api_key_passed_explicitly(mock_completion, llm_config, mock_response):
    """Test that API key is passed explicitly to completion() call"""
    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    mock_completion.return_value = mock_response

    provider = LLMProvider(llm_config)
    messages = [{"role": "user", "content": "Hello"}]

    provider.complete(messages)

    # Verify api_key is passed explicitly, not via global environment
    call_kwargs = mock_completion.call_args[1]
    assert "api_key" in call_kwargs
    assert call_kwargs["api_key"] == "test-key"
