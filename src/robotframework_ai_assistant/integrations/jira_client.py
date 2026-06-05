"""JIRA integration client for Robot Framework AI Assistant."""

import base64
from typing import Any, Optional

import httpx


class JiraClient:
    """Client for JIRA REST API integration."""

    def __init__(
        self,
        url: str,
        username: str,
        api_token: str,
        timeout: float = 30.0,
    ):
        """Initialize the JIRA client.

        Args:
            url: JIRA instance URL (e.g., 'https://your-domain.atlassian.net').
            username: JIRA username or email.
            api_token: JIRA API token.
            timeout: Request timeout in seconds.
        """
        self.url = url.rstrip("/")
        self.username = username
        self.api_token = api_token
        self.timeout = timeout

        # Create basic auth header
        credentials = f"{username}:{api_token}"
        encoded = base64.b64encode(credentials.encode()).decode()
        self._headers = {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make a request to JIRA API.

        Args:
            method: HTTP method.
            endpoint: API endpoint.
            data: Request body data.

        Returns:
            Response JSON.
        """
        url = f"{self.url}/rest/api/3/{endpoint.lstrip('/')}"

        with httpx.Client(timeout=self.timeout) as client:
            response = client.request(
                method=method,
                url=url,
                headers=self._headers,
                json=data,
            )
            response.raise_for_status()

            if response.content:
                return response.json()
            return {"status": "success"}

    def create_issue(
        self,
        project_key: str,
        summary: str,
        description: str,
        issue_type: str = "Bug",
        priority: Optional[str] = None,
        labels: Optional[list[str]] = None,
        components: Optional[list[str]] = None,
        assignee: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create a JIRA issue.

        Args:
            project_key: Project key (e.g., 'PROJ').
            summary: Issue summary.
            description: Issue description.
            issue_type: Issue type (e.g., 'Bug', 'Task', 'Story').
            priority: Priority name (e.g., 'High', 'Medium', 'Low').
            labels: List of labels.
            components: List of component names.
            assignee: Assignee account ID.

        Returns:
            Created issue details.
        """
        fields: dict[str, Any] = {
            "project": {"key": project_key},
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": description}],
                    }
                ],
            },
            "issuetype": {"name": issue_type},
        }

        if priority:
            fields["priority"] = {"name": priority}

        if labels:
            fields["labels"] = labels

        if components:
            fields["components"] = [{"name": c} for c in components]

        if assignee:
            fields["assignee"] = {"accountId": assignee}

        return self._request("POST", "issue", {"fields": fields})

    def get_issue(self, issue_key: str) -> dict[str, Any]:
        """Get a JIRA issue by key.

        Args:
            issue_key: Issue key (e.g., 'PROJ-123').

        Returns:
            Issue details.
        """
        return self._request("GET", f"issue/{issue_key}")

    def update_issue(
        self,
        issue_key: str,
        fields: dict[str, Any],
    ) -> dict[str, Any]:
        """Update a JIRA issue.

        Args:
            issue_key: Issue key.
            fields: Fields to update.

        Returns:
            Update result.
        """
        return self._request("PUT", f"issue/{issue_key}", {"fields": fields})

    def add_comment(
        self,
        issue_key: str,
        comment: str,
    ) -> dict[str, Any]:
        """Add a comment to a JIRA issue.

        Args:
            issue_key: Issue key.
            comment: Comment text.

        Returns:
            Created comment details.
        """
        data = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": comment}],
                    }
                ],
            }
        }
        return self._request("POST", f"issue/{issue_key}/comment", data)

    def search_issues(
        self,
        jql: str,
        max_results: int = 50,
        fields: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """Search for issues using JQL.

        Args:
            jql: JQL query string.
            max_results: Maximum number of results.
            fields: List of fields to return.

        Returns:
            Search results.
        """
        data = {
            "jql": jql,
            "maxResults": max_results,
        }
        if fields:
            data["fields"] = fields

        return self._request("POST", "search", data)

    def transition_issue(
        self,
        issue_key: str,
        transition_id: str,
        comment: Optional[str] = None,
    ) -> dict[str, Any]:
        """Transition an issue to a new status.

        Args:
            issue_key: Issue key.
            transition_id: Transition ID.
            comment: Optional comment.

        Returns:
            Transition result.
        """
        data: dict[str, Any] = {"transition": {"id": transition_id}}

        if comment:
            data["update"] = {
                "comment": [
                    {
                        "add": {
                            "body": {
                                "type": "doc",
                                "version": 1,
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [{"type": "text", "text": comment}],
                                    }
                                ],
                            }
                        }
                    }
                ]
            }

        return self._request("POST", f"issue/{issue_key}/transitions", data)

    def get_transitions(self, issue_key: str) -> dict[str, Any]:
        """Get available transitions for an issue.

        Args:
            issue_key: Issue key.

        Returns:
            Available transitions.
        """
        return self._request("GET", f"issue/{issue_key}/transitions")
