"""OpenAI provider implementation."""

import os
from typing import Any, Optional

from langchain_openai import ChatOpenAI

from robotframework_ai_assistant.providers.base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider."""

    def __init__(
        self,
        model_name: str = "gpt-4",
        temperature: float = 0.7,
        api_key: Optional[str] = None,
        **kwargs: Any,
    ):
        """Initialize OpenAI provider.

        Args:
            model_name: OpenAI model name (e.g., 'gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo').
            temperature: Temperature for generation.
            api_key: OpenAI API key. Defaults to OPENAI_API_KEY env var.
            **kwargs: Additional ChatOpenAI parameters.
        """
        super().__init__(model_name, temperature, api_key, **kwargs)

    @property
    def default_env_var(self) -> str:
        """Get the default environment variable name for API key."""
        return "OPENAI_API_KEY"

    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return "openai"

    def get_llm(self) -> ChatOpenAI:
        """Get or create the OpenAI LLM instance."""
        if self._llm is None:
            api_key = self.api_key or os.getenv(self.default_env_var)
            if not api_key:
                raise ValueError(
                    f"{self.provider_name} API key is required. "
                    f"Set {self.default_env_var} environment variable or pass api_key parameter."
                )

            self._llm = ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                api_key=api_key,
                **self.kwargs,
            )
        return self._llm
