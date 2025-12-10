"""Tests for LLM providers."""

from unittest.mock import MagicMock, patch

import pytest

from robotframework_ai_assistant.providers.factory import LLMProviderFactory
from robotframework_ai_assistant.providers.openai_provider import OpenAIProvider


class TestLLMProviderFactory:
    """Tests for LLM provider factory."""

    def test_get_available_providers(self):
        """Test getting list of available providers."""
        providers = LLMProviderFactory.get_available_providers()
        assert "openai" in providers
        assert "anthropic" in providers
        assert "google" in providers
        assert "azure" in providers
        assert "ollama" in providers
        assert "deepseek" in providers
        assert "qwen" in providers

    def test_create_openai_provider(self):
        """Test creating OpenAI provider."""
        provider = LLMProviderFactory.create_provider(
            provider="openai",
            model_name="gpt-4",
            api_key="test-key",
        )
        assert isinstance(provider, OpenAIProvider)
        assert provider.model_name == "gpt-4"
        assert provider.api_key == "test-key"

    def test_create_provider_case_insensitive(self):
        """Test that provider name is case-insensitive."""
        provider = LLMProviderFactory.create_provider(
            provider="OpenAI",
            model_name="gpt-4",
            api_key="test-key",
        )
        assert isinstance(provider, OpenAIProvider)

    def test_create_unsupported_provider(self):
        """Test error for unsupported provider."""
        with pytest.raises(ValueError, match="Unsupported provider"):
            LLMProviderFactory.create_provider(
                provider="invalid",
                model_name="model",
            )

    def test_register_custom_provider(self):
        """Test registering a custom provider."""
        from robotframework_ai_assistant.providers.base import BaseLLMProvider

        class CustomProvider(BaseLLMProvider):
            @property
            def default_env_var(self):
                return "CUSTOM_API_KEY"

            @property
            def provider_name(self):
                return "custom"

            def get_llm(self):
                return MagicMock()

        LLMProviderFactory.register_provider("custom", CustomProvider)

        provider = LLMProviderFactory.create_provider(
            provider="custom",
            model_name="test-model",
        )
        assert isinstance(provider, CustomProvider)


class TestOpenAIProvider:
    """Tests for OpenAI provider."""

    def test_provider_initialization(self):
        """Test OpenAI provider initialization."""
        provider = OpenAIProvider(
            model_name="gpt-4",
            temperature=0.5,
            api_key="test-key",
        )
        assert provider.model_name == "gpt-4"
        assert provider.temperature == 0.5
        assert provider.api_key == "test-key"

    def test_provider_name(self):
        """Test provider name."""
        provider = OpenAIProvider(api_key="test-key")
        assert provider.provider_name == "openai"

    def test_default_env_var(self):
        """Test default environment variable."""
        provider = OpenAIProvider(api_key="test-key")
        assert provider.default_env_var == "OPENAI_API_KEY"

    @patch("robotframework_ai_assistant.providers.openai_provider.ChatOpenAI")
    def test_get_llm(self, mock_chat_openai):
        """Test getting LLM instance."""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm

        provider = OpenAIProvider(model_name="gpt-4", api_key="test-key")
        llm = provider.get_llm()

        assert llm == mock_llm
        mock_chat_openai.assert_called_once_with(
            model="gpt-4",
            temperature=0.7,
            api_key="test-key",
        )

    @patch("robotframework_ai_assistant.providers.openai_provider.ChatOpenAI")
    def test_get_llm_caching(self, mock_chat_openai):
        """Test that LLM instance is cached."""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm

        provider = OpenAIProvider(api_key="test-key")
        llm1 = provider.get_llm()
        llm2 = provider.get_llm()

        assert llm1 is llm2
        assert mock_chat_openai.call_count == 1

    def test_get_llm_without_api_key(self):
        """Test error when API key is not provided."""
        provider = OpenAIProvider()
        provider.api_key = None

        with pytest.raises(ValueError, match="openai API key is required"):
            provider.get_llm()


class TestAnthropicProvider:
    """Tests for Anthropic provider."""

    def test_provider_initialization(self):
        """Test Anthropic provider initialization."""
        from robotframework_ai_assistant.providers.anthropic_provider import AnthropicProvider

        provider = AnthropicProvider(
            model_name="claude-3-opus-20240229",
            temperature=0.5,
            api_key="test-key",
        )
        assert provider.model_name == "claude-3-opus-20240229"
        assert provider.temperature == 0.5
        assert provider.api_key == "test-key"

    def test_provider_name(self):
        """Test provider name."""
        from robotframework_ai_assistant.providers.anthropic_provider import AnthropicProvider

        provider = AnthropicProvider(api_key="test-key")
        assert provider.provider_name == "anthropic"

    def test_default_env_var(self):
        """Test default environment variable."""
        from robotframework_ai_assistant.providers.anthropic_provider import AnthropicProvider

        provider = AnthropicProvider(api_key="test-key")
        assert provider.default_env_var == "ANTHROPIC_API_KEY"


