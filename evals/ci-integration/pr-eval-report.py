#!/usr/bin/env python3
"""
PR Evaluation Reporter
----------------------
Parses benchmark results and posts report to PR.
Fails CI if critical regressions detected.
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any


def load_results(path: Path) -> Dict[str, Any]:
    """Load benchmark results"""
    with open(path, 'r') as f:
        return json.load(f)


def format_metric(value: float, metric_type: str) -> str:
    """Format metric for display"""
    if metric_type == 'percentage':
        return f"{value:.2%}"
    elif metric_type == 'milliseconds':
        return f"{value:.0f}ms"
    elif metric_type == 'cost':
        return f"${value:.4f}"
    else:
        return f"{value:.2f}"


def generate_markdown_report(results: Dict[str, Any]) -> str:
    """Generate markdown report for PR"""
    report = []
    report.append("## 🤖 AI Golden-Set Evaluation Results\n")

    # Summary
    report.append("### Summary\n")
    report.append("| Metric | Value |")
    report.append("|--------|-------|")
    report.append(f"| Total Tests | {results['total_tests']} |")
    report.append(f"| Passed | {results['passed_tests']} ({results['success_rate']:.1%}) |")
    report.append(f"| Failed | {results['failed_tests']} |")
    report.append(f"| Overall Accuracy | {results['overall_accuracy']:.2%} |")
    report.append(f"| Avg Latency | {results['average_latency_ms']:.0f}ms |")
    report.append(f"| P95 Latency | {results['p95_latency_ms']:.0f}ms |")
    report.append(f"| Total Cost | ${results['total_cost_usd']:.4f} |")
    report.append("")

    # Test results by category
    report.append("### Results by Category\n")
    by_category = {}
    for test in results['test_results']:
        cat = test['category']
        if cat not in by_category:
            by_category[cat] = {'passed': 0, 'total': 0}
        by_category[cat]['total'] += 1
        if test['passed']:
            by_category[cat]['passed'] += 1

    report.append("| Category | Passed / Total | Success Rate |")
    report.append("|----------|----------------|--------------|")
    for cat, stats in sorted(by_category.items()):
        success_rate = stats['passed'] / stats['total'] if stats['total'] > 0 else 0
        emoji = "✅" if success_rate >= 0.95 else "⚠️" if success_rate >= 0.85 else "❌"
        report.append(f"| {emoji} {cat} | {stats['passed']} / {stats['total']} | {success_rate:.1%} |")
    report.append("")

    # Failed tests detail
    failed_tests = [t for t in results['test_results'] if not t['passed']]
    if failed_tests:
        report.append("### ❌ Failed Tests\n")
        for test in failed_tests:
            report.append(f"- **{test['test_id']}** ({test['category']}/{test['task']})")
            report.append(f"  - Accuracy: {test['accuracy']:.2%}")
            if test.get('error'):
                report.append(f"  - Error: `{test['error']}`")
        report.append("")

    return "\n".join(report)


def check_for_regressions(results: Dict[str, Any]) -> bool:
    """Check if there are critical regressions"""
    # Critical failures
    if results['success_rate'] < 0.95:
        return True

    if results['overall_accuracy'] < 0.90:
        return True

    return False


def main():
    parser = argparse.ArgumentParser(description="Generate PR evaluation report")
    parser.add_argument('--results', type=Path, required=True, help="Path to results JSON")
    parser.add_argument('--fail-on-regression', action='store_true', help="Fail CI on regressions")

    args = parser.parse_args()

    # Load results
    results = load_results(args.results)

    # Generate report
    report = generate_markdown_report(results)
    print(report)

    # Check for regressions
    has_regressions = check_for_regressions(results)

    if has_regressions and args.fail_on_regression:
        print("\n❌ Critical regressions detected - failing CI")
        sys.exit(1)
    elif has_regressions:
        print("\n⚠️  Regressions detected but not failing CI")
        sys.exit(0)
    else:
        print("\n✅ No regressions - all checks passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
