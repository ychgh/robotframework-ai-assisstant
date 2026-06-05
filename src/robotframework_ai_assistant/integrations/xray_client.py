"""Xray integration client for Robot Framework AI Assistant."""

from typing import Any, Optional

import httpx


class XrayClient:
    """Client for Xray Cloud REST API integration."""

    XRAY_CLOUD_AUTH_URL = "https://xray.cloud.getxray.app/api/v2/authenticate"
    XRAY_CLOUD_BASE_URL = "https://xray.cloud.getxray.app/api/v2"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        timeout: float = 30.0,
    ):
        """Initialize the Xray client.

        Args:
            client_id: Xray Cloud client ID.
            client_secret: Xray Cloud client secret.
            timeout: Request timeout in seconds.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.timeout = timeout
        self._token: Optional[str] = None

    def _authenticate(self) -> str:
        """Authenticate with Xray Cloud and get bearer token.

        Returns:
            Bearer token.
        """
        if self._token:
            return self._token

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                self.XRAY_CLOUD_AUTH_URL,
                json={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
            )
            response.raise_for_status()
            self._token = response.text.strip('"')
            return self._token

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict[str, Any]] = None,
        files: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make a request to Xray API.

        Args:
            method: HTTP method.
            endpoint: API endpoint.
            data: Request body data.
            files: Files to upload.

        Returns:
            Response JSON.
        """
        token = self._authenticate()
        headers = {"Authorization": f"Bearer {token}"}

        url = f"{self.XRAY_CLOUD_BASE_URL}/{endpoint.lstrip('/')}"

        with httpx.Client(timeout=self.timeout) as client:
            if files:
                response = client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    files=files,
                )
            else:
                headers["Content-Type"] = "application/json"
                response = client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                )

            response.raise_for_status()

            if response.content:
                return response.json()
            return {"status": "success"}

    def import_execution(
        self,
        results_file: str,
        project_key: str,
        test_execution_key: Optional[str] = None,
    ) -> dict[str, Any]:
        """Import test execution results to Xray.

        Args:
            results_file: Path to results file (Robot Framework XML or JSON).
            project_key: JIRA project key.
            test_execution_key: Existing test execution to update.

        Returns:
            Import result.
        """
        # Determine format based on file extension
        is_robot_xml = results_file.endswith(".xml")

        with open(results_file, "rb") as f:
            file_content = f.read()

        if is_robot_xml:
            endpoint = "import/execution/robot"
            files = {"file": ("output.xml", file_content, "application/xml")}
        else:
            endpoint = "import/execution"
            files = {"file": ("results.json", file_content, "application/json")}

        # Add project key as query parameter
        endpoint = f"{endpoint}?projectKey={project_key}"

        if test_execution_key:
            endpoint = f"{endpoint}&testExecKey={test_execution_key}"

        return self._request("POST", endpoint, files=files)

    def create_test(
        self,
        summary: str,
        project_key: str,
        test_type: str = "Manual",
        steps: Optional[list[dict[str, str]]] = None,
    ) -> dict[str, Any]:
        """Create a test case in Xray.

        Args:
            summary: Test case summary.
            project_key: JIRA project key.
            test_type: Type of test ('Manual', 'Cucumber', 'Generic').
            steps: List of test steps with 'action' and 'result' keys.

        Returns:
            Created test details.
        """
        data: dict[str, Any] = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "issuetype": {"name": "Test"},
            }
        }

        # Add test type custom field
        data["fields"]["customfield_10001"] = {"value": test_type}

        if steps and test_type == "Manual":
            data["fields"]["customfield_10002"] = {
                "steps": [
                    {
                        "action": step.get("action", ""),
                        "data": step.get("data", ""),
                        "result": step.get("result", ""),
                    }
                    for step in steps
                ]
            }

        return self._request("POST", "test", data)

    def get_test(self, test_key: str) -> dict[str, Any]:
        """Get a test by key.

        Args:
            test_key: Test issue key.

        Returns:
            Test details.
        """
        return self._request("GET", f"test/{test_key}")

    def create_test_execution(
        self,
        project_key: str,
        summary: str,
        test_keys: list[str],
        description: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create a test execution.

        Args:
            project_key: JIRA project key.
            summary: Test execution summary.
            test_keys: List of test keys to include.
            description: Optional description.

        Returns:
            Created test execution details.
        """
        data = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "issuetype": {"name": "Test Execution"},
            }
        }

        if description:
            data["fields"]["description"] = {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": description}],
                    }
                ],
            }

        result = self._request("POST", "testexec", data)

        # Add tests to execution
        if test_keys and "key" in result:
            self.add_tests_to_execution(result["key"], test_keys)

        return result

    def add_tests_to_execution(
        self,
        test_execution_key: str,
        test_keys: list[str],
    ) -> dict[str, Any]:
        """Add tests to a test execution.

        Args:
            test_execution_key: Test execution key.
            test_keys: List of test keys to add.

        Returns:
            Result of the operation.
        """
        return self._request(
            "POST",
            f"testexec/{test_execution_key}/test",
            {"add": test_keys},
        )

    def update_test_run(
        self,
        test_run_id: str,
        status: str,
        comment: Optional[str] = None,
    ) -> dict[str, Any]:
        """Update a test run status.

        Args:
            test_run_id: Test run ID.
            status: New status ('PASS', 'FAIL', 'TODO', 'EXECUTING').
            comment: Optional comment.

        Returns:
            Update result.
        """
        data: dict[str, Any] = {"status": status}
        if comment:
            data["comment"] = comment

        return self._request("PUT", f"testrun/{test_run_id}", data)

    def get_test_runs(
        self,
        test_execution_key: str,
    ) -> dict[str, Any]:
        """Get test runs for a test execution.

        Args:
            test_execution_key: Test execution key.

        Returns:
            List of test runs.
        """
        return self._request("GET", f"testexec/{test_execution_key}/testrun")
