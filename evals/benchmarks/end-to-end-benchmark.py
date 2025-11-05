#!/usr/bin/env python3
"""
End-to-End Benchmark Runner
-----------------------------
Runs golden dataset test cases and compares against baseline.
Fails if accuracy drops >2% or cost increases >15%.
"""
import argparse
import json
import yaml
import sys
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
import statistics


@dataclass
class TestResult:
    """Single test case result"""
    test_id: str
    category: str
    task: str
    passed: bool
    accuracy: float
    latency_ms: float
    cost_usd: float
    error: str = None


@dataclass
class BenchmarkResults:
    """Aggregate benchmark results"""
    total_tests: int
    passed_tests: int
    failed_tests: int
    overall_accuracy: float
    average_latency_ms: float
    total_cost_usd: float
    p95_latency_ms: float
    success_rate: float
    test_results: List[TestResult]


def load_golden_dataset(path: Path) -> Dict[str, Any]:
    """Load golden dataset YAML"""
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def load_baseline(path: Path) -> Dict[str, Any]:
    """Load baseline metrics JSON"""
    if not path.exists():
        print(f"⚠️  No baseline found at {path}, will create one")
        return None
    with open(path, 'r') as f:
        return json.load(f)


def run_test_case(test_case: Dict[str, Any]) -> TestResult:
    """
    Run a single test case
    TODO: Replace with actual LLM router calls
    """
    test_id = test_case['id']
    category = test_case['category']
    task = test_case['task']

    # Simulate test execution (replace with actual router call)
    # This is a placeholder implementation
    import random
    import time

    # Simulate latency
    latency = random.uniform(500, 2000)
    time.sleep(latency / 1000.0)

    # Simulate accuracy (90-98%)
    accuracy = random.uniform(0.90, 0.98)

    # Simulate cost ($0.0001 - $0.01)
    cost = random.uniform(0.0001, 0.01)

    # Simple pass/fail based on accuracy threshold
    expected = test_case.get('expected_output', {})
    accuracy_threshold = expected.get('accuracy_threshold', 0.90)
    passed = accuracy >= accuracy_threshold

    return TestResult(
        test_id=test_id,
        category=category,
        task=task,
        passed=passed,
        accuracy=accuracy,
        latency_ms=latency,
        cost_usd=cost
    )


def compute_aggregate_metrics(results: List[TestResult]) -> BenchmarkResults:
    """Compute aggregate metrics from test results"""
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed

    accuracies = [r.accuracy for r in results]
    latencies = [r.latency_ms for r in results]
    costs = [r.cost_usd for r in results]

    overall_accuracy = statistics.mean(accuracies)
    avg_latency = statistics.mean(latencies)
    total_cost = sum(costs)
    p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
    success_rate = passed / total if total > 0 else 0.0

    return BenchmarkResults(
        total_tests=total,
        passed_tests=passed,
        failed_tests=failed,
        overall_accuracy=overall_accuracy,
        average_latency_ms=avg_latency,
        total_cost_usd=total_cost,
        p95_latency_ms=p95_latency,
        success_rate=success_rate,
        test_results=results
    )


def compare_with_baseline(
    current: BenchmarkResults,
    baseline: Dict[str, Any],
    thresholds: Dict[str, float]
) -> Dict[str, Any]:
    """Compare current results with baseline and check thresholds"""
    if baseline is None:
        return {
            "comparison_available": False,
            "regressions": [],
            "message": "No baseline available - this will be the new baseline"
        }

    regressions = []

    # Check accuracy
    baseline_accuracy = baseline.get('overall_accuracy', 0.0)
    accuracy_drop = baseline_accuracy - current.overall_accuracy
    max_accuracy_drop = thresholds.get('accuracy_drop_max', 0.02)

    if accuracy_drop > max_accuracy_drop:
        regressions.append({
            "metric": "accuracy",
            "baseline": baseline_accuracy,
            "current": current.overall_accuracy,
            "change": -accuracy_drop,
            "threshold": -max_accuracy_drop,
            "severity": "critical"
        })

    # Check cost
    baseline_cost = baseline.get('total_cost_usd', 0.0)
    cost_increase_pct = (current.total_cost_usd - baseline_cost) / baseline_cost if baseline_cost > 0 else 0
    max_cost_increase = thresholds.get('cost_increase_max', 0.15)

    if cost_increase_pct > max_cost_increase:
        regressions.append({
            "metric": "cost",
            "baseline": baseline_cost,
            "current": current.total_cost_usd,
            "change_pct": cost_increase_pct,
            "threshold_pct": max_cost_increase,
            "severity": "warning"
        })

    # Check latency
    baseline_latency = baseline.get('average_latency_ms', 0.0)
    latency_increase_pct = (current.average_latency_ms - baseline_latency) / baseline_latency if baseline_latency > 0 else 0
    max_latency_increase = thresholds.get('latency_increase_max', 0.20)

    if latency_increase_pct > max_latency_increase:
        regressions.append({
            "metric": "latency",
            "baseline": baseline_latency,
            "current": current.average_latency_ms,
            "change_pct": latency_increase_pct,
            "threshold_pct": max_latency_increase,
            "severity": "warning"
        })

    # Check success rate
    min_success_rate = thresholds.get('success_rate_min', 0.95)
    if current.success_rate < min_success_rate:
        regressions.append({
            "metric": "success_rate",
            "current": current.success_rate,
            "threshold": min_success_rate,
            "severity": "critical"
        })

    return {
        "comparison_available": True,
        "regressions": regressions,
        "has_regressions": len(regressions) > 0
    }


