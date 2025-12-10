"""AI Service for generating test data, test cases, and reports using LangChain."""

from typing import Any, Optional

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate

from robotframework_ai_assistant.providers.factory import LLMProviderFactory

load_dotenv()


class AIService:
    """Service for AI-powered test automation features using LangChain.

    Supports multiple LLM providers including OpenAI, Anthropic (Claude), Google (Gemini),
    Azure OpenAI, and Ollama for local models.
    """

    def __init__(
        self,
        provider: str = "openai",
        model_name: str = "gpt-4",
        temperature: float = 0.7,
        api_key: Optional[str] = None,
        **provider_kwargs: Any,
    ):
        """Initialize the AI service.

        Args:
            provider: LLM provider name ('openai', 'anthropic', 'google', 'azure', 'ollama').
            model_name: Model name for the selected provider.
            temperature: Temperature for generation (0.0 to 1.0).
            api_key: API key for the provider. Defaults to provider-specific env var.
            **provider_kwargs: Additional provider-specific parameters
                (e.g., azure_endpoint for Azure, base_url for Ollama).

        Examples:
            # OpenAI (default)
            service = AIService(provider="openai", model_name="gpt-4")

            # Anthropic Claude
            service = AIService(provider="anthropic", model_name="claude-3-opus-20240229")

            # Google Gemini
            service = AIService(provider="google", model_name="gemini-pro")

            # Azure OpenAI
            service = AIService(
                provider="azure",
                model_name="my-deployment",
                azure_endpoint="https://my-resource.openai.azure.com"
            )

            # Ollama (local)
            service = AIService(provider="ollama", model_name="llama2", base_url="http://localhost:11434")
        """
        self.provider_name = provider
        self.model_name = model_name
        self.temperature = temperature
        self.api_key = api_key
        self.provider_kwargs = provider_kwargs

        self._provider = LLMProviderFactory.create_provider(
            provider=provider,
            model_name=model_name,
            temperature=temperature,
            api_key=api_key,
            **provider_kwargs,
        )

    @property
    def llm(self) -> Any:
        """Get or create the LLM instance.

        Returns:
            LangChain-compatible LLM instance from the configured provider.
        """
        return self._provider.get_llm()

    def generate_test_data(
        self,
        data_type: str,
        count: int = 1,
        constraints: Optional[dict[str, Any]] = None,
        context: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Generate test data using AI.

        Args:
            data_type: Type of data to generate (e.g., 'user', 'order', 'product').
            count: Number of data items to generate.
            constraints: Optional constraints for the data (e.g., {'age': '18-65'}).
            context: Optional context about the application.

        Returns:
            List of generated test data dictionaries.
        """
        constraints_str = ""
        if constraints:
            constraints_str = "\n".join(f"- {k}: {v}" for k, v in constraints.items())
            constraints_str = f"\nConstraints:\n{constraints_str}"

        context_str = f"\nContext: {context}" if context else ""

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a test data generator. Generate realistic test data in JSON format.
Always return valid JSON array with the requested number of items.
Each item should be a JSON object with appropriate fields for the data type."""),
            ("user", """Generate {count} test data item(s) of type '{data_type}'.{constraints}{context}

Return ONLY a valid JSON array, no explanations or markdown.""")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "count": count,
            "data_type": data_type,
            "constraints": constraints_str,
            "context": context_str,
        })

        import json
        try:
            content = response.content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1]
                content = content.rsplit("```", 1)[0]
            return json.loads(content)
        except json.JSONDecodeError:
            return [{"raw_response": response.content}]

    def explore_environment(
        self,
        environment_info: dict[str, Any],
        exploration_type: str = "general",
    ) -> dict[str, Any]:
        """Explore and analyze a test environment.

        Args:
            environment_info: Information about the environment to explore.
            exploration_type: Type of exploration ('general', 'api', 'ui', 'database').

        Returns:
            Analysis and recommendations for the environment.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a QA automation expert analyzing test environments.
Provide insights about the environment, potential test areas, and recommendations.
Return your analysis as a JSON object with the following structure:
{{
    "summary": "Brief summary of the environment",
    "components": ["list of identified components"],
    "test_areas": ["potential areas for testing"],
    "recommendations": ["testing recommendations"],
    "risks": ["potential risks or concerns"]
}}"""),
            ("user", """Analyze this {exploration_type} environment:
{environment_info}

Return ONLY valid JSON, no explanations or markdown.""")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "exploration_type": exploration_type,
            "environment_info": str(environment_info),
        })

        import json
        try:
            content = response.content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1]
                content = content.rsplit("```", 1)[0]
            return json.loads(content)
        except json.JSONDecodeError:
            return {"raw_response": response.content}

    def generate_test_cases(
        self,
        feature_description: str,
        test_type: str = "functional",
        format_type: str = "robot",
        count: int = 5,
    ) -> list[dict[str, Any]]:
        """Generate test cases for a given feature.

        Args:
            feature_description: Description of the feature to test.
            test_type: Type of tests ('functional', 'integration', 'e2e', 'api').
            format_type: Output format ('robot', 'gherkin', 'pytest').
            count: Number of test cases to generate.

        Returns:
            List of generated test cases.
        """
        format_examples = {
            "robot": """Example Robot Framework format:
*** Test Cases ***
Test Case Name
    [Documentation]    Description
    [Tags]    tag1    tag2
    Step 1
    Step 2""",
            "gherkin": """Example Gherkin format:
Feature: Feature Name
  Scenario: Scenario Name
    Given precondition
    When action
    Then expected result""",
            "pytest": """Example pytest format:
def test_case_name():
    \"\"\"Description\"\"\"
    # Arrange
    # Act
    # Assert""",
        }

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a QA test engineer expert. Generate comprehensive test cases.
Return your response as a JSON array with the following structure for each test case:
{{
    "name": "Test case name",
    "description": "Test case description",
    "preconditions": ["list of preconditions"],
    "steps": ["step 1", "step 2"],
    "expected_results": ["expected result 1"],
    "priority": "high/medium/low",
    "tags": ["tag1", "tag2"],
    "code": "formatted test code in the requested format"
}}"""),
            ("user", """Generate {count} {test_type} test cases for the following feature:
{feature_description}

