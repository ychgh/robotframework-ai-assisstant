"""Tests for the FastAPI server."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


class TestAPIServer:
    """Tests for the FastAPI server."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from robotframework_ai_assistant.api.server import app
        return TestClient(app)

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "0.1.0"

    def test_health_endpoint(self, client):
        """Test /health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    @patch("robotframework_ai_assistant.api.server.ai_service")
    def test_generate_test_data(self, mock_service, client):
        """Test test data generation endpoint."""
        mock_service.generate_test_data.return_value = [
            {"id": 1, "name": "Test User", "email": "test@example.com"}
        ]

        response = client.post(
            "/api/v1/test-data/generate",
            json={
                "data_type": "user",
                "count": 1,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert len(data["data"]) == 1

    @patch("robotframework_ai_assistant.api.server.ai_service")
    def test_generate_test_data_with_constraints(self, mock_service, client):
        """Test test data generation with constraints."""
        mock_service.generate_test_data.return_value = [
            {"id": 1, "name": "Adult", "age": 25}
        ]

        response = client.post(
            "/api/v1/test-data/generate",
            json={
                "data_type": "user",
                "count": 1,
                "constraints": {"age": "18-65"},
            },
        )

        assert response.status_code == 200
        mock_service.generate_test_data.assert_called_once()

    @patch("robotframework_ai_assistant.api.server.ai_service")
    def test_explore_environment(self, mock_service, client):
        """Test environment exploration endpoint."""
        mock_service.explore_environment.return_value = {
            "summary": "Test API",
            "components": ["REST API"],
            "test_areas": ["Authentication"],
            "recommendations": ["Test errors"],
            "risks": ["Security"],
        }

        response = client.post(
            "/api/v1/environment/explore",
            json={
                "environment_info": {"url": "https://api.example.com"},
                "exploration_type": "api",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["summary"] == "Test API"

    @patch("robotframework_ai_assistant.api.server.ai_service")
    def test_generate_test_cases(self, mock_service, client):
        """Test test case generation endpoint."""
        mock_service.generate_test_cases.return_value = [
            {
                "name": "Test Login",
                "description": "Test login",
                "steps": ["Open browser"],
                "priority": "high",
            }
        ]

        response = client.post(
            "/api/v1/test-cases/generate",
            json={
                "feature_description": "Login functionality",
                "test_type": "functional",
                "format_type": "robot",
                "count": 1,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1

    @patch("robotframework_ai_assistant.api.server.ai_service")
    def test_generate_test_report(self, mock_service, client):
        """Test test report generation endpoint."""
        mock_service.generate_test_report.return_value = {
            "title": "Test Report",
            "summary": "All tests passed",
            "statistics": {"total": 10, "passed": 10},
            "recommendations": ["Add more tests"],
        }

        response = client.post(
            "/api/v1/reports/generate",
            json={
                "test_results": [{"name": "Test1", "status": "passed"}],
                "report_type": "summary",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Report"

    @patch("robotframework_ai_assistant.api.server.ai_service")
    def test_analyze_for_jira(self, mock_service, client):
        """Test JIRA analysis endpoint."""
        mock_service.analyze_for_jira.return_value = [
            {
                "summary": "Bug: Test failure",
                "description": "Test failed",
                "issue_type": "Bug",
                "priority": "High",
            }
        ]

        response = client.post(
            "/api/v1/jira/analyze",
            json={
                "test_results": [{"name": "Test1", "error": "Failed"}],
                "project_key": "PROJ",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["suggestions"]) == 1

    @patch("robotframework_ai_assistant.api.server.ai_service")
    def test_generate_test_data_error(self, mock_service, client):
        """Test error handling in test data generation."""
        mock_service.generate_test_data.side_effect = ValueError("API key required")

        response = client.post(
            "/api/v1/test-data/generate",
            json={
                "data_type": "user",
                "count": 1,
            },
        )

        assert response.status_code == 400

    def test_openapi_docs(self, client):
        """Test OpenAPI documentation is available."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_redoc(self, client):
        """Test ReDoc documentation is available."""
        response = client.get("/redoc")
        assert response.status_code == 200
