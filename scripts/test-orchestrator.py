#!/usr/bin/env python3
"""
Multi-Agent Orchestrator Integration Tests
Tests routing, coordination, and end-to-end workflows
"""
import requests
import json
import sys
import time
from typing import Dict, List, Any
from dataclasses import dataclass

# ANSI color codes
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
NC = '\033[0m'

@dataclass
class TestResult:
    name: str
    passed: bool
    message: str
    response_time: float

class OrchestratorTester:
    def __init__(self, base_urls: Dict[str, str]):
        self.base_urls = base_urls
        self.results: List[TestResult] = []

    def test_health_checks(self) -> List[TestResult]:
        """Test health endpoints for all specialist services"""
        results = []
        for agent_name, base_url in self.base_urls.items():
            start = time.time()
            try:
                response = requests.get(f"{base_url}/health", timeout=5)
                elapsed = time.time() - start

                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "ok":
                        results.append(TestResult(
                            name=f"{agent_name}_health",
                            passed=True,
                            message=f"Health check passed (model: {data.get('model', 'unknown')})",
                            response_time=elapsed
                        ))
                    else:
                        results.append(TestResult(
                            name=f"{agent_name}_health",
                            passed=False,
                            message=f"Unexpected status: {data.get('status')}",
                            response_time=elapsed
                        ))
                else:
                    results.append(TestResult(
                        name=f"{agent_name}_health",
                        passed=False,
                        message=f"HTTP {response.status_code}",
                        response_time=elapsed
                    ))
            except requests.exceptions.RequestException as e:
                elapsed = time.time() - start
                results.append(TestResult(
                    name=f"{agent_name}_health",
                    passed=False,
                    message=f"Connection error: {str(e)}",
                    response_time=elapsed
                ))

        return results

    def test_capabilities(self) -> List[TestResult]:
        """Test capabilities endpoints for specialist discovery"""
        results = []
        for agent_name, base_url in self.base_urls.items():
            start = time.time()
            try:
                response = requests.get(f"{base_url}/capabilities", timeout=5)
                elapsed = time.time() - start

                if response.status_code == 200:
                    data = response.json()
                    if "agent_name" in data and "capabilities" in data:
                        results.append(TestResult(
                            name=f"{agent_name}_capabilities",
                            passed=True,
                            message=f"Capabilities: {len(data['capabilities'])} items",
                            response_time=elapsed
                        ))
                    else:
                        results.append(TestResult(
                            name=f"{agent_name}_capabilities",
                            passed=False,
                            message="Missing required fields (agent_name, capabilities)",
                            response_time=elapsed
                        ))
                else:
                    results.append(TestResult(
                        name=f"{agent_name}_capabilities",
                        passed=False,
                        message=f"HTTP {response.status_code}",
                        response_time=elapsed
                    ))
            except requests.exceptions.RequestException as e:
                elapsed = time.time() - start
                results.append(TestResult(
                    name=f"{agent_name}_capabilities",
                    passed=False,
                    message=f"Connection error: {str(e)}",
                    response_time=elapsed
                ))

        return results

    def test_specialist_execution(self) -> List[TestResult]:
        """Test individual specialist execution"""
        results = []

        test_cases = [
            {
                "agent": "odoo_developer",
                "task": "Create a simple Odoo module for tracking expenses",
                "expected_keywords": ["module", "model", "__manifest__.py"]
            },
            {
                "agent": "finance_ssc_expert",
                "task": "Generate BIR Form 1601-C for January 2025 for RIM agency",
                "expected_keywords": ["1601-C", "January", "withholding"]
            },
            {
                "agent": "bi_architect",
                "task": "Design a Superset dashboard for expense analytics",
                "expected_keywords": ["dashboard", "chart", "sql"]
            },
            {
                "agent": "devops_engineer",
                "task": "Create deployment spec for a new API service",
                "expected_keywords": ["deploy", "app platform", "yaml"]
            }
        ]

        for test_case in test_cases:
            agent_name = test_case["agent"]
            if agent_name not in self.base_urls:
                continue

            base_url = self.base_urls[agent_name]
            start = time.time()

            try:
                response = requests.post(
                    f"{base_url}/execute",
                    json={
                        "task": test_case["task"],
                        "context": {},
                        "conversation_id": f"test_{agent_name}_{int(time.time())}"
                    },
                    timeout=30
                )
                elapsed = time.time() - start

                if response.status_code == 200:
                    data = response.json()
                    result_text = data.get("result", "").lower()

                    # Check if expected keywords are present
                    keywords_found = sum(1 for kw in test_case["expected_keywords"] if kw.lower() in result_text)
                    confidence = data.get("confidence", 0)

                    if keywords_found > 0 and confidence > 0.7:
                        results.append(TestResult(
                            name=f"{agent_name}_execution",
                            passed=True,
                            message=f"Execution successful (confidence: {confidence:.2f}, keywords: {keywords_found}/{len(test_case['expected_keywords'])})",
                            response_time=elapsed
                        ))
                    else:
                        results.append(TestResult(
                            name=f"{agent_name}_execution",
                            passed=False,
                            message=f"Low quality response (confidence: {confidence:.2f}, keywords: {keywords_found}/{len(test_case['expected_keywords'])})",
                            response_time=elapsed
                        ))
                else:
                    results.append(TestResult(
                        name=f"{agent_name}_execution",
                        passed=False,
                        message=f"HTTP {response.status_code}: {response.text[:100]}",
                        response_time=elapsed
                    ))
            except requests.exceptions.RequestException as e:
                elapsed = time.time() - start
                results.append(TestResult(
                    name=f"{agent_name}_execution",
                    passed=False,
                    message=f"Connection error: {str(e)}",
                    response_time=elapsed
                ))

        return results

    def run_all_tests(self) -> bool:
        """Run all test suites"""
        print(f"{GREEN}=== Multi-Agent Orchestrator Integration Tests ==={NC}\n")

        # Test health checks
        print(f"{YELLOW}Testing health endpoints...{NC}")
        health_results = self.test_health_checks()
        self.results.extend(health_results)
        self.print_results(health_results)

        # Test capabilities
        print(f"\n{YELLOW}Testing capabilities endpoints...{NC}")
        cap_results = self.test_capabilities()
        self.results.extend(cap_results)
        self.print_results(cap_results)

        # Test specialist execution (only if health checks pass)
        if all(r.passed for r in health_results):
            print(f"\n{YELLOW}Testing specialist execution...{NC}")
            exec_results = self.test_specialist_execution()
            self.results.extend(exec_results)
            self.print_results(exec_results)
        else:
            print(f"\n{RED}Skipping execution tests due to health check failures{NC}")

        # Print summary
        self.print_summary()

        return all(r.passed for r in self.results)

    def print_results(self, results: List[TestResult]):
        """Print test results"""
        for result in results:
            status = f"{GREEN}✓{NC}" if result.passed else f"{RED}✗{NC}"
            print(f"  {status} {result.name}: {result.message} ({result.response_time:.2f}s)")

    def print_summary(self):
        """Print test summary"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed

        print(f"\n{GREEN}=== Test Summary ==={NC}")
        print(f"Total: {total}")
        print(f"{GREEN}Passed: {passed}{NC}")
        print(f"{RED}Failed: {failed}{NC}")

        if passed == total:
            print(f"\n{GREEN}All tests passed! ✓{NC}")
        else:
            print(f"\n{RED}Some tests failed. Review output above.{NC}")

if __name__ == "__main__":
    # Define specialist service URLs
    # Update these with actual deployed URLs
    BASE_URLS = {
        "odoo_developer": "https://odoo-developer-agent.ondigitalocean.app",
        "finance_ssc_expert": "https://finance-ssc-expert.ondigitalocean.app",
        "bi_architect": "https://bi-architect.ondigitalocean.app",
        "devops_engineer": "https://devops-engineer.ondigitalocean.app"
    }

    # Allow URL override via command line
    if len(sys.argv) > 1:
        print(f"{YELLOW}Loading URLs from command line arguments...{NC}")
        # Expected format: agent_name=url agent_name=url ...
        for arg in sys.argv[1:]:
            if "=" in arg:
                agent, url = arg.split("=", 1)
                BASE_URLS[agent] = url

    print(f"{YELLOW}Testing endpoints:{NC}")
    for agent, url in BASE_URLS.items():
        print(f"  {agent}: {url}")
    print()

    # Run tests
    tester = OrchestratorTester(BASE_URLS)
    success = tester.run_all_tests()

    sys.exit(0 if success else 1)
