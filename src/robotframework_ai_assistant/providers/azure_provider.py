"""Azure OpenAI provider implementation."""

import os
from typing import Any, Optional

from robotframework_ai_assistant.providers.base import BaseLLMProvider


class AzureOpenAIProvider(BaseLLMProvider):
    """Azure OpenAI LLM provider."""

    def __init__(
        self,
        model_name: str,
        temperature: float = 0.7,
        api_key: Optional[str] = None,
        azure_endpoint: Optional[str] = None,
        api_version: str = "2024-02-01",
        **kwargs: Any,
    ):
        """Initialize Azure OpenAI provider.

        Args:
            model_name: Azure OpenAI deployment name.
            temperature: Temperature for generation.
            api_key: Azure OpenAI API key. Defaults to AZURE_OPENAI_API_KEY env var.
            azure_endpoint: Azure OpenAI endpoint. Defaults to AZURE_OPENAI_ENDPOINT env var.
            api_version: Azure OpenAI API version.
            **kwargs: Additional AzureChatOpenAI parameters.
        """
        super().__init__(model_name, temperature, api_key, **kwargs)
        self.azure_endpoint = azure_endpoint
        self.api_version = api_version

    @property
    def default_env_var(self) -> str:
        """Get the default environment variable name for API key."""
        return "AZURE_OPENAI_API_KEY"

    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return "azure"

    def get_llm(self) -> Any:
        """Get or create the Azure OpenAI LLM instance."""
        if self._llm is None:
            try:
                from langchain_openai import AzureChatOpenAI
            except ImportError as e:
                raise ImportError(
                    "langchain-openai is required for Azure OpenAI provider. "
                    "It should already be installed."
                ) from e

            api_key = self.api_key or os.getenv(self.default_env_var)
            if not api_key:
                raise ValueError(
                    f"{self.provider_name} API key is required. "
                    f"Set {self.default_env_var} environment variable or pass api_key parameter."
                )

            endpoint = self.azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
            if not endpoint:
                raise ValueError(
                    "Azure OpenAI endpoint is required. "
                    "Set AZURE_OPENAI_ENDPOINT environment variable or pass azure_endpoint parameter."
                )

            self._llm = AzureChatOpenAI(
                azure_deployment=self.model_name,
                temperature=self.temperature,
                api_key=api_key,
                azure_endpoint=endpoint,
                api_version=self.api_version,
                **self.kwargs,
            )
        return self._llm
