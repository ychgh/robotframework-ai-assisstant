"""DeepSeek provider implementation."""

import os
from typing import Any, Optional

from robotframework_ai_assistant.providers.base import BaseLLMProvider


class DeepSeekProvider(BaseLLMProvider):
    """DeepSeek LLM provider.

    DeepSeek provides OpenAI-compatible API endpoints.
    """

    def __init__(
        self,
        model_name: str = "deepseek-chat",
        temperature: float = 0.7,
        api_key: Optional[str] = None,
        base_url: str = "https://api.deepseek.com/v1",
        **kwargs: Any,
    ):
        """Initialize DeepSeek provider.

        Args:
            model_name: DeepSeek model name (e.g., 'deepseek-chat', 'deepseek-coder').
            temperature: Temperature for generation.
            api_key: DeepSeek API key. Defaults to DEEPSEEK_API_KEY env var.
            base_url: DeepSeek API base URL. Defaults to 'https://api.deepseek.com/v1'.
            **kwargs: Additional ChatOpenAI parameters.
        """
        super().__init__(model_name, temperature, api_key, **kwargs)
        self.base_url = base_url

    @property
    def default_env_var(self) -> str:
        """Get the default environment variable name for API key."""
        return "DEEPSEEK_API_KEY"

    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return "deepseek"

    def get_llm(self) -> Any:
        """Get or create the DeepSeek LLM instance."""
        if self._llm is None:
            try:
                from langchain_openai import ChatOpenAI
            except ImportError as e:
                raise ImportError(
                    "langchain-openai is required for DeepSeek provider. "
                    "It should already be installed."
                ) from e

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
                base_url=self.base_url,
                **self.kwargs,
            )
        return self._llm
