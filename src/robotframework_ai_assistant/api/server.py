"""FastAPI server for Robot Framework AI Assistant."""

import os
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from robotframework_ai_assistant.ai_service import AIService

# Initialize FastAPI app
app = FastAPI(
    title="Robot Framework AI Assistant API",
    description="""
    AI-driven automation API for Robot Framework.

    This API provides endpoints for:
    - Test data generation using AI
    - Test environment exploration
    - Test case generation
    - Test report generation
    - JIRA/XRAY/Zephyr integration

    Use this API standalone or as a backend for the Robot Framework AI Assistant library.
    """,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI service with configuration from environment
ai_service = AIService(
    provider=os.getenv("LLM_PROVIDER", "openai"),
    model_name=os.getenv("LLM_MODEL", "gpt-4"),
    temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
)


# ==================== Request/Response Models ====================


class TestDataRequest(BaseModel):
    """Request model for test data generation."""

    data_type: str = Field(..., description="Type of data to generate (e.g., 'user', 'order', 'product')")
    count: int = Field(default=1, ge=1, le=100, description="Number of items to generate")
    constraints: Optional[dict[str, Any]] = Field(default=None, description="Optional constraints for the data")
    context: Optional[str] = Field(default=None, description="Additional context about the application")


class TestDataResponse(BaseModel):
    """Response model for test data generation."""

    data: list[dict[str, Any]]
    count: int


class EnvironmentExploreRequest(BaseModel):
    """Request model for environment exploration."""

    environment_info: dict[str, Any] = Field(..., description="Information about the environment")
    exploration_type: str = Field(
        default="general",
        description="Type of exploration: 'general', 'api', 'ui', 'database'",
    )


class EnvironmentExploreResponse(BaseModel):
    """Response model for environment exploration."""

    summary: Optional[str] = None
    components: Optional[list[str]] = None
    test_areas: Optional[list[str]] = None
    recommendations: Optional[list[str]] = None
    risks: Optional[list[str]] = None
    raw_response: Optional[str] = None


class TestCaseRequest(BaseModel):
    """Request model for test case generation."""

    feature_description: str = Field(..., description="Description of the feature to test")
    test_type: str = Field(
        default="functional",
        description="Type of tests: 'functional', 'integration', 'e2e', 'api'",
    )
    format_type: str = Field(
        default="robot",
        description="Output format: 'robot', 'gherkin', 'pytest'",
    )
    count: int = Field(default=5, ge=1, le=20, description="Number of test cases to generate")


class TestCase(BaseModel):
    """Model for a generated test case."""

    name: Optional[str] = None
    description: Optional[str] = None
    preconditions: Optional[list[str]] = None
    steps: Optional[list[str]] = None
    expected_results: Optional[list[str]] = None
    priority: Optional[str] = None
    tags: Optional[list[str]] = None
    code: Optional[str] = None


class TestCaseResponse(BaseModel):
    """Response model for test case generation."""

    test_cases: list[dict[str, Any]]
    count: int


class TestReportRequest(BaseModel):
    """Request model for test report generation."""

    test_results: list[dict[str, Any]] = Field(..., description="List of test results")
    report_type: str = Field(
        default="summary",
        description="Type of report: 'summary', 'detailed', 'executive'",
    )
    include_recommendations: bool = Field(default=True, description="Include improvement recommendations")


class TestReportResponse(BaseModel):
    """Response model for test report generation."""

    title: Optional[str] = None
    summary: Optional[str] = None
    statistics: Optional[dict[str, Any]] = None
    highlights: Optional[list[str]] = None
    failures_analysis: Optional[list[str]] = None
    recommendations: Optional[list[str]] = None
    trends: Optional[str] = None
    raw_response: Optional[str] = None


class JiraAnalysisRequest(BaseModel):
    """Request model for JIRA analysis."""

    test_results: list[dict[str, Any]] = Field(..., description="Test results to analyze")
    project_key: str = Field(..., description="JIRA project key")


class JiraTicketSuggestion(BaseModel):
    """Model for a JIRA ticket suggestion."""

    summary: Optional[str] = None
    description: Optional[str] = None
    issue_type: Optional[str] = None
    priority: Optional[str] = None
    labels: Optional[list[str]] = None
    components: Optional[list[str]] = None
    acceptance_criteria: Optional[list[str]] = None


class JiraAnalysisResponse(BaseModel):
    """Response model for JIRA analysis."""

    suggestions: list[dict[str, Any]]


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str
    version: str
    ai_configured: bool


# ==================== API Endpoints ====================


@app.get("/", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Check API health and configuration status."""
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        ai_configured=bool(os.getenv("OPENAI_API_KEY") or ai_service.api_key),
    )


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health():
    """Health check endpoint."""
    return await health_check()


@app.post("/api/v1/test-data/generate", response_model=TestDataResponse, tags=["Test Data"])
async def generate_test_data(request: TestDataRequest):
    """Generate test data using AI.

    Generate realistic test data based on the specified type and constraints.
    Supports various data types like users, orders, products, etc.
    """
    try:
        data = ai_service.generate_test_data(
            data_type=request.data_type,
            count=request.count,
            constraints=request.constraints,
            context=request.context,
        )
        return TestDataResponse(data=data, count=len(data))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate test data: {e!s}") from None


@app.post("/api/v1/environment/explore", response_model=EnvironmentExploreResponse, tags=["Environment"])
async def explore_environment(request: EnvironmentExploreRequest):
    """Explore and analyze a test environment using AI.

    Analyzes the provided environment information and provides insights,
    potential test areas, and recommendations.
    """
    try:
        result = ai_service.explore_environment(
            environment_info=request.environment_info,
            exploration_type=request.exploration_type,
        )
        return EnvironmentExploreResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to explore environment: {e!s}") from None


@app.post("/api/v1/test-cases/generate", response_model=TestCaseResponse, tags=["Test Cases"])
async def generate_test_cases(request: TestCaseRequest):
    """Generate test cases for a feature using AI.

    Generate comprehensive test cases based on the feature description.
    Supports multiple output formats including Robot Framework, Gherkin, and pytest.
    """
    try:
        test_cases = ai_service.generate_test_cases(
            feature_description=request.feature_description,
            test_type=request.test_type,
            format_type=request.format_type,
            count=request.count,
        )
        return TestCaseResponse(test_cases=test_cases, count=len(test_cases))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate test cases: {e!s}") from None


@app.post("/api/v1/reports/generate", response_model=TestReportResponse, tags=["Reports"])
async def generate_test_report(request: TestReportRequest):
    """Generate an AI-powered test report.

    Analyzes test results and generates an insightful report with
    statistics, failure analysis, and recommendations.
    """
    try:
        report = ai_service.generate_test_report(
            test_results=request.test_results,
            report_type=request.report_type,
            include_recommendations=request.include_recommendations,
        )
        return TestReportResponse(**report)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {e!s}") from None


@app.post("/api/v1/jira/analyze", response_model=JiraAnalysisResponse, tags=["JIRA Integration"])
async def analyze_for_jira(request: JiraAnalysisRequest):
    """Analyze test results and suggest JIRA tickets.

    Analyzes test failures and generates JIRA ticket suggestions
    with summaries, descriptions, priorities, and labels.
    """
    try:
        suggestions = ai_service.analyze_for_jira(
            test_results=request.test_results,
            project_key=request.project_key,
        )
        return JiraAnalysisResponse(suggestions=suggestions)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze for JIRA: {e!s}") from None


def main():
    """Run the API server."""
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")

    uvicorn.run(
        "robotframework_ai_assistant.api.server:app",
        host=host,
        port=port,
        reload=os.getenv("DEBUG", "false").lower() == "true",
    )


if __name__ == "__main__":
    main()
