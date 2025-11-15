import pytest
from news_agent.utils.retry import retry_with_backoff
from news_agent.config.models import RetryConfig


def test_retry_succeeds_on_first_attempt():
    """Test successful execution on first try"""
    config = RetryConfig(max_attempts=3, backoff_multiplier=2)

    call_count = 0

    def successful_func():
        nonlocal call_count
        call_count += 1
        return "success"

    result = retry_with_backoff(successful_func, config)
    assert result == "success"
    assert call_count == 1


def test_retry_succeeds_after_failures():
    """Test retry succeeds after initial failures"""
    config = RetryConfig(max_attempts=3, backoff_multiplier=1)

    call_count = 0

    def eventually_succeeds():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ConnectionError("Network error")
        return "success"

    result = retry_with_backoff(eventually_succeeds, config)
    assert result == "success"
    assert call_count == 3


def test_retry_fails_after_max_attempts():
    """Test retry gives up after max attempts"""
    config = RetryConfig(max_attempts=3, backoff_multiplier=1, graceful_degradation=False)

    def always_fails():
        raise ValueError("Always fails")

    with pytest.raises(ValueError):
        retry_with_backoff(always_fails, config)
