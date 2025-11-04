"""Shared types for issue classification."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Dict, List, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .schema import IssueClassificationPayload


class DecisionType(str, Enum):
    ODOO_SA = "odoo_sa"
    OCA = "oca"
    IPAI = "ipai"


class AreaType(str, Enum):
    PROCUREMENT = "procurement"
    EXPENSE = "expense"
    SUBSCRIPTIONS = "subscriptions"
    BI = "bi"
    ML = "ml"
    AGENT = "agent"
    CONNECTOR = "connector"


@dataclass(slots=True)
class IssueAnalysis:
    issue_number: int
    title: str
    body: str
    domain: str
    capabilities: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    decision: DecisionType = DecisionType.IPAI
    area: AreaType = AreaType.CONNECTOR
    acceptance_criteria: List[str] = field(default_factory=list)

    @classmethod
    def from_payload(
        cls,
        issue_number: int,
        title: str,
        body: str,
        payload: "IssueClassificationPayload",
    ) -> "IssueAnalysis":
        """Create an analysis from a structured LLM payload."""

        return cls(
            issue_number=issue_number,
            title=title,
            body=body,
            domain=payload.domain,
            capabilities=payload.capabilities,
            dependencies=payload.dependencies,
            decision=DecisionType(payload.decision),
            area=AreaType(payload.area),
            acceptance_criteria=payload.acceptance_criteria,
        )

    def to_plan(self) -> Dict:
        """Return a plan.yaml style dictionary."""

        return {
            "issue": self.issue_number,
            "title": self.title,
            "decision": self.decision.value,
            "area": self.area.value,
            "domain": self.domain,
            "implementation": {
                "type": self._get_implementation_type(),
                "modules": self._get_required_modules(),
                "dependencies": self.dependencies,
                "acceptance_criteria": self.acceptance_criteria,
            },
            "workflow": self._get_workflow_steps(),
            "testing": self._get_testing_requirements(),
            "deployment": self._get_deployment_requirements(),
        }

    def summary(self) -> Dict:
        """Return a serialisable summary of the analysis."""

        data = asdict(self)
        data["decision"] = self.decision.value
        data["area"] = self.area.value
        return data

    # Internal helper methods originally part of the monolithic script
    def _get_implementation_type(self) -> str:
        return {
            DecisionType.ODOO_SA: "standard_module",
            DecisionType.OCA: "oca_module",
            DecisionType.IPAI: "custom_module",
        }[self.decision]

    def _get_required_modules(self) -> List[str]:
        base_modules = ["base", "mail"]

        match self.area:
            case AreaType.PROCUREMENT:
                base_modules.extend(["purchase", "stock", "account", "product"])
            case AreaType.EXPENSE:
                base_modules.extend(["hr", "hr_expense", "account"])
            case AreaType.SUBSCRIPTIONS:
                base_modules.extend(["account", "product", "contract", "contract_sale"])
            case AreaType.ML:
                base_modules.extend(["base", "queue_job"])
            case AreaType.AGENT | AreaType.CONNECTOR | AreaType.BI:
                base_modules.extend(["base"])

        return base_modules

    def _get_workflow_steps(self) -> List[str]:
        steps = [
            "Create module structure",
            "Implement models",
            "Add security rules",
            "Create views and menus",
            "Add business logic",
            "Write tests",
        ]

        if self.area is AreaType.ML:
            steps.extend(
                [
                    "Set up feature extraction",
                    "Configure ML pipeline",
                    "Create prediction jobs",
                ]
            )
        elif self.area is AreaType.CONNECTOR:
            steps.extend(
                [
                    "Configure external service",
                    "Set up data sync",
                    "Create API endpoints",
                ]
            )

        return steps

    def _get_testing_requirements(self) -> Dict:
        return {
            "unit_tests": True,
            "integration_tests": self.area in (AreaType.ML, AreaType.CONNECTOR),
            "performance_tests": self.area is AreaType.ML,
            "security_tests": True,
        }

    def _get_deployment_requirements(self) -> Dict:
        return {
            "environment": ["development", "staging", "production"],
            "dependencies": self.dependencies,
            "migration_required": True,
            "backup_required": True,
        }
