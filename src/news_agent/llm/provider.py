import os
from typing import Any
from litellm import completion
from news_agent.config.models import LLMConfig


class LLMProvider:
    """Wrapper for LiteLLM to support multiple LLM providers"""

    def __init__(self, config: LLMConfig):
        self.config = config
        self.model = config.model

        # Verify API key exists
        api_key = os.getenv(config.api_key_env)
        if not api_key:
            raise ValueError(
                f"API key not found in environment variable: {config.api_key_env}"
            )

        # Set API key for litellm
        os.environ[f"{config.provider.upper()}_API_KEY"] = api_key

    def complete(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any
    ) -> str:
        """Generate completion using configured LLM provider"""
        response = completion(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return response.choices[0].message.content

    def complete_json(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs: Any
    ) -> str:
        """Generate JSON completion"""
        return self.complete(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
            **kwargs
        )