Format: {format_type}
{format_example}

Return ONLY valid JSON array, no explanations or markdown.""")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "count": count,
            "test_type": test_type,
            "feature_description": feature_description,
            "format_type": format_type,
            "format_example": format_examples.get(format_type, ""),
        })

        import json
        try:
            content = response.content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1]
                content = content.rsplit("```", 1)[0]
            return json.loads(content)
        except json.JSONDecodeError:
            return [{"raw_response": response.content}]

    def generate_test_report(
        self,
        test_results: list[dict[str, Any]],
        report_type: str = "summary",
        include_recommendations: bool = True,
    ) -> dict[str, Any]:
        """Generate an AI-powered test report.

        Args:
            test_results: List of test results to analyze.
            report_type: Type of report ('summary', 'detailed', 'executive').
            include_recommendations: Whether to include improvement recommendations.

        Returns:
            Generated test report.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a QA reporting specialist. Analyze test results and generate insightful reports.
Return your report as a JSON object with the following structure:
{{
    "title": "Report title",
    "summary": "Executive summary",
    "statistics": {{
        "total": number,
        "passed": number,
        "failed": number,
        "skipped": number,
        "pass_rate": "percentage"
    }},
    "highlights": ["key findings"],
    "failures_analysis": ["analysis of failures"],
    "recommendations": ["improvement recommendations"],
    "trends": "trend analysis if applicable"
}}"""),
            ("user", """Generate a {report_type} test report for the following results:
{test_results}

Include recommendations: {include_recommendations}

Return ONLY valid JSON, no explanations or markdown.""")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "report_type": report_type,
            "test_results": str(test_results),
            "include_recommendations": include_recommendations,
        })

        import json
        try:
            content = response.content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1]
                content = content.rsplit("```", 1)[0]
            return json.loads(content)
        except json.JSONDecodeError:
            return {"raw_response": response.content}

    def analyze_for_jira(
        self,
        test_results: list[dict[str, Any]],
        project_key: str,
    ) -> list[dict[str, Any]]:
        """Analyze test results and suggest JIRA tickets.

        Args:
            test_results: Test results to analyze.
            project_key: JIRA project key.

        Returns:
            List of suggested JIRA tickets.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a QA engineer preparing JIRA tickets from test failures.
For each failure, generate a JIRA ticket suggestion with:
{{
    "summary": "Brief summary for JIRA",
    "description": "Detailed description",
    "issue_type": "Bug/Task/Story",
    "priority": "Highest/High/Medium/Low/Lowest",
    "labels": ["label1", "label2"],
    "components": ["component1"],
    "acceptance_criteria": ["criteria1"]
}}"""),
            ("user", """Analyze these test results and suggest JIRA tickets for project {project_key}:
{test_results}

Return ONLY valid JSON array of ticket suggestions, no explanations or markdown.""")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "project_key": project_key,
            "test_results": str(test_results),
        })

        import json
        try:
            content = response.content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1]
                content = content.rsplit("```", 1)[0]
            return json.loads(content)
        except json.JSONDecodeError:
            return [{"raw_response": response.content}]
