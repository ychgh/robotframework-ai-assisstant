# Multi-Provider LLM Architecture

## Overview

The Robot Framework AI Assistant now supports multiple LLM providers through a flexible, extensible architecture.

## Architecture

```
┌─────────────────────────────────────────┐
│      AIService (ai_service.py)          │
│  ┌───────────────────────────────────┐  │
│  │  Generates test data, test cases, │  │
│  │  reports using LLM provider       │  │
│  └───────────────────────────────────┘  │
└──────────────┬──────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  LLMProviderFactory (factory.py)         │
│  ┌────────────────────────────────────┐  │
│  │  Creates appropriate provider      │  │
│  │  based on provider name            │  │
│  └────────────────────────────────────┘  │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  BaseLLMProvider (base.py)               │
│  ┌────────────────────────────────────┐  │
│  │  Abstract base class defining      │  │
│  │  provider interface                │  │
│  └────────────────────────────────────┘  │
└──────────────┬───────────────────────────┘
               │
       ┌───────┴───────┬──────────┬──────────┬──────────┐
       ▼               ▼          ▼          ▼          ▼
┌──────────┐    ┌──────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│ OpenAI   │    │Anthropic │ │ Google │ │ Azure  │ │Ollama  │
│Provider  │    │Provider  │ │Provider│ │Provider│ │Provider│
└──────────┘    └──────────┘ └────────┘ └────────┘ └────────┘
```

## Supported Providers

### 1. OpenAI (Default)
- **Models**: GPT-4, GPT-4-turbo, GPT-3.5-turbo
- **Environment Variable**: `OPENAI_API_KEY`
- **Installation**: Built-in (langchain-openai)

### 2. Anthropic Claude
- **Models**: claude-3-opus-20240229, claude-3-sonnet-20240229
- **Environment Variable**: `ANTHROPIC_API_KEY`
- **Installation**: `pip install langchain-anthropic`

### 3. Google Gemini
- **Models**: gemini-pro, gemini-pro-vision
- **Environment Variable**: `GOOGLE_API_KEY`
- **Installation**: `pip install langchain-google-genai`

### 4. Azure OpenAI
- **Models**: Any Azure deployment name
- **Environment Variables**: `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`
- **Installation**: Built-in (langchain-openai)

### 5. Ollama (Local Models)
- **Models**: llama2, mistral, codellama, etc.
- **Environment Variable**: Not required
- **Installation**: Built-in (langchain-community)
- **Requirements**: Ollama server running on http://localhost:11434

## Usage Examples

### Robot Framework Library

```robotframework
*** Settings ***
# OpenAI (default)
Library    AIAssistantLibrary

# Anthropic Claude
Library    AIAssistantLibrary
...        provider=anthropic
...        model_name=claude-3-opus-20240229
...        api_key=${ANTHROPIC_KEY}

# Google Gemini
Library    AIAssistantLibrary
...        provider=google
...        model_name=gemini-pro

# Azure OpenAI
Library    AIAssistantLibrary
...        provider=azure
...        model_name=my-gpt4-deployment
...        azure_endpoint=https://my-resource.openai.azure.com

# Ollama (local)
Library    AIAssistantLibrary
...        provider=ollama
...        model_name=llama2
```

### Python API

```python
from robotframework_ai_assistant.ai_service import AIService

# OpenAI
service = AIService(provider="openai", model_name="gpt-4")

# Anthropic
service = AIService(
    provider="anthropic",
    model_name="claude-3-opus-20240229",
    api_key="your-key"
)

# Google
service = AIService(provider="google", model_name="gemini-pro")

# Azure
service = AIService(
    provider="azure",
    model_name="my-deployment",
    azure_endpoint="https://my-resource.openai.azure.com"
)

# Ollama
service = AIService(provider="ollama", model_name="llama2")
```

### FastAPI Server

Configure via environment variables:

```bash
# OpenAI (default)
export OPENAI_API_KEY=your-key
rf-ai-server

# Anthropic
export LLM_PROVIDER=anthropic
export LLM_MODEL=claude-3-opus-20240229
export ANTHROPIC_API_KEY=your-key
rf-ai-server

# Google
export LLM_PROVIDER=google
export LLM_MODEL=gemini-pro
export GOOGLE_API_KEY=your-key
rf-ai-server

# Ollama
export LLM_PROVIDER=ollama
export LLM_MODEL=llama2
rf-ai-server
```

## Extending with Custom Providers

You can register custom providers:

```python
from robotframework_ai_assistant.providers.base import BaseLLMProvider
from robotframework_ai_assistant.providers.factory import LLMProviderFactory

class CustomProvider(BaseLLMProvider):
    @property
    def default_env_var(self):
        return "CUSTOM_API_KEY"
    
    @property
    def provider_name(self):
        return "custom"
    
    def get_llm(self):
        # Return LangChain-compatible LLM
        pass

# Register the provider
LLMProviderFactory.register_provider("custom", CustomProvider)

# Use it
service = AIService(provider="custom", model_name="model-name")
```

## Benefits

1. **Flexibility**: Choose the best LLM for your use case
2. **Cost Optimization**: Use different providers based on budget
3. **Local Development**: Test with Ollama without API costs
4. **Enterprise Ready**: Support Azure deployments
5. **Extensible**: Easy to add new providers
6. **Backward Compatible**: Defaults to OpenAI GPT-4

## Testing

All providers are thoroughly tested:
- 18 provider-specific tests
- 68 total tests passing
- Comprehensive coverage of initialization, configuration, and LLM creation
