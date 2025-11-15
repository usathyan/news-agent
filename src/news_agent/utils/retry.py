import time
from typing import TypeVar, Callable
from news_agent.config.models import RetryConfig

T = TypeVar('T')


def retry_with_backoff(
    func: Callable[[], T],
    config: RetryConfig,
    retryable_exceptions: tuple = (ConnectionError, TimeoutError)
) -> T:
    """Execute function with exponential backoff retry logic"""
    last_exception = None

    for attempt in range(config.max_attempts):
        try:
            return func()
        except retryable_exceptions as e:
            last_exception = e

            if attempt < config.max_attempts - 1:
                # Calculate backoff delay
                delay = config.backoff_multiplier ** attempt
                time.sleep(delay)
            else:
                # Last attempt failed
                if config.graceful_degradation:
                    return None  # type: ignore
                else:
                    raise

    # This shouldn't be reached, but for type safety
    if not config.graceful_degradation and last_exception:
        raise last_exception
    return None  # type: ignore