class TestAzureOpenAIProvider:
    """Tests for Azure OpenAI provider."""

    def test_provider_initialization(self):
        """Test Azure provider initialization."""
        from robotframework_ai_assistant.providers.azure_provider import AzureOpenAIProvider

        provider = AzureOpenAIProvider(
            model_name="my-deployment",
            azure_endpoint="https://my-resource.openai.azure.com",
            api_key="test-key",
        )
        assert provider.model_name == "my-deployment"
        assert provider.azure_endpoint == "https://my-resource.openai.azure.com"

    def test_provider_name(self):
        """Test provider name."""
        from robotframework_ai_assistant.providers.azure_provider import AzureOpenAIProvider

        provider = AzureOpenAIProvider(
            model_name="deployment",
            api_key="test-key",
        )
        assert provider.provider_name == "azure"


class TestOllamaProvider:
    """Tests for Ollama provider."""

    def test_provider_initialization(self):
        """Test Ollama provider initialization."""
        from robotframework_ai_assistant.providers.ollama_provider import OllamaProvider

        provider = OllamaProvider(
            model_name="llama2",
            base_url="http://localhost:11434",
        )
        assert provider.model_name == "llama2"
        assert provider.base_url == "http://localhost:11434"

    def test_provider_name(self):
        """Test provider name."""
        from robotframework_ai_assistant.providers.ollama_provider import OllamaProvider

        provider = OllamaProvider()
        assert provider.provider_name == "ollama"


class TestDeepSeekProvider:
    """Tests for DeepSeek provider."""

    def test_provider_initialization(self):
        """Test DeepSeek provider initialization."""
        from robotframework_ai_assistant.providers.deepseek_provider import DeepSeekProvider

        provider = DeepSeekProvider(
            model_name="deepseek-chat",
            api_key="test-key",
        )
        assert provider.model_name == "deepseek-chat"
        assert provider.api_key == "test-key"
        assert provider.base_url == "https://api.deepseek.com/v1"

    def test_provider_name(self):
        """Test provider name."""
        from robotframework_ai_assistant.providers.deepseek_provider import DeepSeekProvider

        provider = DeepSeekProvider(api_key="test-key")
        assert provider.provider_name == "deepseek"

    def test_default_env_var(self):
        """Test default environment variable."""
        from robotframework_ai_assistant.providers.deepseek_provider import DeepSeekProvider

        provider = DeepSeekProvider(api_key="test-key")
        assert provider.default_env_var == "DEEPSEEK_API_KEY"

    @patch("langchain_openai.ChatOpenAI")
    def test_get_llm(self, mock_chat_openai):
        """Test getting LLM instance."""
        from robotframework_ai_assistant.providers.deepseek_provider import DeepSeekProvider

        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm

        provider = DeepSeekProvider(model_name="deepseek-chat", api_key="test-key")
        llm = provider.get_llm()

        assert llm == mock_llm
        mock_chat_openai.assert_called_once_with(
            model="deepseek-chat",
            temperature=0.7,
            api_key="test-key",
            base_url="https://api.deepseek.com/v1",
        )


class TestQwenProvider:
    """Tests for Qwen provider."""

    def test_provider_initialization(self):
        """Test Qwen provider initialization."""
        from robotframework_ai_assistant.providers.qwen_provider import QwenProvider

        provider = QwenProvider(
            model_name="qwen-turbo",
            api_key="test-key",
        )
        assert provider.model_name == "qwen-turbo"
        assert provider.api_key == "test-key"
        assert provider.base_url == "https://dashscope.aliyuncs.com/compatible-mode/v1"

    def test_provider_name(self):
        """Test provider name."""
        from robotframework_ai_assistant.providers.qwen_provider import QwenProvider

        provider = QwenProvider(api_key="test-key")
        assert provider.provider_name == "qwen"

    def test_default_env_var(self):
        """Test default environment variable."""
        from robotframework_ai_assistant.providers.qwen_provider import QwenProvider

        provider = QwenProvider(api_key="test-key")
        assert provider.default_env_var == "DASHSCOPE_API_KEY"

    @patch("langchain_openai.ChatOpenAI")
    def test_get_llm(self, mock_chat_openai):
        """Test getting LLM instance."""
        from robotframework_ai_assistant.providers.qwen_provider import QwenProvider

        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm

        provider = QwenProvider(model_name="qwen-turbo", api_key="test-key")
        llm = provider.get_llm()

        assert llm == mock_llm
        mock_chat_openai.assert_called_once_with(
            model="qwen-turbo",
            temperature=0.7,
            api_key="test-key",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
