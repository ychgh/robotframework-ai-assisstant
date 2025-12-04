"""Tests for the AI Service."""

import json
from unittest.mock import MagicMock, patch

import pytest

from robotframework_ai_assistant.ai_service import AIService


class TestAIService:
    """Tests for AIService class."""

    def test_service_initialization(self):
        """Test AI service initialization."""
        service = AIService(api_key="test-key")
        assert service.api_key == "test-key"
        assert service.model_name == "gpt-4"
        assert service.temperature == 0.7

    def test_service_initialization_custom_params(self):
        """Test AI service initialization with custom parameters."""
        service = AIService(
            api_key="test-key",
            model_name="gpt-3.5-turbo",
            temperature=0.5,
        )
        assert service.model_name == "gpt-3.5-turbo"
        assert service.temperature == 0.5

    def test_llm_property_raises_without_key(self):
        """Test that accessing LLM without API key raises error."""
        service = AIService()
        service.api_key = None

        with pytest.raises(ValueError, match="OpenAI API key is required"):
            _ = service.llm

    @patch("robotframework_ai_assistant.ai_service.ChatOpenAI")
    def test_llm_property_creates_instance(self, mock_chat_openai):
        """Test that LLM instance is created correctly."""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm

        service = AIService(api_key="test-key")
        llm = service.llm

        assert llm == mock_llm
        mock_chat_openai.assert_called_once_with(
            model="gpt-4",
            temperature=0.7,
            api_key="test-key",
        )

    @patch("robotframework_ai_assistant.ai_service.ChatOpenAI")
    def test_llm_property_caches_instance(self, mock_chat_openai):
        """Test that LLM instance is cached."""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm

        service = AIService(api_key="test-key")
        llm1 = service.llm
        llm2 = service.llm

        assert llm1 is llm2
        assert mock_chat_openai.call_count == 1

    @patch("robotframework_ai_assistant.ai_service.ChatPromptTemplate")
    @patch("robotframework_ai_assistant.ai_service.ChatOpenAI")
    def test_generate_test_data(self, mock_chat_openai, mock_prompt_class):
        """Test generate_test_data method with mocked LLM."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.content = json.dumps([
            {"id": 1, "name": "Test User", "email": "test@example.com"}
        ])

        # Setup mock chain
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = mock_response

        # Setup mock prompt
        mock_prompt = MagicMock()
        mock_prompt.__or__ = MagicMock(return_value=mock_chain)
        mock_prompt_class.from_messages.return_value = mock_prompt

        # Setup mock LLM
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm

        service = AIService(api_key="test-key")
        result = service.generate_test_data("user", count=1)

        assert len(result) == 1
        assert result[0]["name"] == "Test User"

    @patch("robotframework_ai_assistant.ai_service.ChatPromptTemplate")
    @patch("robotframework_ai_assistant.ai_service.ChatOpenAI")
    def test_generate_test_data_handles_code_block(self, mock_chat_openai, mock_prompt_class):
        """Test that code blocks are handled in response."""
        mock_response = MagicMock()
        mock_response.content = """```json
[{"id": 1, "name": "Test"}]
```"""

        mock_chain = MagicMock()
        mock_chain.invoke.return_value = mock_response

        mock_prompt = MagicMock()
        mock_prompt.__or__ = MagicMock(return_value=mock_chain)
        mock_prompt_class.from_messages.return_value = mock_prompt

        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm

        service = AIService(api_key="test-key")
        result = service.generate_test_data("user", count=1)

        assert len(result) == 1
        assert result[0]["name"] == "Test"

    @patch("robotframework_ai_assistant.ai_service.ChatPromptTemplate")
    @patch("robotframework_ai_assistant.ai_service.ChatOpenAI")
    def test_generate_test_data_handles_invalid_json(self, mock_chat_openai, mock_prompt_class):
        """Test handling of invalid JSON response."""
        mock_response = MagicMock()
        mock_response.content = "This is not valid JSON"

        mock_chain = MagicMock()
        mock_chain.invoke.return_value = mock_response

        mock_prompt = MagicMock()
        mock_prompt.__or__ = MagicMock(return_value=mock_chain)
        mock_prompt_class.from_messages.return_value = mock_prompt

        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm

        service = AIService(api_key="test-key")
        result = service.generate_test_data("user", count=1)

        assert len(result) == 1
        assert "raw_response" in result[0]

    @patch("robotframework_ai_assistant.ai_service.ChatPromptTemplate")
    @patch("robotframework_ai_assistant.ai_service.ChatOpenAI")
    def test_explore_environment(self, mock_chat_openai, mock_prompt_class):
        """Test explore_environment method with mocked LLM."""
        mock_response = MagicMock()
        mock_response.content = json.dumps({
            "summary": "Test environment",
            "components": ["API", "Database"],
            "test_areas": ["Authentication"],
            "recommendations": ["Test edge cases"],
            "risks": ["Security"],
        })

        mock_chain = MagicMock()
        mock_chain.invoke.return_value = mock_response

        mock_prompt = MagicMock()
        mock_prompt.__or__ = MagicMock(return_value=mock_chain)
        mock_prompt_class.from_messages.return_value = mock_prompt

        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm

        service = AIService(api_key="test-key")
        result = service.explore_environment({"url": "https://api.example.com"}, "api")

        assert result["summary"] == "Test environment"
        assert len(result["components"]) == 2

    @patch("robotframework_ai_assistant.ai_service.ChatPromptTemplate")
    @patch("robotframework_ai_assistant.ai_service.ChatOpenAI")
    def test_generate_test_cases(self, mock_chat_openai, mock_prompt_class):
        """Test generate_test_cases method with mocked LLM."""
        mock_response = MagicMock()
        mock_response.content = json.dumps([
            {
                "name": "Test Login",
                "description": "Test login functionality",
                "steps": ["Open browser", "Enter credentials"],
                "expected_results": ["User logged in"],
                "priority": "high",
                "tags": ["login"],
                "code": "*** Test Cases ***\nTest Login\n    Log    Test",
            }
        ])

        mock_chain = MagicMock()
        mock_chain.invoke.return_value = mock_response

        mock_prompt = MagicMock()
        mock_prompt.__or__ = MagicMock(return_value=mock_chain)
        mock_prompt_class.from_messages.return_value = mock_prompt

        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm

        service = AIService(api_key="test-key")
        result = service.generate_test_cases("Login feature", "functional", "robot", 1)

        assert len(result) == 1
        assert result[0]["name"] == "Test Login"

    @patch("robotframework_ai_assistant.ai_service.ChatPromptTemplate")
    @patch("robotframework_ai_assistant.ai_service.ChatOpenAI")
    def test_generate_test_report(self, mock_chat_openai, mock_prompt_class):
        """Test generate_test_report method with mocked LLM."""
        mock_response = MagicMock()
        mock_response.content = json.dumps({
            "title": "Test Report",
            "summary": "Tests completed",
            "statistics": {
                "total": 10,
                "passed": 8,
                "failed": 2,
                "pass_rate": "80%",
            },
            "highlights": ["Good coverage"],
            "failures_analysis": ["Timeout issues"],
            "recommendations": ["Increase timeouts"],
        })

        mock_chain = MagicMock()
        mock_chain.invoke.return_value = mock_response

        mock_prompt = MagicMock()
        mock_prompt.__or__ = MagicMock(return_value=mock_chain)
        mock_prompt_class.from_messages.return_value = mock_prompt

        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm

        service = AIService(api_key="test-key")
        result = service.generate_test_report(
            [{"name": "Test1", "status": "passed"}],
            "summary",
            True,
        )

        assert result["title"] == "Test Report"
        assert result["statistics"]["pass_rate"] == "80%"

    @patch("robotframework_ai_assistant.ai_service.ChatPromptTemplate")
    @patch("robotframework_ai_assistant.ai_service.ChatOpenAI")
    def test_analyze_for_jira(self, mock_chat_openai, mock_prompt_class):
        """Test analyze_for_jira method with mocked LLM."""
        mock_response = MagicMock()
        mock_response.content = json.dumps([
            {
                "summary": "Login test failure",
                "description": "Login test failed due to timeout",
                "issue_type": "Bug",
                "priority": "High",
                "labels": ["automated-test"],
            }
        ])

        mock_chain = MagicMock()
        mock_chain.invoke.return_value = mock_response

        mock_prompt = MagicMock()
        mock_prompt.__or__ = MagicMock(return_value=mock_chain)
        mock_prompt_class.from_messages.return_value = mock_prompt

        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm

        service = AIService(api_key="test-key")
        result = service.analyze_for_jira(
            [{"test": "Login", "error": "Timeout"}],
            "PROJ",
        )

        assert len(result) == 1
        assert result[0]["summary"] == "Login test failure"
