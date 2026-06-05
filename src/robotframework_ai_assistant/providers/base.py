"""Base provider interface for LLM implementations."""

from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseLLMProvider(ABC):
    """Base class for LLM providers."""

    def __init__(
        self,
        model_name: str,
        temperature: float = 0.7,
        api_key: Optional[str] = None,
        **kwargs: Any,
    ):
        """Initialize the provider.

        Args:
            model_name: Name of the model to use.
            temperature: Temperature for generation (0.0 to 1.0).
            api_key: API key for the provider.
            **kwargs: Additional provider-specific parameters.
        """
        self.model_name = model_name
        self.temperature = temperature
        self.api_key = api_key
        self.kwargs = kwargs
        self._llm: Optional[Any] = None

    @abstractmethod
    def get_llm(self) -> Any:
        """Get or create the LLM instance.

        Returns:
            The LLM instance compatible with LangChain.
        """
        pass

    @property
    @abstractmethod
    def default_env_var(self) -> str:
        """Get the default environment variable name for API key.

        Returns:
            Environment variable name.
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get the provider name.

        Returns:
            Provider name.
        """
        pass
