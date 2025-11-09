# Eval Flywheel Pattern

## Overview

Test-driven development for AI systems. Create test cases BEFORE building features, measure continuously, and gate deployments on eval scores. Adapted from OpenAI Cookbook's "Eval-driven development" pattern.

## Target Repos

- `ipai-bot` (agents, tasks, flows)
- `pulser-copilot` (MCP tools)
- `insightpulse-workspace` (future)

## Pattern

```
Write Test Cases → Build Feature → Run Evals → Measure → Iterate
                                       ↓
                                 Gate Deployment (>95% pass rate)
```

## Test Case Format

```yaml
# ipai-bot/evals/test_cases/bir_classification.yaml

name: BIR Issue Classification
description: Test accuracy of BIR issue type/urgency classification

test_cases:
  - id: bir_classify_001
    description: "Classify critical 1601-C bug"
    input:
      issue_title: "1601-C validation fails for negative amounts"
      issue_body: |
        When submitting 1601-C with negative tax amount, validation rejects it.
        But RMC 5-2023 allows negative amounts in certain cases.
        This is blocking monthly filing for all entities.
    expected:
      issue_type: "bug"
      bir_form: "1601-C"
      urgency: "high"
      mentions_rmc: true
    tolerance:
      urgency: ["high", "critical"]  # Either acceptable

  - id: bir_classify_002
    description: "Classify feature request"
    input:
      issue_title: "Add support for 2550M monthly VAT"
      issue_body: "We need monthly VAT filing capability for small taxpayers."
    expected:
      issue_type: "feature"
      bir_form: "2550M"
      urgency: "medium"

  - id: bir_classify_003
    description: "Classify documentation request"
    input:
      issue_title: "How to file 1702-RT for new company?"
      issue_body: "I need step-by-step guide for annual income tax filing."
    expected:
      issue_type: "docs"
      bir_form: "1702-RT"
      urgency: "low"

behavioral_requirements:
  - name: "no_tax_hallucinations"
    description: "Must not reference non-existent BIR forms or RMCs"
    check_with_llm: true

  - name: "consistent_urgency_for_bugs"
    description: "Bugs should be medium or higher urgency"
    check: "issue_type == 'bug' implies urgency in ['medium', 'high', 'critical']"

  - name: "form_detection_accuracy"
    description: "Must detect BIR form mentions with >90% accuracy"
    metric: "precision"

  - name: "no_false_positives"
    description: "Non-BIR issues should not be classified as BIR"
    negative_cases:
      - input:
          issue_title: "Fix typo in README"
        expected:
          is_bir_related: false
```

## Eval Runner

