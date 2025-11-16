import os
import logging
from typing import Any, List, Dict
import litellm
from litellm import completion
from litellm.exceptions import (
    AuthenticationError,
    RateLimitError,
    Timeout,
    APIError,
    BadRequestError
)
from news_agent.config.models import LLMConfig

# Configure logger
logger = logging.getLogger(__name__)

# Supported LLM providers
SUPPORTED_PROVIDERS = {"anthropic", "openai", "azure", "cohere", "bedrock", "openrouter", "ollama"}


class LLMProvider:
    """Wrapper for LiteLLM to support multiple LLM providers"""

    def __init__(self, config: LLMConfig):
        self.config = config
        self.model = config.model

        # Validate provider
        if config.provider.lower() not in SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Unsupported provider: {config.provider}. "
                f"Supported providers: {', '.join(sorted(SUPPORTED_PROVIDERS))}"
            )

        # Verify API key exists and store it as instance variable
        api_key = os.getenv(config.api_key_env)
        if not api_key:
            raise ValueError(
                f"API key not found in environment variable: {config.api_key_env}"
            )

        # Store API key in instance variable instead of global environment
        self._api_key = api_key

        # Configure LangSmith telemetry if API key is available
        langsmith_key = os.getenv("LANGSMITH_API_KEY")
        if langsmith_key:
            litellm.success_callback = ["langsmith"]
            logger.info("LangSmith telemetry enabled")

        logger.info(f"Initialized LLM provider: {config.provider} with model: {self.model}")

    def complete(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any
    ) -> str:
        """Generate completion using configured LLM provider"""
        logger.debug(f"Generating completion with model: {self.model}, temperature: {temperature}, max_tokens: {max_tokens}")

        try:
            response = completion(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=self._api_key,
                **kwargs
            )

            # Validate response
            if not response.choices:
                raise ValueError("API returned empty choices list")

            if response.choices[0].message.content is None:
                raise ValueError("API returned None content in message")

            # Log usage information
            if hasattr(response, 'usage') and response.usage:
                logger.info(
                    f"Completion successful - Tokens used: "
                    f"prompt={response.usage.prompt_tokens}, "
                    f"completion={response.usage.completion_tokens}, "
                    f"total={response.usage.total_tokens}"
                )

            return response.choices[0].message.content

        except AuthenticationError as e:
            logger.error(f"Authentication failed: {e}")
            raise ValueError(
                f"Authentication failed. Please check your API key for {self.config.provider}"
            ) from e
        except RateLimitError as e:
            logger.error(f"Rate limit exceeded: {e}")
            raise ValueError(
                f"Rate limit exceeded for {self.config.provider}. Please try again later."
            ) from e
        except Timeout as e:
            logger.error(f"Request timeout: {e}")
            raise ValueError(
                f"Request to {self.config.provider} timed out. Please try again."
            ) from e
        except BadRequestError as e:
            logger.error(f"Bad request: {e}")
            raise ValueError(
                f"Invalid request to {self.config.provider}: {str(e)}"
            ) from e
        except APIError as e:
            logger.error(f"API error: {e}")
            raise ValueError(
                f"API error from {self.config.provider}: {str(e)}"
            ) from e

    def complete_json(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs: Any
    ) -> str:
        """Generate JSON completion"""
        logger.debug("Generating JSON completion")
        return self.complete(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
            **kwargs
        )
