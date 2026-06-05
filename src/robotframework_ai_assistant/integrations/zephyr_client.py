"""Zephyr Scale integration client for Robot Framework AI Assistant."""

from typing import Any, Optional

import httpx


class ZephyrClient:
    """Client for Zephyr Scale REST API integration."""

    def __init__(
        self,
        api_token: str,
        jira_url: str,
        timeout: float = 30.0,
    ):
        """Initialize the Zephyr client.

        Args:
            api_token: Zephyr Scale API token.
            jira_url: JIRA instance URL.
            timeout: Request timeout in seconds.
        """
        self.api_token = api_token
        self.jira_url = jira_url.rstrip("/")
        self.timeout = timeout

        # Determine if using Cloud or Server
        if "atlassian.net" in jira_url:
            self.base_url = "https://api.zephyrscale.smartbear.com/v2"
        else:
            self.base_url = f"{self.jira_url}/rest/atm/1.0"

        self._headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make a request to Zephyr Scale API.

        Args:
            method: HTTP method.
            endpoint: API endpoint.
            data: Request body data.
            params: Query parameters.

        Returns:
            Response JSON.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        with httpx.Client(timeout=self.timeout) as client:
            response = client.request(
                method=method,
                url=url,
                headers=self._headers,
                json=data,
                params=params,
            )
            response.raise_for_status()

            if response.content:
                return response.json()
            return {"status": "success"}

    def create_test_cycle(
        self,
        name: str,
        project_key: str,
        description: Optional[str] = None,
        folder_id: Optional[int] = None,
    ) -> dict[str, Any]:
        """Create a test cycle.

        Args:
            name: Test cycle name.
            project_key: JIRA project key.
            description: Optional description.
            folder_id: Optional folder ID.

        Returns:
            Created test cycle details.
        """
        data: dict[str, Any] = {
            "name": name,
            "projectKey": project_key,
        }

        if description:
            data["description"] = description

        if folder_id:
            data["folderId"] = folder_id

        return self._request("POST", "testcycles", data)

    def get_test_cycle(self, cycle_key: str) -> dict[str, Any]:
        """Get a test cycle by key.

        Args:
            cycle_key: Test cycle key.

        Returns:
            Test cycle details.
        """
        return self._request("GET", f"testcycles/{cycle_key}")

    def list_test_cycles(
        self,
        project_key: str,
        max_results: int = 50,
    ) -> dict[str, Any]:
        """List test cycles for a project.

        Args:
            project_key: JIRA project key.
            max_results: Maximum number of results.

        Returns:
            List of test cycles.
        """
        return self._request(
            "GET",
            "testcycles",
            params={"projectKey": project_key, "maxResults": max_results},
        )

    def create_test_case(
        self,
        name: str,
        project_key: str,
        objective: Optional[str] = None,
        precondition: Optional[str] = None,
        priority: str = "Normal",
        status: str = "Draft",
        labels: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """Create a test case.

        Args:
            name: Test case name.
            project_key: JIRA project key.
            objective: Test objective.
            precondition: Test precondition.
            priority: Priority ('Low', 'Normal', 'High').
            status: Status ('Draft', 'Approved', 'Deprecated').
            labels: List of labels.

        Returns:
            Created test case details.
        """
        data: dict[str, Any] = {
            "name": name,
            "projectKey": project_key,
            "priority": priority,
            "status": status,
        }

        if objective:
            data["objective"] = objective

        if precondition:
            data["precondition"] = precondition

        if labels:
            data["labels"] = labels

        return self._request("POST", "testcases", data)

    def get_test_case(self, test_case_key: str) -> dict[str, Any]:
        """Get a test case by key.

        Args:
            test_case_key: Test case key.

        Returns:
            Test case details.
        """
        return self._request("GET", f"testcases/{test_case_key}")

    def add_test_to_cycle(
        self,
        test_case_key: str,
        test_cycle_key: str,
    ) -> dict[str, Any]:
        """Add a test case to a test cycle.

        Args:
            test_case_key: Test case key.
            test_cycle_key: Test cycle key.

        Returns:
            Result of adding the test.
        """
        data = {
            "testCaseKey": test_case_key,
        }
        return self._request(
            "POST",
            f"testcycles/{test_cycle_key}/testruns",
            data,
        )

    def create_execution(
        self,
        test_case_key: str,
        test_cycle_key: str,
        status: str = "Not Executed",
        comment: Optional[str] = None,
        environment: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create a test execution.

        Args:
            test_case_key: Test case key.
            test_cycle_key: Test cycle key.
            status: Execution status.
            comment: Optional comment.
            environment: Optional environment name.

        Returns:
            Created execution details.
        """
        data: dict[str, Any] = {
            "testCaseKey": test_case_key,
            "testCycleKey": test_cycle_key,
            "statusName": status,
        }

        if comment:
            data["comment"] = comment

        if environment:
            data["environment"] = environment

        return self._request("POST", "testexecutions", data)

    def update_execution(
        self,
        execution_id: str,
        status: str,
        comment: Optional[str] = None,
    ) -> dict[str, Any]:
        """Update a test execution.

        Args:
            execution_id: Execution ID.
            status: New status ('Pass', 'Fail', 'Blocked', 'Not Executed').
            comment: Optional comment.

        Returns:
            Updated execution details.
        """
        data: dict[str, Any] = {"statusName": status}

        if comment:
            data["comment"] = comment

        return self._request("PUT", f"testexecutions/{execution_id}", data)

    def get_execution(self, execution_id: str) -> dict[str, Any]:
        """Get a test execution.

        Args:
            execution_id: Execution ID.

        Returns:
            Execution details.
        """
        return self._request("GET", f"testexecutions/{execution_id}")

    def list_executions(
        self,
        project_key: str,
        test_cycle_key: Optional[str] = None,
        max_results: int = 50,
    ) -> dict[str, Any]:
        """List test executions.

        Args:
            project_key: JIRA project key.
            test_cycle_key: Optional test cycle to filter by.
            max_results: Maximum number of results.

        Returns:
            List of executions.
        """
        params: dict[str, Any] = {
            "projectKey": project_key,
            "maxResults": max_results,
        }

        if test_cycle_key:
            params["testCycleKey"] = test_cycle_key

        return self._request("GET", "testexecutions", params=params)

    def add_test_step(
        self,
        test_case_key: str,
        description: str,
        expected_result: str,
        test_data: Optional[str] = None,
    ) -> dict[str, Any]:
        """Add a test step to a test case.

        Args:
            test_case_key: Test case key.
            description: Step description.
            expected_result: Expected result.
            test_data: Optional test data.

        Returns:
            Created step details.
        """
        data: dict[str, Any] = {
            "description": description,
            "expectedResult": expected_result,
        }

        if test_data:
            data["testData"] = test_data

        return self._request(
            "POST",
            f"testcases/{test_case_key}/teststeps",
            data,
        )
