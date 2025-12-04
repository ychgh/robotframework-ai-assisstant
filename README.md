# Robot Framework AI Assistant

AI-driven automation library for Robot Framework with test data generation, environment exploration, test case generation, and integrations with JIRA/XRAY/Zephyr.

## Features

- **Test Data Generation**: Generate realistic test data using AI for various data types (users, orders, products, etc.)
- **Test Environment Exploration**: Analyze and understand test environments with AI-powered insights
- **Test Case Generation**: Auto-generate test cases in Robot Framework, Gherkin, or pytest formats
- **Test Report Generation**: Create intelligent test reports with failure analysis and recommendations
- **JIRA Integration**: Create issues, link tests, and manage test artifacts in JIRA
- **Xray Integration**: Import test executions and manage test cases in Xray
- **Zephyr Scale Integration**: Create test cycles, manage executions in Zephyr Scale

## Installation

```bash
pip install robotframework-ai-assistant
```

Or install from source:

```bash
git clone https://github.com/ychgh/robotframework-ai-assisstant.git
cd robotframework-ai-assisstant
pip install -e .
```

## Configuration

Set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY=your-api-key
```

Or provide it when importing the library in Robot Framework.

## Usage

### As a Robot Framework Library

```robotframework
*** Settings ***
Library    AIAssistantLibrary    api_key=${API_KEY}

*** Test Cases ***
Generate User Test Data
    ${users}=    Generate Test Data    user    count=5
    Log    Generated ${users}

Generate Login Test Cases
    ${tests}=    Generate Test Cases    User login with email and password    functional    robot    5
    Log    ${tests}

Explore API Environment
    ${analysis}=    Explore Test Environment    {"url": "https://api.example.com", "type": "REST"}    api
    Log    ${analysis}

Generate Test Report
    ${report}=    Generate Test Report    [{"name": "Test1", "status": "passed"}]    summary
    Log    ${report}
```

### With JIRA Integration

```robotframework
*** Settings ***
Library    AIAssistantLibrary
...        jira_url=https://your-domain.atlassian.net
...        jira_username=${JIRA_USER}
...        jira_api_token=${JIRA_TOKEN}

*** Test Cases ***
Create Issue From Test Failure
    ${issue}=    Create JIRA Issue From Failure
    ...    Login Test Failed
    ...    Expected 200 but got 401
    ...    PROJ
    Log    Created issue: ${issue}[key]
```

### With Xray Integration

```robotframework
*** Settings ***
Library    AIAssistantLibrary
...        xray_client_id=${XRAY_CLIENT_ID}
...        xray_client_secret=${XRAY_CLIENT_SECRET}

*** Test Cases ***
Import Test Results To Xray
    ${result}=    Import Test Execution To Xray    output.xml    PROJ
    Log    Imported: ${result}
```

### With Zephyr Scale Integration

```robotframework
*** Settings ***
Library    AIAssistantLibrary
...        zephyr_api_token=${ZEPHYR_TOKEN}
...        jira_url=https://your-domain.atlassian.net

*** Test Cases ***
Create Test Cycle
    ${cycle}=    Create Zephyr Test Cycle    Sprint 1 Regression    PROJ
    Log    Created cycle: ${cycle}
```

## API Server

The library can run as a standalone FastAPI server:

```bash
# Start the server
rf-ai-server

# Or with custom host/port
HOST=0.0.0.0 PORT=8080 rf-ai-server
```

### API Endpoints

- `GET /` - Health check
- `POST /api/v1/test-data/generate` - Generate test data
- `POST /api/v1/environment/explore` - Explore test environment
- `POST /api/v1/test-cases/generate` - Generate test cases
- `POST /api/v1/reports/generate` - Generate test reports
- `POST /api/v1/jira/analyze` - Analyze test results for JIRA tickets

API documentation available at `/docs` (Swagger UI) or `/redoc` (ReDoc).

### Example API Requests

```bash
# Generate test data
curl -X POST http://localhost:8000/api/v1/test-data/generate \
  -H "Content-Type: application/json" \
  -d '{"data_type": "user", "count": 3}'

# Generate test cases
curl -X POST http://localhost:8000/api/v1/test-cases/generate \
  -H "Content-Type: application/json" \
  -d '{"feature_description": "User login with email and password", "test_type": "functional", "format_type": "robot", "count": 5}'
```

## Frontend Demo

A Next.js frontend demo is included in the `frontend/` directory:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 to use the demo interface.

## Development

### Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install with development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest tests/
```

### Linting

```bash
ruff check src/ tests/
ruff format src/ tests/
```

## Keywords Reference

### Test Data Generation

| Keyword | Description |
|---------|-------------|
| `Generate Test Data` | Generate test data of any type |
| `Generate User Data` | Generate realistic user data |

### Environment Exploration

| Keyword | Description |
|---------|-------------|
| `Explore Test Environment` | Analyze a test environment |
| `Analyze API Endpoints` | Analyze API specifications |

### Test Case Generation

| Keyword | Description |
|---------|-------------|
| `Generate Test Cases` | Generate test cases for a feature |
| `Generate Robot Test Suite` | Generate a complete Robot Framework test suite |

### Test Reports

| Keyword | Description |
|---------|-------------|
| `Generate Test Report` | Generate an AI-powered test report |
| `Analyze Test Failures` | Analyze test failures with insights |

### JIRA Integration

| Keyword | Description |
|---------|-------------|
| `Create JIRA Issue From Failure` | Create a JIRA issue from a test failure |
| `Link Test To JIRA Issue` | Link a test case to a JIRA issue |
| `Get JIRA Issue` | Get details of a JIRA issue |

### Xray Integration

| Keyword | Description |
|---------|-------------|
| `Import Test Execution To Xray` | Import test results to Xray |
| `Create Xray Test` | Create a test case in Xray |

### Zephyr Scale Integration

| Keyword | Description |
|---------|-------------|
| `Create Zephyr Test Cycle` | Create a test cycle |
| `Add Test To Zephyr Cycle` | Add a test to a cycle |
| `Update Zephyr Execution` | Update execution status |

## License

Apache License 2.0 - see [LICENSE](LICENSE) for details.

