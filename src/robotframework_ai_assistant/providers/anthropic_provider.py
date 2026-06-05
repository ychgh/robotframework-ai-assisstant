"""Anthropic (Claude) provider implementation."""

import os
from typing import Any, Optional

from robotframework_ai_assistant.providers.base import BaseLLMProvider


class AnthropicProvider(BaseLLMProvider):
    """Anthropic (Claude) LLM provider."""

    def __init__(
        self,
        model_name: str = "claude-3-opus-20240229",
        temperature: float = 0.7,
        api_key: Optional[str] = None,
        **kwargs: Any,
    ):
        """Initialize Anthropic provider.

        Args:
            model_name: Anthropic model name (e.g., 'claude-3-opus-20240229', 'claude-3-sonnet-20240229').
            temperature: Temperature for generation.
            api_key: Anthropic API key. Defaults to ANTHROPIC_API_KEY env var.
            **kwargs: Additional ChatAnthropic parameters.
        """
        super().__init__(model_name, temperature, api_key, **kwargs)

    @property
    def default_env_var(self) -> str:
        """Get the default environment variable name for API key."""
        return "ANTHROPIC_API_KEY"

    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return "anthropic"

    def get_llm(self) -> Any:
        """Get or create the Anthropic LLM instance."""
        if self._llm is None:
            try:
                from langchain_anthropic import ChatAnthropic
            except ImportError as e:
                raise ImportError(
                    "langchain-anthropic is required for Anthropic provider. "
                    "Install it with: pip install langchain-anthropic"
                ) from e

            api_key = self.api_key or os.getenv(self.default_env_var)
            if not api_key:
                raise ValueError(
                    f"{self.provider_name} API key is required. "
                    f"Set {self.default_env_var} environment variable or pass api_key parameter."
                )

            self._llm = ChatAnthropic(
                model=self.model_name,
                temperature=self.temperature,
                anthropic_api_key=api_key,
                **self.kwargs,
            )
        return self._llm
