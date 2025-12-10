"""Factory for creating LLM provider instances."""

from typing import Any, Optional

from robotframework_ai_assistant.providers.base import BaseLLMProvider


class LLMProviderFactory:
    """Factory for creating LLM provider instances."""

    _providers: dict[str, type[BaseLLMProvider]] = {}

    @classmethod
    def register_provider(cls, name: str, provider_class: type[BaseLLMProvider]) -> None:
        """Register a provider.

        Args:
            name: Provider name.
            provider_class: Provider class.
        """
        cls._providers[name.lower()] = provider_class

    @classmethod
    def create_provider(
        cls,
        provider: str,
        model_name: str,
        temperature: float = 0.7,
        api_key: Optional[str] = None,
        **kwargs: Any,
    ) -> BaseLLMProvider:
        """Create a provider instance.

        Args:
            provider: Provider name ('openai', 'anthropic', 'google', 'azure', 'ollama').
            model_name: Model name.
            temperature: Temperature for generation.
            api_key: API key for the provider.
            **kwargs: Additional provider-specific parameters.

        Returns:
            Provider instance.

        Raises:
            ValueError: If provider is not supported.
        """
        provider_lower = provider.lower()

        # Lazy load providers to avoid import errors for optional dependencies
        if provider_lower not in cls._providers:
            cls._load_default_providers()

        if provider_lower not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(
                f"Unsupported provider: {provider}. Available providers: {available}"
            )

        provider_class = cls._providers[provider_lower]
        return provider_class(
            model_name=model_name,
            temperature=temperature,
            api_key=api_key,
            **kwargs,
        )

    @classmethod
    def _load_default_providers(cls) -> None:
        """Load default providers."""
        if cls._providers:
            return  # Already loaded

        # Import and register default providers
        from robotframework_ai_assistant.providers.anthropic_provider import AnthropicProvider
        from robotframework_ai_assistant.providers.azure_provider import AzureOpenAIProvider
        from robotframework_ai_assistant.providers.google_provider import GoogleProvider
        from robotframework_ai_assistant.providers.ollama_provider import OllamaProvider
        from robotframework_ai_assistant.providers.openai_provider import OpenAIProvider

        cls.register_provider("openai", OpenAIProvider)
        cls.register_provider("anthropic", AnthropicProvider)
        cls.register_provider("google", GoogleProvider)
        cls.register_provider("azure", AzureOpenAIProvider)
        cls.register_provider("ollama", OllamaProvider)

    @classmethod
    def get_available_providers(cls) -> list[str]:
        """Get list of available providers.

        Returns:
            List of provider names.
        """
        cls._load_default_providers()
        return list(cls._providers.keys())
