"use client";

import { useState } from "react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type TabType = "test-data" | "environment" | "test-cases" | "reports" | "jira";

interface ApiResponse {
  [key: string]: unknown;
}

export default function Home() {
  const [activeTab, setActiveTab] = useState<TabType>("test-data");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ApiResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Form states
  const [dataType, setDataType] = useState("user");
  const [dataCount, setDataCount] = useState(5);
  const [constraints, setConstraints] = useState("");

  const [envInfo, setEnvInfo] = useState('{"url": "https://api.example.com", "type": "REST API"}');
  const [explorationType, setExplorationType] = useState("api");

  const [featureDescription, setFeatureDescription] = useState("");
  const [testType, setTestType] = useState("functional");
  const [formatType, setFormatType] = useState("robot");
  const [testCount, setTestCount] = useState(5);

  const [testResults, setTestResults] = useState('[{"name": "Test Login", "status": "passed"}, {"name": "Test Logout", "status": "failed", "error": "Timeout"}]');
  const [reportType, setReportType] = useState("summary");

  const [jiraResults, setJiraResults] = useState('[{"name": "Test Login", "status": "failed", "error": "Authentication timeout"}]');
  const [projectKey, setProjectKey] = useState("PROJ");

  const handleApiCall = async (endpoint: string, body: object) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "API request failed");
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateTestData = () => {
    let parsedConstraints = undefined;
    if (constraints.trim()) {
      try {
        parsedConstraints = JSON.parse(constraints);
      } catch {
        setError("Invalid JSON in constraints field");
        return;
      }
    }

    handleApiCall("/api/v1/test-data/generate", {
      data_type: dataType,
      count: dataCount,
      constraints: parsedConstraints,
    });
  };

  const handleExploreEnvironment = () => {
    let parsedEnvInfo;
    try {
      parsedEnvInfo = JSON.parse(envInfo);
    } catch {
      setError("Invalid JSON in environment info field");
      return;
    }

    handleApiCall("/api/v1/environment/explore", {
      environment_info: parsedEnvInfo,
      exploration_type: explorationType,
    });
  };

  const handleGenerateTestCases = () => {
    if (!featureDescription.trim()) {
      setError("Please enter a feature description");
      return;
    }

    handleApiCall("/api/v1/test-cases/generate", {
      feature_description: featureDescription,
      test_type: testType,
      format_type: formatType,
      count: testCount,
    });
  };

  const handleGenerateReport = () => {
    let parsedResults;
    try {
      parsedResults = JSON.parse(testResults);
    } catch {
      setError("Invalid JSON in test results field");
      return;
    }

    handleApiCall("/api/v1/reports/generate", {
      test_results: parsedResults,
      report_type: reportType,
      include_recommendations: true,
    });
  };

  const handleAnalyzeForJira = () => {
    let parsedResults;
    try {
      parsedResults = JSON.parse(jiraResults);
    } catch {
      setError("Invalid JSON in test results field");
      return;
    }

    handleApiCall("/api/v1/jira/analyze", {
      test_results: parsedResults,
      project_key: projectKey,
    });
  };

  const tabs = [
    { id: "test-data" as TabType, label: "Test Data", icon: "📊" },
    { id: "environment" as TabType, label: "Environment", icon: "🔍" },
    { id: "test-cases" as TabType, label: "Test Cases", icon: "📝" },
    { id: "reports" as TabType, label: "Reports", icon: "📈" },
    { id: "jira" as TabType, label: "JIRA", icon: "🎫" },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800">
      {/* Header */}
      <header className="bg-gray-800/50 backdrop-blur border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="text-3xl">🤖</div>
            <div>
              <h1 className="text-2xl font-bold text-white">Robot Framework AI Assistant</h1>
              <p className="text-gray-400 text-sm">AI-driven automation for QA testing</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Tabs */}
        <div className="flex flex-wrap gap-2 mb-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
                activeTab === tab.id
                  ? "bg-blue-600 text-white shadow-lg shadow-blue-600/30"
                  : "bg-gray-700 text-gray-300 hover:bg-gray-600"
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          ))}
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Input Panel */}
          <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
            <h2 className="text-xl font-semibold text-white mb-4">
              {activeTab === "test-data" && "Generate Test Data"}
              {activeTab === "environment" && "Explore Environment"}
              {activeTab === "test-cases" && "Generate Test Cases"}
              {activeTab === "reports" && "Generate Test Report"}
              {activeTab === "jira" && "JIRA Integration"}
            </h2>

            {/* Test Data Form */}
            {activeTab === "test-data" && (
              <div className="space-y-4">
                <div>
                  <label className="block text-gray-300 text-sm mb-1">Data Type</label>
                  <select
                    value={dataType}
                    onChange={(e) => setDataType(e.target.value)}
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                  >
                    <option value="user">User</option>
                    <option value="order">Order</option>
                    <option value="product">Product</option>
                    <option value="address">Address</option>
                    <option value="payment">Payment</option>
                  </select>
                </div>
                <div>
                  <label className="block text-gray-300 text-sm mb-1">Count</label>
                  <input
                    type="number"
                    min={1}
                    max={100}
                    value={dataCount}
                    onChange={(e) => setDataCount(parseInt(e.target.value))}
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                  />
                </div>
                <div>
                  <label className="block text-gray-300 text-sm mb-1">Constraints (JSON)</label>
                  <textarea
                    value={constraints}
                    onChange={(e) => setConstraints(e.target.value)}
                    placeholder='{"age": "18-65", "country": "US"}'
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white h-24"
                  />
                </div>
                <button
                  onClick={handleGenerateTestData}
                  disabled={loading}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg font-medium disabled:opacity-50"
                >
                  {loading ? "Generating..." : "Generate Test Data"}
                </button>
              </div>
            )}

            {/* Environment Form */}
            {activeTab === "environment" && (
              <div className="space-y-4">
                <div>
                  <label className="block text-gray-300 text-sm mb-1">Environment Info (JSON)</label>
                  <textarea
                    value={envInfo}
                    onChange={(e) => setEnvInfo(e.target.value)}
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white h-32"
                  />
                </div>
                <div>
                  <label className="block text-gray-300 text-sm mb-1">Exploration Type</label>
                  <select
                    value={explorationType}
                    onChange={(e) => setExplorationType(e.target.value)}
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                  >
                    <option value="general">General</option>
                    <option value="api">API</option>
                    <option value="ui">UI</option>
                    <option value="database">Database</option>
                  </select>
                </div>
                <button
                  onClick={handleExploreEnvironment}
                  disabled={loading}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg font-medium disabled:opacity-50"
                >
                  {loading ? "Exploring..." : "Explore Environment"}
                </button>
              </div>
            )}

            {/* Test Cases Form */}
            {activeTab === "test-cases" && (
              <div className="space-y-4">
                <div>
                  <label className="block text-gray-300 text-sm mb-1">Feature Description</label>
                  <textarea
                    value={featureDescription}
                    onChange={(e) => setFeatureDescription(e.target.value)}
                    placeholder="Describe the feature you want to test..."
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white h-32"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-gray-300 text-sm mb-1">Test Type</label>
                    <select
                      value={testType}
                      onChange={(e) => setTestType(e.target.value)}
                      className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                    >
                      <option value="functional">Functional</option>
                      <option value="integration">Integration</option>
                      <option value="e2e">End-to-End</option>
                      <option value="api">API</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-gray-300 text-sm mb-1">Format</label>
                    <select
                      value={formatType}
                      onChange={(e) => setFormatType(e.target.value)}
                      className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                    >
                      <option value="robot">Robot Framework</option>
                      <option value="gherkin">Gherkin</option>
                      <option value="pytest">Pytest</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label className="block text-gray-300 text-sm mb-1">Number of Test Cases</label>
                  <input
                    type="number"
                    min={1}
                    max={20}
                    value={testCount}
                    onChange={(e) => setTestCount(parseInt(e.target.value))}
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                  />
                </div>
                <button
                  onClick={handleGenerateTestCases}
                  disabled={loading}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg font-medium disabled:opacity-50"
                >
                  {loading ? "Generating..." : "Generate Test Cases"}
                </button>
              </div>
            )}

            {/* Reports Form */}
            {activeTab === "reports" && (
              <div className="space-y-4">
                <div>
                  <label className="block text-gray-300 text-sm mb-1">Test Results (JSON)</label>
                  <textarea
                    value={testResults}
                    onChange={(e) => setTestResults(e.target.value)}
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white h-32"
                  />
                </div>
                <div>
                  <label className="block text-gray-300 text-sm mb-1">Report Type</label>
                  <select
                    value={reportType}
                    onChange={(e) => setReportType(e.target.value)}
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                  >
                    <option value="summary">Summary</option>
                    <option value="detailed">Detailed</option>
                    <option value="executive">Executive</option>
                  </select>
                </div>
                <button
                  onClick={handleGenerateReport}
                  disabled={loading}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg font-medium disabled:opacity-50"
                >
                  {loading ? "Generating..." : "Generate Report"}
                </button>
              </div>
            )}

            {/* JIRA Form */}
            {activeTab === "jira" && (
              <div className="space-y-4">
                <div>
                  <label className="block text-gray-300 text-sm mb-1">Test Results (JSON)</label>
                  <textarea
                    value={jiraResults}
                    onChange={(e) => setJiraResults(e.target.value)}
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white h-32"
                  />
                </div>
                <div>
                  <label className="block text-gray-300 text-sm mb-1">JIRA Project Key</label>
                  <input
                    type="text"
                    value={projectKey}
                    onChange={(e) => setProjectKey(e.target.value)}
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                  />
                </div>
                <button
                  onClick={handleAnalyzeForJira}
                  disabled={loading}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg font-medium disabled:opacity-50"
                >
                  {loading ? "Analyzing..." : "Analyze for JIRA Tickets"}
                </button>
              </div>
            )}
          </div>

          {/* Result Panel */}
          <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
            <h2 className="text-xl font-semibold text-white mb-4">Result</h2>

            {loading && (
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
              </div>
            )}

            {error && (
              <div className="bg-red-900/50 border border-red-700 rounded-lg p-4 text-red-200">
                <p className="font-medium">Error</p>
                <p className="text-sm">{error}</p>
              </div>
            )}

            {result && !loading && (
              <div className="bg-gray-700 rounded-lg p-4 overflow-auto max-h-[500px]">
                <pre className="text-gray-200 text-sm whitespace-pre-wrap">
                  {JSON.stringify(result, null, 2)}
                </pre>
              </div>
            )}

            {!result && !loading && !error && (
              <div className="flex items-center justify-center h-64 text-gray-500">
                <p>Submit a request to see results</p>
              </div>
            )}
          </div>
        </div>

        {/* Features Section */}
        <div className="mt-12 grid md:grid-cols-3 gap-6">
          <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
            <div className="text-3xl mb-3">🚀</div>
            <h3 className="text-lg font-semibold text-white mb-2">AI-Powered Generation</h3>
            <p className="text-gray-400 text-sm">
              Generate realistic test data, comprehensive test cases, and insightful reports using advanced AI models.
            </p>
          </div>
          <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
            <div className="text-3xl mb-3">🔗</div>
            <h3 className="text-lg font-semibold text-white mb-2">Seamless Integrations</h3>
            <p className="text-gray-400 text-sm">
              Connect with JIRA, Xray, and Zephyr Scale for end-to-end test management and issue tracking.
            </p>
          </div>
          <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
            <div className="text-3xl mb-3">🤖</div>
            <h3 className="text-lg font-semibold text-white mb-2">Robot Framework Ready</h3>
            <p className="text-gray-400 text-sm">
              Use as a Robot Framework library with keywords or as a standalone API server for any automation framework.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-700 mt-12 py-6">
        <div className="max-w-7xl mx-auto px-4 text-center text-gray-500 text-sm">
          <p>Robot Framework AI Assistant - AI-driven automation for QA testing</p>
          <p className="mt-1">
            <a href="https://github.com/ychgh/robotframework-ai-assisstant" className="text-blue-400 hover:underline">
              GitHub Repository
            </a>
          </p>
        </div>
      </footer>
    </div>
  );
}