```python
# ipai-bot/evals/run_evals.py

import yaml
from pathlib import Path
from typing import Dict, List, Any

class EvalRunner:
    """Run evals for ipai-bot tasks and flows"""

    def __init__(self):
        self.task_executors = {
            "classify_bir_issue": self.execute_bir_classifier,
            "autofix_ci": self.execute_ci_autofix,
            "search_code": self.execute_code_search,
        }

    def run_suite(self, suite_name: str = "all") -> EvalResults:
        """Run all test cases in a suite"""

        if suite_name == "all":
            test_files = Path("evals/test_cases").glob("*.yaml")
        else:
            test_files = [Path(f"evals/test_cases/{suite_name}.yaml")]

        all_results = []

        for test_file in test_files:
            print(f"\n{'='*80}")
            print(f"Running suite: {test_file.stem}")
            print(f"{'='*80}\n")

            suite_results = self.run_test_file(test_file)
            all_results.extend(suite_results)

        return self.aggregate_results(all_results)

    def run_test_file(self, test_file: Path) -> List[TestResult]:
        """Run all test cases in a file"""

        with open(test_file) as f:
            suite = yaml.safe_load(f)

        results = []

        # Run individual test cases
        for test_case in suite["test_cases"]:
            print(f"Running: {test_case['id']} - {test_case.get('description', '')}")

            result = self.run_test_case(test_case)
            results.append(result)

            if result.passed:
                print(f"  ✅ PASS")
            else:
                print(f"  ❌ FAIL: {result.failure_reason}")

        # Check behavioral requirements
        for requirement in suite.get("behavioral_requirements", []):
            print(f"\nChecking behavioral requirement: {requirement['name']}")

            behavior_result = self.check_behavioral_requirement(
                requirement,
                results
            )
            results.append(behavior_result)

            if behavior_result.passed:
                print(f"  ✅ PASS")
            else:
                print(f"  ❌ FAIL: {behavior_result.failure_reason}")

        return results

    def run_test_case(self, test_case: dict) -> TestResult:
        """Run a single test case"""

        # Determine which task to execute
        task_name = test_case.get("task", "infer_from_test_case")

        if task_name == "infer_from_test_case":
            # Infer from test case structure
            if "issue_title" in test_case["input"]:
                task_name = "classify_bir_issue"
            elif "error" in test_case["input"]:
                task_name = "autofix_ci"
            # ... more inference logic

        # Execute the task
        executor = self.task_executors.get(task_name)
        if not executor:
            raise ValueError(f"No executor for task: {task_name}")

        actual = executor(test_case["input"])

        # Compare with expected
        passed, failure_reason = self.compare_results(
            actual,
            test_case["expected"],
            test_case.get("tolerance", {})
        )

        return TestResult(
            test_id=test_case["id"],
            task=task_name,
            passed=passed,
            actual=actual,
            expected=test_case["expected"],
            failure_reason=failure_reason,
        )

    def compare_results(
        self,
        actual: dict,
        expected: dict,
        tolerance: dict
    ) -> tuple[bool, str]:
        """Compare actual vs expected with tolerance"""

        for key, expected_value in expected.items():
            if key not in actual:
                return False, f"Missing key: {key}"

            actual_value = actual[key]

            # Check tolerance
            if key in tolerance:
                acceptable_values = tolerance[key]
                if actual_value not in acceptable_values:
                    return False, f"{key}: {actual_value} not in {acceptable_values}"
            else:
                # Exact match
                if actual_value != expected_value:
                    return False, f"{key}: expected {expected_value}, got {actual_value}"

        return True, None

    def check_behavioral_requirement(
        self,
        requirement: dict,
        test_results: List[TestResult],
    ) -> TestResult:
        """Check a behavioral requirement across all test results"""

        if requirement.get("check_with_llm"):
            # Use LLM to check complex requirements
            return self.check_requirement_with_llm(requirement, test_results)

        elif "check" in requirement:
            # Simple logical check
            return self.check_requirement_logic(requirement, test_results)

        elif "metric" in requirement:
            # Compute metric (precision, recall, F1)
            return self.check_requirement_metric(requirement, test_results)

        else:
            raise ValueError(f"Unknown requirement type: {requirement}")

    def check_requirement_with_llm(
        self,
        requirement: dict,
        test_results: List[TestResult],
    ) -> TestResult:
        """Use LLM to check behavioral requirement"""

        # Summarize test results
        results_summary = "\n".join([
            f"Test {r.test_id}: {r.actual}"
            for r in test_results
            if r.task == requirement.get("task")
        ])

        check_prompt = f"""
        Requirement: {requirement['description']}

        Test Results:
        {results_summary}

        Does the system meet this requirement across all test cases?

        Answer YES or NO, followed by brief explanation.
        """

        response = llm_client.complete(check_prompt)
        passed = response.strip().startswith("YES")

        return TestResult(
            test_id=f"behavioral_{requirement['name']}",
            task="behavioral_check",
            passed=passed,
            actual=response,
            expected=requirement['description'],
            failure_reason=None if passed else response,
        )

    def aggregate_results(self, results: List[TestResult]) -> EvalResults:
        """Aggregate all results into summary"""

        total = len(results)
        passed = sum(1 for r in results if r.passed)
        failed = total - passed

        pass_rate = (passed / total * 100) if total > 0 else 0

        return EvalResults(
            total=total,
            passed=passed,
            failed=failed,
            pass_rate=pass_rate,
            results=results,
        )
```

## Make Targets

