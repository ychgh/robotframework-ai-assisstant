"""Tests for integration clients."""

from unittest.mock import MagicMock, patch

from robotframework_ai_assistant.integrations.jira_client import JiraClient
from robotframework_ai_assistant.integrations.xray_client import XrayClient
from robotframework_ai_assistant.integrations.zephyr_client import ZephyrClient


class TestJiraClient:
    """Tests for JIRA client."""

    def test_client_initialization(self):
        """Test JIRA client initialization."""
        client = JiraClient(
            url="https://test.atlassian.net",
            username="user@test.com",
            api_token="token123",
        )
        assert client.url == "https://test.atlassian.net"
        assert client.username == "user@test.com"

    def test_client_url_trailing_slash(self):
        """Test URL trailing slash is removed."""
        client = JiraClient(
            url="https://test.atlassian.net/",
            username="user@test.com",
            api_token="token123",
        )
        assert client.url == "https://test.atlassian.net"

    @patch("httpx.Client")
    def test_create_issue(self, mock_client_class):
        """Test create issue."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"key": "PROJ-123", "id": "12345"}
        mock_response.content = b'{"key": "PROJ-123"}'

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        client = JiraClient(
            url="https://test.atlassian.net",
            username="user@test.com",
            api_token="token123",
        )

        result = client.create_issue(
            project_key="PROJ",
            summary="Test issue",
            description="Test description",
            issue_type="Bug",
        )

        assert result["key"] == "PROJ-123"

    @patch("httpx.Client")
    def test_get_issue(self, mock_client_class):
        """Test get issue."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "key": "PROJ-123",
            "fields": {"summary": "Test issue"},
        }
        mock_response.content = b'{"key": "PROJ-123"}'

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        client = JiraClient(
            url="https://test.atlassian.net",
            username="user@test.com",
            api_token="token123",
        )

        result = client.get_issue("PROJ-123")

        assert result["key"] == "PROJ-123"


class TestXrayClient:
    """Tests for Xray client."""

    def test_client_initialization(self):
        """Test Xray client initialization."""
        client = XrayClient(
            client_id="client123",
            client_secret="secret456",
        )
        assert client.client_id == "client123"
        assert client.client_secret == "secret456"

    @patch("httpx.Client")
    def test_authentication(self, mock_client_class):
        """Test Xray authentication."""
        mock_response = MagicMock()
        mock_response.text = '"token123"'

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        client = XrayClient(
            client_id="client123",
            client_secret="secret456",
        )

        token = client._authenticate()
        assert token == "token123"

    @patch("httpx.Client")
    def test_authentication_caching(self, mock_client_class):
        """Test that authentication token is cached."""
        mock_response = MagicMock()
        mock_response.text = '"token123"'

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        client = XrayClient(
            client_id="client123",
            client_secret="secret456",
        )

        client._authenticate()
        client._authenticate()

        # Should only authenticate once
        assert mock_client.post.call_count == 1


class TestZephyrClient:
    """Tests for Zephyr client."""

    def test_client_initialization_cloud(self):
        """Test Zephyr client initialization for Cloud."""
        client = ZephyrClient(
            api_token="token123",
            jira_url="https://test.atlassian.net",
        )
        assert "zephyrscale.smartbear.com" in client.base_url

    def test_client_initialization_server(self):
        """Test Zephyr client initialization for Server."""
        client = ZephyrClient(
            api_token="token123",
            jira_url="https://jira.example.com",
        )
        assert "jira.example.com" in client.base_url

    @patch("httpx.Client")
    def test_create_test_cycle(self, mock_client_class):
        """Test create test cycle."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"key": "PROJ-C1", "name": "Test Cycle"}
        mock_response.content = b'{"key": "PROJ-C1"}'

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        client = ZephyrClient(
            api_token="token123",
            jira_url="https://test.atlassian.net",
        )

        result = client.create_test_cycle(
            name="Test Cycle",
            project_key="PROJ",
        )

        assert result["key"] == "PROJ-C1"

    @patch("httpx.Client")
    def test_create_test_case(self, mock_client_class):
        """Test create test case."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"key": "PROJ-T1", "name": "Test Case"}
        mock_response.content = b'{"key": "PROJ-T1"}'

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        client = ZephyrClient(
            api_token="token123",
            jira_url="https://test.atlassian.net",
        )

        result = client.create_test_case(
            name="Test Case",
            project_key="PROJ",
            objective="Test objective",
        )

        assert result["key"] == "PROJ-T1"
