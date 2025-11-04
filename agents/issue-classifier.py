#!/usr/bin/env python3
"""Hybrid GitHub issue classifier leveraging the OpenAI cookbook stack."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import yaml

from ai_stack import OpenAIConfig
from ai_stack.issues import HybridIssueClassifier, LLMIssueClassifier, RuleBasedIssueClassifier


def build_classifier(disable_llm: bool = False) -> HybridIssueClassifier:
    """Construct a classifier with optional LLM support."""

    rule_classifier = RuleBasedIssueClassifier()

    if disable_llm:
        return HybridIssueClassifier(llm_classifier=None, rule_classifier=rule_classifier)

    try:
        config = OpenAIConfig.from_env()
        llm_classifier = LLMIssueClassifier(config=config)
    except RuntimeError as exc:
        print(f"[issue-classifier] Falling back to rule-based mode: {exc}", file=sys.stderr)
        llm_classifier = None

    return HybridIssueClassifier(llm_classifier=llm_classifier, rule_classifier=rule_classifier)


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--issue-number", type=int, default=0, help="GitHub issue number")
    parser.add_argument("--title", required=True, help="Issue title")
    body_group = parser.add_mutually_exclusive_group(required=True)
    body_group.add_argument("--body", help="Raw issue body text")
    body_group.add_argument(
        "--body-file",
        type=Path,
        help="Path to a file containing the issue body (Markdown)",
    )
    parser.add_argument(
        "--disable-llm",
        action="store_true",
        help="Force the classifier to use the rule-based heuristics only",
    )
    parser.add_argument(
        "--plan-out",
        type=Path,
        help="Optional path to write the generated plan.yaml data",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        help="Optional path to write the structured classification JSON",
    )
    return parser.parse_args(argv)


def load_body(args: argparse.Namespace) -> str:
    if args.body is not None:
        return args.body.replace("\r\n", "\n").replace("\r", "\n")
    try:
        text = args.body_file.read_text(encoding="utf-8")
        return text.replace("\r\n", "\n").replace("\r", "\n")
    except OSError as exc:  # noqa: BLE001
        raise SystemExit(f"Unable to read issue body from {args.body_file}: {exc}") from exc


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    body = load_body(args)

    classifier = build_classifier(disable_llm=args.disable_llm)
    analysis = classifier.classify(args.issue_number, args.title, body)
    plan = analysis.to_plan()

    print("Issue analysis (JSON):")
    print(json.dumps(analysis.summary(), indent=2))
    print("\nGenerated plan.yaml:")
    print(yaml.dump(plan, default_flow_style=False, sort_keys=False))

    if args.plan_out:
        args.plan_out.write_text(yaml.dump(plan, sort_keys=False), encoding="utf-8")
    if args.json_out:
        args.json_out.write_text(json.dumps(analysis.summary(), indent=2), encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