```makefile
# Makefile

.PHONY: eval
eval:
	@echo "Running all evals..."
	python -m evals.run_evals --suite all

.PHONY: eval-bir
eval-bir:
	@echo "Running BIR classification evals..."
	python -m evals.run_evals --suite bir_classification

.PHONY: eval-ci-autofix
eval-ci-autofix:
	@echo "Running CI autofix evals..."
	python -m evals.run_evals --suite ci_autofix

.PHONY: eval-code-search
eval-code-search:
	@echo "Running code search evals..."
	python -m evals.run_evals --suite code_search

.PHONY: eval-gate
eval-gate:
	@echo "Running eval gate (requires 95% pass rate)..."
	python -m evals.run_evals --suite all --gate 95
	@if [ $$? -ne 0 ]; then \
		echo "❌ Eval gate failed! Pass rate < 95%"; \
		exit 1; \
	else \
		echo "✅ Eval gate passed! Pass rate >= 95%"; \
	fi
```

## GitHub Actions Integration

```yaml
# .github/workflows/ai-eval.yml

name: AI Eval Gate

on:
  pull_request:
    paths:
      - 'src/tasks/**'
      - 'src/flows/**'
      - 'src/tools/**'
      - 'prompts/**'
      - 'evals/**'
  push:
    branches:
      - main

jobs:
  run-evals:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run evals
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
        run: |
          make eval > eval_results.txt 2>&1
          cat eval_results.txt

      - name: Parse results
        id: parse
        run: |
          PASS_RATE=$(grep "Pass rate:" eval_results.txt | awk '{print $3}' | tr -d '%')
          echo "pass_rate=$PASS_RATE" >> $GITHUB_OUTPUT

      - name: Check threshold
        run: |
          PASS_RATE="${{ steps.parse.outputs.pass_rate }}"

          if (( $(echo "$PASS_RATE < 95" | bc -l) )); then
            echo "❌ Eval pass rate $PASS_RATE% < 95% threshold"
            echo "::error::AI eval gate failed - pass rate too low"
            exit 1
          else
            echo "✅ Eval pass rate $PASS_RATE% >= 95% threshold"
          fi

      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: eval-results
          path: eval_results.txt

      - name: Comment on PR
        if: github.event_name == 'pull_request' && always()
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const results = fs.readFileSync('eval_results.txt', 'utf8');

            const passRate = "${{ steps.parse.outputs.pass_rate }}";
            const status = passRate >= 95 ? '✅ PASS' : '❌ FAIL';

            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: `## AI Eval Results ${status}

              **Pass Rate**: ${passRate}%
              **Threshold**: 95%

              <details>
              <summary>Full Results</summary>

              \`\`\`
              ${results}
              \`\`\`

              </details>
              `
            });
```

## MCP Tool Evals

```yaml
# pulser-copilot/evals/test_cases/search_code.yaml

name: Search Code Tool Evals
description: Test that search_code returns relevant files

test_cases:
  - id: search_code_001
    description: "Find BIR 1601-C validation logic"
    input:
      query: "1601-C validation rules"
    expected_files:
      - path_contains: "bir_forms"
        path_contains: "validation"
      - path_contains: "bir_1601c"
    expected_ranking:
      - "most relevant file should be ranked #1"
    behavioral:
      - "Files must actually exist in repo"
      - "Should not return test files unless explicitly asked"
      - "Ranking should prioritize exact matches"

  - id: search_code_002
    description: "Find month-end closing procedures"
    input:
      query: "month end closing workflow"
    expected_files:
      - path_contains: "account_closing"
      - path_contains: "month_end"
    behavioral:
      - "Should include both code and scripts"
      - "Should prefer documentation when it exists"

  - id: search_code_003
    description: "Find OCA module scaffolding"
    input:
      query: "scaffold OCA compliant module"
    expected_files:
      - path_contains: "scaffold"
      - path_contains: "OCA"
    behavioral:
      - "Should include examples and templates"
```

## Metrics to Track

```python
# evals/metrics.py

def compute_metrics(results: List[TestResult]) -> Dict[str, float]:
    """Compute standard ML metrics"""

    # Precision: TP / (TP + FP)
    precision = compute_precision(results)

    # Recall: TP / (TP + FN)
    recall = compute_recall(results)

    # F1: 2 * (precision * recall) / (precision + recall)
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    # Pass rate: Passed / Total
    pass_rate = sum(1 for r in results if r.passed) / len(results) * 100

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "pass_rate": pass_rate,
    }
