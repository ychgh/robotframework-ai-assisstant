"""Tests for the AI Assistant Library keywords."""

from unittest.mock import MagicMock, patch

import pytest

from robotframework_ai_assistant.keywords.library import AIAssistantLibrary


class TestAIAssistantLibrary:
    """Tests for AIAssistantLibrary class."""

    def test_library_initialization(self):
        """Test that library can be initialized without API key."""
        library = AIAssistantLibrary()
        assert library is not None
        assert library._ai_service is not None

    def test_library_initialization_with_api_key(self):
        """Test that library can be initialized with API key."""
        library = AIAssistantLibrary(api_key="test-key")
        assert library._ai_service.api_key == "test-key"

    def test_library_initialization_with_jira(self):
        """Test that library can be initialized with JIRA credentials."""
        library = AIAssistantLibrary(
            jira_url="https://test.atlassian.net",
            jira_username="user@test.com",
            jira_api_token="token123",
        )
        assert library._jira_client is not None

    def test_library_initialization_without_jira(self):
        """Test that JIRA client is None when not configured."""
        library = AIAssistantLibrary()
        assert library._jira_client is None

    @patch("robotframework_ai_assistant.keywords.library.AIService")
    def test_generate_test_data(self, mock_ai_service_class):
        """Test generate_test_data keyword."""
        mock_service = MagicMock()
        mock_service.generate_test_data.return_value = [
            {"id": 1, "name": "Test User", "email": "test@example.com"}
        ]
        mock_ai_service_class.return_value = mock_service

        library = AIAssistantLibrary()
        library._ai_service = mock_service

        result = library.generate_test_data("user", count=1)

        assert len(result) == 1
        assert result[0]["name"] == "Test User"
        mock_service.generate_test_data.assert_called_once()

    @patch("robotframework_ai_assistant.keywords.library.AIService")
    def test_generate_test_data_with_constraints(self, mock_ai_service_class):
        """Test generate_test_data with constraints."""
        mock_service = MagicMock()
        mock_service.generate_test_data.return_value = [
            {"id": 1, "name": "Adult User", "age": 25}
        ]
        mock_ai_service_class.return_value = mock_service

        library = AIAssistantLibrary()
        library._ai_service = mock_service

        result = library.generate_test_data(
            "user",
            count=1,
            constraints='{"age": "18-65"}',
        )

        assert len(result) == 1
        mock_service.generate_test_data.assert_called_once()

    @patch("robotframework_ai_assistant.keywords.library.AIService")
    def test_explore_test_environment(self, mock_ai_service_class):
        """Test explore_test_environment keyword."""
        mock_service = MagicMock()
        mock_service.explore_environment.return_value = {
            "summary": "Test API environment",
            "components": ["REST API", "Database"],
            "test_areas": ["Authentication", "CRUD operations"],
            "recommendations": ["Test error handling"],
            "risks": ["Rate limiting not tested"],
        }
        mock_ai_service_class.return_value = mock_service

        library = AIAssistantLibrary()
        library._ai_service = mock_service

        result = library.explore_test_environment('{"url": "https://api.example.com"}', "api")

        assert result["summary"] == "Test API environment"
        assert len(result["components"]) == 2
        mock_service.explore_environment.assert_called_once()

    @patch("robotframework_ai_assistant.keywords.library.AIService")
    def test_generate_test_cases(self, mock_ai_service_class):
        """Test generate_test_cases keyword."""
        mock_service = MagicMock()
        mock_service.generate_test_cases.return_value = [
            {
                "name": "Test Login Success",
                "description": "Verify successful login",
                "steps": ["Open browser", "Enter credentials", "Click login"],
                "expected_results": ["User is logged in"],
                "priority": "high",
                "tags": ["login", "smoke"],
            }
        ]
        mock_ai_service_class.return_value = mock_service

        library = AIAssistantLibrary()
        library._ai_service = mock_service

        result = library.generate_test_cases("Login functionality", "functional", "robot", 1)

        assert len(result) == 1
        assert result[0]["name"] == "Test Login Success"
        mock_service.generate_test_cases.assert_called_once()

    @patch("robotframework_ai_assistant.keywords.library.AIService")
    def test_generate_test_report(self, mock_ai_service_class):
        """Test generate_test_report keyword."""
        mock_service = MagicMock()
        mock_service.generate_test_report.return_value = {
            "title": "Test Execution Report",
            "summary": "All tests passed",
            "statistics": {
                "total": 10,
                "passed": 10,
                "failed": 0,
                "pass_rate": "100%",
            },
            "highlights": ["All tests passed"],
            "recommendations": ["Add more edge cases"],
        }
        mock_ai_service_class.return_value = mock_service

        library = AIAssistantLibrary()
        library._ai_service = mock_service

        result = library.generate_test_report('[{"name": "Test1", "status": "passed"}]')

        assert result["title"] == "Test Execution Report"
        assert result["statistics"]["pass_rate"] == "100%"
        mock_service.generate_test_report.assert_called_once()

    def test_create_jira_issue_without_client(self):
        """Test that JIRA operations fail without client."""
        library = AIAssistantLibrary()

        with pytest.raises(RuntimeError, match="JIRA client not configured"):
            library.create_jira_issue_from_failure(
                "Test Failed",
                "Error message",
                "PROJ",
            )

    def test_xray_operation_without_client(self):
        """Test that Xray operations fail without client."""
        library = AIAssistantLibrary()

        with pytest.raises(RuntimeError, match="Xray client not configured"):
            library.import_test_execution_to_xray("output.xml", "PROJ")

    def test_zephyr_operation_without_client(self):
        """Test that Zephyr operations fail without client."""
        library = AIAssistantLibrary()

        with pytest.raises(RuntimeError, match="Zephyr client not configured"):
            library.create_zephyr_test_cycle("Test Cycle", "PROJ")


class TestLibraryKeywordDecorators:
    """Tests for keyword decorators and metadata."""

    def test_library_has_scope(self):
        """Test that library has GLOBAL scope."""
        assert AIAssistantLibrary.ROBOT_LIBRARY_SCOPE == "GLOBAL"

    def test_library_has_version(self):
        """Test that library has version."""
        assert AIAssistantLibrary.ROBOT_LIBRARY_VERSION == "0.1.0"
