"""Issue classifiers backed by OpenAI models with rule-based fallback."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, TYPE_CHECKING

from ..clients import get_openai_client
from ..config import OpenAIConfig
from ..responses import ResponsesRunner, StructuredResponseError
from ..runtime import StackRuntime
from .prompt import (
    ISSUE_CLASSIFICATION_SYSTEM_PROMPT,
    ISSUE_CLASSIFICATION_USER_PROMPT,
)
from .schema import IssueClassificationPayload
from .types import AreaType, DecisionType, IssueAnalysis

if TYPE_CHECKING:  # pragma: no cover - imported for typing only
    from openai import OpenAI

LOGGER = logging.getLogger(__name__)


class IssueClassificationError(RuntimeError):
    """Raised when the LLM-backed classifier cannot produce a result."""


def _extract_section(body: str, section_name: str) -> str:
    target_header = f"## {section_name}".lower()
    collected: List[str] = []
    capture = False

    for line in body.splitlines():
        normalized = line.strip().lower()
        if normalized.startswith("## ") or normalized.startswith("### "):
            if capture:
                break
            capture = normalized == target_header
            continue

        if capture:
            collected.append(line.rstrip())

    return "\n".join(collected).strip()


def _extract_list_section(body: str, section_name: str) -> List[str]:
    section = _extract_section(body, section_name)
    if not section:
        return []
    items: List[str] = []
    for raw_line in section.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("-") or stripped.startswith("*"):
            items.append(stripped.lstrip("-* ").strip())
    return [item for item in items if item]


@dataclass(slots=True)
class RuleBasedIssueClassifier:
    """Baseline classifier using heuristics from the legacy script."""

    keyword_patterns: Dict[DecisionType, Iterable[str]] | None = None
    area_patterns: Dict[AreaType, Iterable[str]] | None = None

    def __post_init__(self) -> None:
        self.keyword_patterns = self.keyword_patterns or {
            DecisionType.ODOO_SA: [
                r"\\b(standard|core|base|built-in|native)\\b",
                r"\\b(odoo\\.com|enterprise)\\b",
                r"\\b(saas|cloud)\\b",
            ],
            DecisionType.OCA: [
                r"\\b(oca|community|open source|free)\\b",
                r"\\b(accounting|hr|project|manufacturing)\\b",
                r"\\b(module|addon|extension)\\b",
            ],
            DecisionType.IPAI: [
                r"\\b(ipai|insightpulse|custom|proprietary)\\b",
                r"\\b(procurement|expense|subscription)\\b",
                r"\\b(ml|ai|machine learning|prediction)\\b",
                r"\\b(agent|automation|workflow)\\b",
            ],
        }

        self.area_patterns = self.area_patterns or {
            AreaType.PROCUREMENT: [
                r"\\b(procurement|purchase|vendor|rfq|requisition)\\b",
                r"\\b(supplier|catalog|score)\\b",
            ],
            AreaType.EXPENSE: [
                r"\\b(expense|advance|policy|ocr|audit)\\b",
                r"\\b(reimbursement|receipt)\\b",
            ],
            AreaType.SUBSCRIPTIONS: [
                r"\\b(subscription|recurring|mrr|churn)\\b",
                r"\\b(usage|billing|dunning)\\b",
            ],
            AreaType.BI: [
                r"\\b(bi|dashboard|report|analytics)\\b",
                r"\\b(superset|tableau|visualization)\\b",
            ],
            AreaType.ML: [
                r"\\b(ml|ai|machine learning|prediction)\\b",
                r"\\b(model|training|inference)\\b",
            ],
            AreaType.AGENT: [
                r"\\b(agent|automation|workflow|classification)\\b",
                r"\\b(plan\\.yaml|decision)\\b",
            ],
            AreaType.CONNECTOR: [
                r"\\b(connector|integration|api|sync)\\b",
                r"\\b(supabase|mindsdb|airbyte)\\b",
            ],
        }

    def classify(self, issue_number: int, title: str, body: str) -> IssueAnalysis:
        domain = _extract_section(body, "Domain")
        capabilities = _extract_list_section(body, "Capabilities")
        dependencies = _extract_list_section(body, "Dependencies")
        acceptance = _extract_list_section(body, "Acceptance Criteria")

        decision = self._determine_decision(title, body)
        area = self._determine_area(title, body)

        return IssueAnalysis(
            issue_number=issue_number,
            title=title,
            body=body,
            domain=domain,
            capabilities=capabilities,
            dependencies=dependencies,
            decision=decision,
            area=area,
            acceptance_criteria=acceptance,
        )

    def _determine_decision(self, title: str, body: str) -> DecisionType:
        text = f"{title} {body}".lower()
        scores = {
            decision_type: sum(len(re.findall(pattern, text)) for pattern in patterns)
            for decision_type, patterns in self.keyword_patterns.items()
        }
        return max(scores.items(), key=lambda item: item[1])[0]

    def _determine_area(self, title: str, body: str) -> AreaType:
        text = f"{title} {body}".lower()
        scores = {
            area_type: sum(len(re.findall(pattern, text)) for pattern in patterns)
            for area_type, patterns in self.area_patterns.items()
        }
        return max(scores.items(), key=lambda item: item[1])[0] if scores else AreaType.CONNECTOR


@dataclass(slots=True)
class LLMIssueClassifier:
    """Classifier that defers to OpenAI's Responses API."""

    client: Optional["OpenAI"] = None
    config: Optional[OpenAIConfig] = None
    runtime: Optional[StackRuntime] = None
    runner: Optional[ResponsesRunner] = None

    def __post_init__(self) -> None:
        if self.runtime:
            self.config = self.runtime.config
            self.client = self.runtime.ensure_client()
            self.runner = self.runtime.responses_runner()
        else:
            self.config = self.config or OpenAIConfig.from_env()
            self.client = self.client or get_openai_client(self.config)
            self.runner = ResponsesRunner(client=self.client, model=self.config.model)

    def classify(self, issue_number: int, title: str, body: str) -> IssueAnalysis:
        formatted_issue = self._format_issue(title, body)
        if self.runner is None:
            raise IssueClassificationError("LLM runner not initialised")

        try:
            payload = self.runner.structured(
                input_messages=[
                    {
                        "role": "system",
                        "content": [
                            {"type": "text", "text": ISSUE_CLASSIFICATION_SYSTEM_PROMPT},
                        ],
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": ISSUE_CLASSIFICATION_USER_PROMPT.format(
                                    issue_body=formatted_issue
                                ),
                            }
                        ],
                    },
                ],
                response_model=IssueClassificationPayload,
            )
        except StructuredResponseError as exc:
            raise IssueClassificationError("LLM structured response failed") from exc

        return IssueAnalysis.from_payload(
            issue_number=issue_number,
            title=title,
            body=body,
            payload=payload,
        )

    @staticmethod
    def _format_issue(title: str, body: str) -> str:
        return f"Title: {title}\n\nBody:\n{body.strip()}"


@dataclass(slots=True)
class HybridIssueClassifier:
    """Try the LLM classifier and fall back to the rule-based heuristics."""

    llm_classifier: Optional[LLMIssueClassifier] = None
    rule_classifier: RuleBasedIssueClassifier = field(default_factory=RuleBasedIssueClassifier)

    def classify(self, issue_number: int, title: str, body: str) -> IssueAnalysis:
        if self.llm_classifier is not None:
            try:
                return self.llm_classifier.classify(issue_number, title, body)
            except (IssueClassificationError, RuntimeError) as exc:
                LOGGER.warning("LLM classification failed: %s", exc)

        return self.rule_classifier.classify(issue_number, title, body)
