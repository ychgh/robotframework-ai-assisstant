"""Ollama provider implementation for local models."""

from typing import Any, Optional

from robotframework_ai_assistant.providers.base import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):
    """Ollama LLM provider for local models."""

    def __init__(
        self,
        model_name: str = "llama2",
        temperature: float = 0.7,
        api_key: Optional[str] = None,
        base_url: str = "http://localhost:11434",
        **kwargs: Any,
    ):
        """Initialize Ollama provider.

        Args:
            model_name: Ollama model name (e.g., 'llama2', 'mistral', 'codellama').
            temperature: Temperature for generation.
            api_key: Not used for Ollama but kept for interface compatibility.
            base_url: Ollama server base URL. Defaults to 'http://localhost:11434'.
            **kwargs: Additional ChatOllama parameters.
        """
        super().__init__(model_name, temperature, api_key, **kwargs)
        self.base_url = base_url

    @property
    def default_env_var(self) -> str:
        """Get the default environment variable name for API key."""
        return "OLLAMA_API_KEY"  # Not typically used

    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return "ollama"

    def get_llm(self) -> Any:
        """Get or create the Ollama LLM instance."""
        if self._llm is None:
            try:
                from langchain_community.chat_models import ChatOllama
            except ImportError as e:
                raise ImportError(
                    "langchain-community is required for Ollama provider. "
                    "It should already be installed."
                ) from e

            self._llm = ChatOllama(
                model=self.model_name,
                temperature=self.temperature,
                base_url=self.base_url,
                **self.kwargs,
            )
        return self._llm