def save_results(results: BenchmarkResults, output_path: Path):
    """Save results to JSON file"""
    output_data = {
        "timestamp": "2025-01-05T00:00:00Z",  # Use actual timestamp in production
        "total_tests": results.total_tests,
        "passed_tests": results.passed_tests,
        "failed_tests": results.failed_tests,
        "overall_accuracy": results.overall_accuracy,
        "average_latency_ms": results.average_latency_ms,
        "total_cost_usd": results.total_cost_usd,
        "p95_latency_ms": results.p95_latency_ms,
        "success_rate": results.success_rate,
        "test_results": [asdict(r) for r in results.test_results]
    }

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"✓ Results saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Run golden-set benchmark")
    parser.add_argument('--dataset', type=Path, required=True, help="Path to golden dataset YAML")
    parser.add_argument('--baseline', type=Path, required=True, help="Path to baseline JSON")
    parser.add_argument('--out', type=Path, required=True, help="Output path for results JSON")
    parser.add_argument('--accuracy-threshold', type=float, default=0.02, help="Max accuracy drop")
    parser.add_argument('--cost-threshold', type=float, default=0.15, help="Max cost increase")

    args = parser.parse_args()

    print("=" * 70)
    print("InsightPulse AI Golden-Set Benchmark")
    print("=" * 70)

    # Load dataset
    print(f"\n📂 Loading dataset: {args.dataset}")
    dataset = load_golden_dataset(args.dataset)
    test_cases = dataset['test_cases']
    print(f"   Loaded {len(test_cases)} test cases")

    # Load baseline
    print(f"\n📊 Loading baseline: {args.baseline}")
    baseline = load_baseline(args.baseline)

    # Run test cases
    print(f"\n🚀 Running {len(test_cases)} test cases...")
    results = []
    for i, test_case in enumerate(test_cases, 1):
        test_id = test_case['id']
        print(f"   [{i}/{len(test_cases)}] {test_id}...", end=' ')
        result = run_test_case(test_case)
        results.append(result)
        status = "✓" if result.passed else "✗"
        print(f"{status} ({result.accuracy:.1%}, {result.latency_ms:.0f}ms, ${result.cost_usd:.4f})")

    # Compute aggregate metrics
    print("\n📈 Computing aggregate metrics...")
    aggregate = compute_aggregate_metrics(results)

    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Total tests:       {aggregate.total_tests}")
    print(f"Passed:            {aggregate.passed_tests} ({aggregate.success_rate:.1%})")
    print(f"Failed:            {aggregate.failed_tests}")
    print(f"Overall accuracy:  {aggregate.overall_accuracy:.2%}")
    print(f"Avg latency:       {aggregate.average_latency_ms:.0f}ms")
    print(f"P95 latency:       {aggregate.p95_latency_ms:.0f}ms")
    print(f"Total cost:        ${aggregate.total_cost_usd:.4f}")

    # Compare with baseline
    thresholds = {
        'accuracy_drop_max': args.accuracy_threshold,
        'cost_increase_max': args.cost_threshold,
        'latency_increase_max': 0.20,
        'success_rate_min': 0.95
    }
    comparison = compare_with_baseline(aggregate, baseline, thresholds)

    # Print comparison
    if comparison['comparison_available']:
        print("\n" + "=" * 70)
        print("BASELINE COMPARISON")
        print("=" * 70)
        if comparison['has_regressions']:
            print("❌ REGRESSIONS DETECTED:")
            for reg in comparison['regressions']:
                print(f"   • {reg['metric'].upper()}: {reg}")
        else:
            print("✅ No regressions detected")

    # Save results
    save_results(aggregate, args.out)

    # Exit with appropriate code
    if comparison['has_regressions']:
        critical_regressions = [r for r in comparison['regressions'] if r['severity'] == 'critical']
        if critical_regressions:
            print("\n❌ CRITICAL REGRESSIONS FOUND - FAILING BUILD")
            sys.exit(1)
        else:
            print("\n⚠️  Warnings present but no critical regressions")
            sys.exit(0)
    else:
        print("\n✅ All checks passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
