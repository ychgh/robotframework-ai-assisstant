"""Robot Framework AI Assistant Library.

This library provides AI-driven automation keywords for Robot Framework.
"""

import json
from typing import Any, Optional

from robot.api import logger
from robot.api.deco import keyword, library

from robotframework_ai_assistant.ai_service import AIService
from robotframework_ai_assistant.integrations.jira_client import JiraClient
from robotframework_ai_assistant.integrations.xray_client import XrayClient
from robotframework_ai_assistant.integrations.zephyr_client import ZephyrClient


@library(scope="GLOBAL", version="0.1.0")
class AIAssistantLibrary:
    """AI-driven automation library for Robot Framework.

    This library provides keywords for:
    - Test data generation using AI
    - Test environment exploration
    - Test case generation
    - Test report generation
    - Integration with JIRA, XRAY, and Zephyr

    = Configuration =

    The library requires an OpenAI API key, which can be provided in two ways:
    1. Set the ``OPENAI_API_KEY`` environment variable
    2. Pass ``api_key`` when importing the library

    = Example =

    | Library | AIAssistantLibrary | api_key=${API_KEY} |

    Or using environment variable:

    | Library | AIAssistantLibrary |

    = JIRA Integration =

    To use JIRA integration, provide JIRA credentials:
    | Library | AIAssistantLibrary | jira_url=https://your-jira.atlassian.net |
    | ...     | jira_username=${JIRA_USER} | jira_api_token=${JIRA_TOKEN} |
    """

    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    ROBOT_LIBRARY_VERSION = "0.1.0"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gpt-4",
        temperature: float = 0.7,
        jira_url: Optional[str] = None,
        jira_username: Optional[str] = None,
        jira_api_token: Optional[str] = None,
        xray_client_id: Optional[str] = None,
        xray_client_secret: Optional[str] = None,
        zephyr_api_token: Optional[str] = None,
    ):
        """Initialize the AI Assistant Library.

        Args:
            api_key: OpenAI API key. Defaults to OPENAI_API_KEY env var.
            model_name: OpenAI model to use. Defaults to 'gpt-4'.
            temperature: Generation temperature. Defaults to 0.7.
            jira_url: JIRA instance URL for integration.
            jira_username: JIRA username/email for integration.
            jira_api_token: JIRA API token for integration.
            xray_client_id: Xray Cloud client ID.
            xray_client_secret: Xray Cloud client secret.
            zephyr_api_token: Zephyr Scale API token.
        """
        self._ai_service = AIService(
            model_name=model_name,
            temperature=temperature,
            api_key=api_key,
        )

        self._jira_client: Optional[JiraClient] = None
        if jira_url and jira_username and jira_api_token:
            self._jira_client = JiraClient(
                url=jira_url,
                username=jira_username,
                api_token=jira_api_token,
            )

        self._xray_client: Optional[XrayClient] = None
        if xray_client_id and xray_client_secret:
            self._xray_client = XrayClient(
                client_id=xray_client_id,
                client_secret=xray_client_secret,
            )

        self._zephyr_client: Optional[ZephyrClient] = None
        if zephyr_api_token and jira_url:
            self._zephyr_client = ZephyrClient(
                api_token=zephyr_api_token,
                jira_url=jira_url,
            )

    # ==================== Test Data Generation Keywords ====================

    @keyword("Generate Test Data")
    def generate_test_data(
        self,
        data_type: str,
        count: int = 1,
        constraints: Optional[str] = None,
        context: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Generate test data using AI.

        Generates realistic test data based on the specified type and constraints.

        Args:
            data_type: Type of data to generate (e.g., 'user', 'order', 'product').
            count: Number of data items to generate. Defaults to 1.
            constraints: JSON string with constraints (e.g., '{"age": "18-65"}').
            context: Additional context about the application.

        Returns:
            List of generated test data dictionaries.

        Example:
        | ${users}= | Generate Test Data | user | count=5 |
        | ${orders}= | Generate Test Data | order | constraints={"status": "pending"} |
        """
        logger.info(f"Generating {count} test data item(s) of type '{data_type}'")

        constraints_dict = None
        if constraints:
            try:
                constraints_dict = json.loads(constraints)
            except json.JSONDecodeError:
                logger.warn(f"Invalid constraints JSON: {constraints}")

        result = self._ai_service.generate_test_data(
            data_type=data_type,
            count=int(count),
            constraints=constraints_dict,
            context=context,
        )

        logger.info(f"Generated {len(result)} test data item(s)")
        return result

    @keyword("Generate User Data")
    def generate_user_data(
        self,
        count: int = 1,
        locale: str = "en_US",
        include_address: bool = True,
    ) -> list[dict[str, Any]]:
        """Generate realistic user test data.

        Args:
            count: Number of users to generate.
            locale: Locale for name/address generation.
            include_address: Whether to include address information.

        Returns:
            List of generated user data.

        Example:
        | ${users}= | Generate User Data | count=10 | locale=en_US |
        """
        constraints = {
            "locale": locale,
            "include_address": include_address,
            "fields": ["first_name", "last_name", "email", "phone", "username"],
        }
        if include_address:
            constraints["fields"].extend(["street", "city", "state", "zip_code", "country"])

        return self._ai_service.generate_test_data(
            data_type="user",
            count=int(count),
            constraints=constraints,
        )

    # ==================== Environment Exploration Keywords ====================

    @keyword("Explore Test Environment")
    def explore_test_environment(
        self,
        environment_info: str,
        exploration_type: str = "general",
    ) -> dict[str, Any]:
        """Explore and analyze a test environment using AI.

        Analyzes the provided environment information and provides insights,
        potential test areas, and recommendations.

        Args:
            environment_info: JSON string with environment details.
            exploration_type: Type of exploration ('general', 'api', 'ui', 'database').

        Returns:
            Analysis and recommendations for the environment.

        Example:
        | ${env_info}= | Create Dictionary | url=https://api.example.com | type=REST |
        | ${analysis}= | Explore Test Environment | ${env_info} | api |
        """
        logger.info(f"Exploring {exploration_type} environment")

        try:
            env_dict = json.loads(environment_info) if isinstance(environment_info, str) else environment_info
        except json.JSONDecodeError:
            env_dict = {"description": environment_info}

        result = self._ai_service.explore_environment(
            environment_info=env_dict,
            exploration_type=exploration_type,
        )

        logger.info(f"Environment exploration complete: {result.get('summary', 'N/A')}")
        return result

    @keyword("Analyze API Endpoints")
    def analyze_api_endpoints(
        self,
        api_spec: str,
    ) -> dict[str, Any]:
        """Analyze API endpoints and suggest test scenarios.

        Args:
            api_spec: API specification (OpenAPI/Swagger JSON or description).

        Returns:
            Analysis with suggested test scenarios for each endpoint.

        Example:
        | ${spec}= | Get File | openapi.json |
        | ${analysis}= | Analyze API Endpoints | ${spec} |
        """
        return self._ai_service.explore_environment(
            environment_info={"api_specification": api_spec},
            exploration_type="api",
        )

    # ==================== Test Case Generation Keywords ====================

    @keyword("Generate Test Cases")
    def generate_test_cases(
        self,
        feature_description: str,
        test_type: str = "functional",
        format_type: str = "robot",
        count: int = 5,
    ) -> list[dict[str, Any]]:
        """Generate test cases for a feature using AI.

        Args:
            feature_description: Description of the feature to test.
            test_type: Type of tests ('functional', 'integration', 'e2e', 'api').
            format_type: Output format ('robot', 'gherkin', 'pytest').
            count: Number of test cases to generate.

        Returns:
            List of generated test cases.

        Example:
        | ${tests}= | Generate Test Cases | User login with email and password | functional |
        | ${api_tests}= | Generate Test Cases | REST API for user management | api | robot | 10 |
        """
        logger.info(f"Generating {count} {test_type} test cases for: {feature_description[:50]}...")

        result = self._ai_service.generate_test_cases(
            feature_description=feature_description,
            test_type=test_type,
            format_type=format_type,
            count=int(count),
        )

        logger.info(f"Generated {len(result)} test cases")
        return result

    @keyword("Generate Robot Test Suite")
    def generate_robot_test_suite(
        self,
        feature_description: str,
        suite_name: str = "Generated Tests",
        tags: Optional[str] = None,
    ) -> str:
        """Generate a complete Robot Framework test suite.

        Args:
            feature_description: Description of the feature to test.
            suite_name: Name for the test suite.
            tags: Comma-separated tags to apply to all tests.

        Returns:
            Robot Framework test suite content as string.

        Example:
        | ${suite}= | Generate Robot Test Suite | Login functionality | Login Tests |
        | Create File | login_tests.robot | ${suite} |
        """
        test_cases = self._ai_service.generate_test_cases(
            feature_description=feature_description,
            test_type="functional",
            format_type="robot",
            count=5,
        )

        tag_list = [t.strip() for t in tags.split(",")] if tags else []

        suite_content = f"""*** Settings ***
Documentation    {suite_name} - Auto-generated test suite
Library          SeleniumLibrary
Library          AIAssistantLibrary

*** Variables ***
${{BASE_URL}}    http://localhost

*** Test Cases ***
"""
        for tc in test_cases:
            if isinstance(tc, dict) and "name" in tc:
                suite_content += f"\n{tc['name']}\n"
                suite_content += f"    [Documentation]    {tc.get('description', 'Generated test case')}\n"

                all_tags = tag_list + tc.get("tags", [])
                if all_tags:
                    suite_content += f"    [Tags]    {'    '.join(all_tags)}\n"

                for step in tc.get("steps", ["Log    Test step placeholder"]):
                    suite_content += f"    {step}\n"

        return suite_content

    # ==================== Test Report Generation Keywords ====================

    @keyword("Generate Test Report")
    def generate_test_report(
        self,
        test_results: str,
        report_type: str = "summary",
        include_recommendations: bool = True,
    ) -> dict[str, Any]:
        """Generate an AI-powered test report.

        Analyzes test results and generates an insightful report with
        statistics, failure analysis, and recommendations.

        Args:
            test_results: JSON string of test results or path to results file.
            report_type: Type of report ('summary', 'detailed', 'executive').
            include_recommendations: Whether to include improvement recommendations.

        Returns:
            Generated test report as dictionary.

        Example:
        | ${results}= | Get File | test_results.json |
        | ${report}= | Generate Test Report | ${results} | detailed |
        """
        logger.info(f"Generating {report_type} test report")

        try:
            results_list = json.loads(test_results) if isinstance(test_results, str) else test_results
        except json.JSONDecodeError:
            results_list = [{"raw_input": test_results}]

        result = self._ai_service.generate_test_report(
            test_results=results_list,
            report_type=report_type,
            include_recommendations=include_recommendations,
        )

        logger.info("Test report generated successfully")
        return result

    @keyword("Analyze Test Failures")
    def analyze_test_failures(
        self,
        failures: str,
    ) -> dict[str, Any]:
        """Analyze test failures and provide insights.

        Args:
            failures: JSON string of failed test cases with error details.

        Returns:
            Analysis of failures with root cause suggestions.

        Example:
        | ${failures}= | Get Failed Tests |
        | ${analysis}= | Analyze Test Failures | ${failures} |
        """
        try:
            failures_list = json.loads(failures) if isinstance(failures, str) else failures
        except json.JSONDecodeError:
            failures_list = [{"error": failures}]

        return self._ai_service.generate_test_report(
            test_results=failures_list,
            report_type="detailed",
            include_recommendations=True,
        )

    # ==================== JIRA Integration Keywords ====================

    @keyword("Create JIRA Issue From Failure")
    def create_jira_issue_from_failure(
        self,
        test_name: str,
        error_message: str,
        project_key: str,
        additional_info: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create a JIRA issue from a test failure.

        Args:
            test_name: Name of the failed test.
            error_message: Error message from the failure.
            project_key: JIRA project key.
            additional_info: Additional context as JSON string.

        Returns:
            Created JIRA issue details.

        Example:
        | ${issue}= | Create JIRA Issue From Failure | Login Test Failed |
        | ...       | Expected 200 but got 401 | PROJ |
        """
        if not self._jira_client:
            raise RuntimeError("JIRA client not configured. Provide JIRA credentials when importing library.")

        # Use AI to generate a better issue description
        suggestions = self._ai_service.analyze_for_jira(
            test_results=[{
                "test_name": test_name,
                "error": error_message,
                "additional_info": additional_info,
            }],
            project_key=project_key,
        )

        if suggestions and isinstance(suggestions[0], dict):
            suggestion = suggestions[0]
            return self._jira_client.create_issue(
                project_key=project_key,
                summary=suggestion.get("summary", f"Test Failure: {test_name}"),
                description=suggestion.get("description", error_message),
                issue_type=suggestion.get("issue_type", "Bug"),
                priority=suggestion.get("priority", "Medium"),
                labels=suggestion.get("labels", ["automated-test", "failure"]),
            )

        return self._jira_client.create_issue(
            project_key=project_key,
            summary=f"Test Failure: {test_name}",
            description=f"Error: {error_message}\n\nAdditional Info: {additional_info or 'N/A'}",
            issue_type="Bug",
        )

    @keyword("Link Test To JIRA Issue")
    def link_test_to_jira_issue(
        self,
        test_id: str,
        issue_key: str,
    ) -> dict[str, Any]:
        """Link a test case to a JIRA issue.

        Args:
            test_id: Test case identifier.
            issue_key: JIRA issue key (e.g., 'PROJ-123').

        Returns:
            Link details.

        Example:
        | ${result}= | Link Test To JIRA Issue | TC001 | PROJ-123 |
        """
        if not self._jira_client:
            raise RuntimeError("JIRA client not configured.")

        return self._jira_client.add_comment(
            issue_key=issue_key,
            comment=f"Linked test case: {test_id}",
        )

    @keyword("Get JIRA Issue")
    def get_jira_issue(self, issue_key: str) -> dict[str, Any]:
        """Get details of a JIRA issue.

        Args:
            issue_key: JIRA issue key (e.g., 'PROJ-123').

        Returns:
            JIRA issue details.

        Example:
        | ${issue}= | Get JIRA Issue | PROJ-123 |
        | Log | Issue summary: ${issue}[summary] |
        """
        if not self._jira_client:
            raise RuntimeError("JIRA client not configured.")

        return self._jira_client.get_issue(issue_key)

    # ==================== XRAY Integration Keywords ====================

    @keyword("Import Test Execution To Xray")
    def import_test_execution_to_xray(
        self,
        results_file: str,
        project_key: str,
        test_execution_key: Optional[str] = None,
    ) -> dict[str, Any]:
        """Import test execution results to Xray.

        Args:
            results_file: Path to Robot Framework output.xml or JSON results.
            project_key: JIRA project key.
            test_execution_key: Existing test execution key to update.

        Returns:
            Import result with test execution details.

        Example:
        | ${result}= | Import Test Execution To Xray | output.xml | PROJ |
        """
        if not self._xray_client:
            raise RuntimeError("Xray client not configured. Provide Xray credentials when importing library.")

        return self._xray_client.import_execution(
            results_file=results_file,
            project_key=project_key,
            test_execution_key=test_execution_key,
        )

    @keyword("Create Xray Test")
    def create_xray_test(
        self,
        summary: str,
        project_key: str,
        test_type: str = "Manual",
        steps: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create a test case in Xray.

        Args:
            summary: Test case summary.
            project_key: JIRA project key.
            test_type: Type of test ('Manual', 'Cucumber', 'Generic').
            steps: JSON array of test steps.

        Returns:
            Created test details.

        Example:
        | ${test}= | Create Xray Test | Login with valid credentials | PROJ |
        """
        if not self._xray_client:
            raise RuntimeError("Xray client not configured.")

        steps_list = None
        if steps:
            try:
                steps_list = json.loads(steps)
            except json.JSONDecodeError:
                steps_list = [{"action": steps, "result": "Expected result"}]

        return self._xray_client.create_test(
            summary=summary,
            project_key=project_key,
            test_type=test_type,
            steps=steps_list,
        )

    # ==================== Zephyr Integration Keywords ====================

    @keyword("Create Zephyr Test Cycle")
    def create_zephyr_test_cycle(
        self,
        name: str,
        project_key: str,
        description: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create a test cycle in Zephyr Scale.

        Args:
            name: Test cycle name.
            project_key: JIRA project key.
            description: Optional description.

        Returns:
            Created test cycle details.

        Example:
        | ${cycle}= | Create Zephyr Test Cycle | Sprint 1 Regression | PROJ |
        """
        if not self._zephyr_client:
            raise RuntimeError("Zephyr client not configured. Provide Zephyr credentials when importing library.")

        return self._zephyr_client.create_test_cycle(
            name=name,
            project_key=project_key,
            description=description,
        )

    @keyword("Add Test To Zephyr Cycle")
    def add_test_to_zephyr_cycle(
        self,
        test_case_key: str,
        test_cycle_key: str,
    ) -> dict[str, Any]:
        """Add a test case to a Zephyr test cycle.

        Args:
            test_case_key: Test case key.
            test_cycle_key: Test cycle key.

        Returns:
            Result of adding the test.

        Example:
        | ${result}= | Add Test To Zephyr Cycle | PROJ-T1 | PROJ-C1 |
        """
        if not self._zephyr_client:
            raise RuntimeError("Zephyr client not configured.")

        return self._zephyr_client.add_test_to_cycle(
            test_case_key=test_case_key,
            test_cycle_key=test_cycle_key,
        )

    @keyword("Update Zephyr Execution")
    def update_zephyr_execution(
        self,
        execution_id: str,
        status: str,
        comment: Optional[str] = None,
    ) -> dict[str, Any]:
        """Update a Zephyr test execution status.

        Args:
            execution_id: Execution ID.
            status: New status ('Pass', 'Fail', 'Blocked', 'Not Executed').
            comment: Optional comment.

        Returns:
            Updated execution details.

        Example:
        | ${result}= | Update Zephyr Execution | 12345 | Pass | Test passed successfully |
        """
        if not self._zephyr_client:
            raise RuntimeError("Zephyr client not configured.")

        return self._zephyr_client.update_execution(
            execution_id=execution_id,
            status=status,
            comment=comment,
        )
