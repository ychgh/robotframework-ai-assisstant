"""Google (Gemini) provider implementation."""

import os
from typing import Any, Optional

from robotframework_ai_assistant.providers.base import BaseLLMProvider


class GoogleProvider(BaseLLMProvider):
    """Google (Gemini) LLM provider."""

    def __init__(
        self,
        model_name: str = "gemini-pro",
        temperature: float = 0.7,
        api_key: Optional[str] = None,
        **kwargs: Any,
    ):
        """Initialize Google provider.

        Args:
            model_name: Google model name (e.g., 'gemini-pro', 'gemini-pro-vision').
            temperature: Temperature for generation.
            api_key: Google API key. Defaults to GOOGLE_API_KEY env var.
            **kwargs: Additional ChatGoogleGenerativeAI parameters.
        """
        super().__init__(model_name, temperature, api_key, **kwargs)

    @property
    def default_env_var(self) -> str:
        """Get the default environment variable name for API key."""
        return "GOOGLE_API_KEY"

    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return "google"

    def get_llm(self) -> Any:
        """Get or create the Google LLM instance."""
        if self._llm is None:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
            except ImportError as e:
                raise ImportError(
                    "langchain-google-genai is required for Google provider. "
                    "Install it with: pip install langchain-google-genai"
                ) from e

            api_key = self.api_key or os.getenv(self.default_env_var)
            if not api_key:
                raise ValueError(
                    f"{self.provider_name} API key is required. "
                    f"Set {self.default_env_var} environment variable or pass api_key parameter."
                )

            self._llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                temperature=self.temperature,
                google_api_key=api_key,
                **self.kwargs,
            )
        return self._llm