```

## Continuous Monitoring

```python
# evals/monitor.py

@celery_app.task(name="run_eval_sweep")
@cron_schedule("0 0 * * *")  # Daily
def run_eval_sweep():
    """Run all evals and log to Superset"""

    results = run_all_evals()

    # Log to Supabase for Superset dashboard
    supabase.table("eval_runs").insert({
        "timestamp": datetime.now(),
        "total": results.total,
        "passed": results.passed,
        "failed": results.failed,
        "pass_rate": results.pass_rate,
        "metrics": compute_metrics(results.results),
    }).execute()

    # Alert if pass rate drops below threshold
    if results.pass_rate < 90:
        slack_notify(
            channel="#ai-alerts",
            message=f"⚠️ Eval pass rate dropped to {results.pass_rate}%",
        )
```

## Directory Structure

```
ipai-bot/
├── evals/
│   ├── test_cases/
│   │   ├── bir_classification.yaml
│   │   ├── ci_autofix.yaml
│   │   ├── code_search.yaml
│   │   └── pdf_extraction.yaml
│   ├── run_evals.py
│   ├── metrics.py
│   ├── monitor.py
│   └── results/
│       └── 2025-01-20_eval_results.json

pulser-copilot/
├── evals/
│   ├── test_cases/
│   │   ├── search_code.yaml
│   │   ├── deep_research.yaml
│   │   └── scaffold_module.yaml
│   └── run_evals.py
```

## Baseline & Regression Tracking

```python
# evals/baseline.py

def compare_to_baseline(results: EvalResults) -> RegressionReport:
    """Compare current results to baseline"""

    baseline = load_baseline()

    regressions = []
    improvements = []

    for test_id in results.test_ids:
        current_result = results.get(test_id)
        baseline_result = baseline.get(test_id)

        if baseline_result:
            if current_result.passed and not baseline_result.passed:
                improvements.append(test_id)
            elif not current_result.passed and baseline_result.passed:
                regressions.append(test_id)

    return RegressionReport(
        regressions=regressions,
        improvements=improvements,
        new_tests=results.test_ids - baseline.test_ids,
    )
```

## Cost Tracking

```python
# evals/cost_tracker.py

def estimate_eval_cost(suite_name: str) -> float:
    """Estimate cost to run eval suite"""

    suite = load_suite(suite_name)

    total_tokens = 0

    for test_case in suite.test_cases:
        # Estimate input tokens
        input_tokens = estimate_tokens(test_case.input)

        # Estimate output tokens (avg 500 for classifications)
        output_tokens = 500

        total_tokens += input_tokens + output_tokens

    # GPT-4 pricing: $0.01 / 1K input, $0.03 / 1K output
    cost = (total_tokens / 1000) * 0.02  # Average

    return cost
```

## Pass Criteria

```python
# evals/gate.py

GATE_CRITERIA = {
    "overall_pass_rate": 95,  # %
    "behavioral_violations": 0,  # Must be zero
    "no_regressions": True,
    "critical_tests_pass": 100,  # % (marked as critical)
}

def check_gate(results: EvalResults, baseline: EvalResults) -> GateResult:
    """Check if results meet deployment gate criteria"""

    checks = {
        "pass_rate": results.pass_rate >= GATE_CRITERIA["overall_pass_rate"],
        "behavioral": count_behavioral_failures(results) == 0,
        "regressions": not has_regressions(results, baseline),
        "critical": critical_tests_pass_rate(results) == 100,
    }

    passed = all(checks.values())

    return GateResult(
        passed=passed,
        checks=checks,
        message="Gate passed" if passed else f"Gate failed: {checks}",
    )
```

## Next Steps

1. Create first 10 test cases for BIR classification
2. Implement eval runner
3. Add GitHub Actions workflow
4. Set up Superset dashboard for eval metrics
5. Establish baseline from current system
6. Enable deployment gate on critical repos

## Success Metrics

- **Test coverage**: 50+ test cases per repo
- **Pass rate**: >95% consistently
- **Regression detection**: <24 hours
- **Gate enforcement**: 100% on main branch
- **Cost per eval run**: <$5
