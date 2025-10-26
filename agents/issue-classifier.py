#!/usr/bin/env python3
"""
GitHub Issue Classifier for InsightPulse Odoo
Classifies issues into Odoo SA / OCA / IPAI categories and generates plan.yaml
"""

import os
import yaml
import json
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class DecisionType(Enum):
    ODOO_SA = "odoo_sa"
    OCA = "oca"
    IPAI = "ipai"

class AreaType(Enum):
    PROCUREMENT = "procurement"
    EXPENSE = "expense"
    SUBSCRIPTIONS = "subscriptions"
    BI = "bi"
    ML = "ml"
    AGENT = "agent"
    CONNECTOR = "connector"

@dataclass
class IssueAnalysis:
    issue_number: int
    title: str
    body: str
    domain: str
    capabilities: List[str]
    dependencies: List[str]
    decision: DecisionType
    area: AreaType
    acceptance_criteria: List[str]

class IssueClassifier:
    def __init__(self):
        self.keyword_patterns = {
            DecisionType.ODOO_SA: [
                r'\b(standard|core|base|built-in|native)\b',
                r'\b(odoo\.com|enterprise)\b',
                r'\b(saas|cloud)\b'
            ],
            DecisionType.OCA: [
                r'\b(oca|community|open source|free)\b',
                r'\b(accounting|hr|project|manufacturing)\b',
                r'\b(module|addon|extension)\b'
            ],
            DecisionType.IPAI: [
                r'\b(ipai|insightpulse|custom|proprietary)\b',
                r'\b(procurement|expense|subscription)\b',
                r'\b(ml|ai|machine learning|prediction)\b',
                r'\b(agent|automation|workflow)\b'
            ]
        }
        
        self.area_patterns = {
            AreaType.PROCUREMENT: [
                r'\b(procurement|purchase|vendor|rfq|requisition)\b',
                r'\b(supplier|catalog|score)\b'
            ],
            AreaType.EXPENSE: [
                r'\b(expense|advance|policy|ocr|audit)\b',
                r'\b(reimbursement|receipt)\b'
            ],
            AreaType.SUBSCRIPTIONS: [
                r'\b(subscription|recurring|mrr|churn)\b',
                r'\b(usage|billing|dunning)\b'
            ],
            AreaType.BI: [
                r'\b(bi|dashboard|report|analytics)\b',
                r'\b(superset|tableau|visualization)\b'
            ],
            AreaType.ML: [
                r'\b(ml|ai|machine learning|prediction)\b',
                r'\b(model|training|inference)\b'
            ],
            AreaType.AGENT: [
                r'\b(agent|automation|workflow|classification)\b',
                r'\b(plan\.yaml|decision)\b'
            ],
            AreaType.CONNECTOR: [
                r'\b(connector|integration|api|sync)\b',
                r'\b(supabase|mindsdb|airbyte)\b'
            ]
        }

    def classify_issue(self, issue_number: int, title: str, body: str) -> IssueAnalysis:
        """Classify a GitHub issue and generate analysis"""
        
        # Extract domain from issue body
        domain = self._extract_section(body, "Domain")
        
        # Extract capabilities
        capabilities = self._extract_list_section(body, "Capabilities")
        
        # Extract dependencies
        dependencies = self._extract_list_section(body, "Dependencies")
        
        # Extract acceptance criteria
        acceptance_criteria = self._extract_list_section(body, "Acceptance Criteria")
        
        # Determine decision type
        decision = self._determine_decision(title, body)
        
        # Determine area
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
            acceptance_criteria=acceptance_criteria
        )

    def _extract_section(self, body: str, section_name: str) -> str:
        """Extract a specific section from issue body"""
        pattern = rf"## {section_name}\s*\n(.*?)(?=\n## |\n```|\n---|\n### |\n\n\n|\Z)"
        match = re.search(pattern, body, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""

    def _extract_list_section(self, body: str, section_name: str) -> List[str]:
        """Extract a list section from issue body"""
        section = self._extract_section(body, section_name)
        if not section:
            return []
        
        # Extract bullet points
        items = re.findall(r'[-*]\s*(.*)', section)
        return [item.strip() for item in items if item.strip()]

    def _determine_decision(self, title: str, body: str) -> DecisionType:
        """Determine the decision type based on content analysis"""
        text = f"{title} {body}".lower()
        
        scores = {}
        for decision_type, patterns in self.keyword_patterns.items():
            score = sum(len(re.findall(pattern, text)) for pattern in patterns)
            scores[decision_type] = score
        
        # Return the decision type with highest score
        return max(scores.items(), key=lambda x: x[1])[0]

    def _determine_area(self, title: str, body: str) -> AreaType:
        """Determine the area based on content analysis"""
        text = f"{title} {body}".lower()
        
        scores = {}
        for area_type, patterns in self.area_patterns.items():
            score = sum(len(re.findall(pattern, text)) for pattern in patterns)
            scores[area_type] = score
        
        # Return the area with highest score, default to connector
        return max(scores.items(), key=lambda x: x[1])[0] if scores else AreaType.CONNECTOR

    def generate_plan_yaml(self, analysis: IssueAnalysis) -> Dict:
        """Generate plan.yaml based on issue analysis"""
        
        plan = {
            'issue': analysis.issue_number,
            'title': analysis.title,
            'decision': analysis.decision.value,
            'area': analysis.area.value,
            'domain': analysis.domain,
            'implementation': {
                'type': self._get_implementation_type(analysis.decision),
                'modules': self._get_required_modules(analysis),
                'dependencies': analysis.dependencies,
                'acceptance_criteria': analysis.acceptance_criteria
            },
            'workflow': self._get_workflow_steps(analysis),
            'testing': self._get_testing_requirements(analysis),
            'deployment': self._get_deployment_requirements(analysis)
        }
        
        return plan

    def _get_implementation_type(self, decision: DecisionType) -> str:
        """Get implementation type based on decision"""
        return {
            DecisionType.ODOO_SA: "standard_module",
            DecisionType.OCA: "oca_module",
            DecisionType.IPAI: "custom_module"
        }[decision]

    def _get_required_modules(self, analysis: IssueAnalysis) -> List[str]:
        """Get required modules based on analysis"""
        base_modules = ["base", "mail"]
        
        if analysis.area == AreaType.PROCUREMENT:
            base_modules.extend(["purchase", "stock", "account", "product"])
        elif analysis.area == AreaType.EXPENSE:
            base_modules.extend(["hr", "hr_expense", "account"])
        elif analysis.area == AreaType.SUBSCRIPTIONS:
            base_modules.extend(["account", "product", "contract", "contract_sale"])
        elif analysis.area == AreaType.BI:
            base_modules.extend(["base"])
        elif analysis.area == AreaType.ML:
            base_modules.extend(["base", "queue_job"])
        elif analysis.area == AreaType.AGENT:
            base_modules.extend(["base"])
        elif analysis.area == AreaType.CONNECTOR:
            base_modules.extend(["base"])
            
        return base_modules

    def _get_workflow_steps(self, analysis: IssueAnalysis) -> List[str]:
        """Get workflow steps based on analysis"""
        steps = [
            "Create module structure",
            "Implement models",
            "Add security rules",
            "Create views and menus",
            "Add business logic",
            "Write tests"
        ]
        
        if analysis.area == AreaType.ML:
            steps.extend([
                "Set up feature extraction",
                "Configure ML pipeline",
                "Create prediction jobs"
            ])
        elif analysis.area == AreaType.CONNECTOR:
            steps.extend([
                "Configure external service",
                "Set up data sync",
                "Create API endpoints"
            ])
            
        return steps

    def _get_testing_requirements(self, analysis: IssueAnalysis) -> Dict:
        """Get testing requirements based on analysis"""
        return {
            'unit_tests': True,
            'integration_tests': analysis.area in [AreaType.ML, AreaType.CONNECTOR],
            'performance_tests': analysis.area == AreaType.ML,
            'security_tests': True
        }

    def _get_deployment_requirements(self, analysis: IssueAnalysis) -> Dict:
        """Get deployment requirements based on analysis"""
        return {
            'environment': ['development', 'staging', 'production'],
            'dependencies': analysis.dependencies,
            'migration_required': True,
            'backup_required': True
        }

def main():
    """Main function for testing the classifier"""
    # Example usage
    classifier = IssueClassifier()
    
    # Example issue data
    issue_data = {
        'number': 1,
        'title': 'Integrate Odoo with Apache Superset as a data source',
        'body': '''
## Domain
Business Intelligence and Analytics

## Capabilities
- Secure data sync from Odoo to Superset
- Automated dashboard creation
- Data lineage tracking

## Dependencies
- Odoo Postgres database
- Apache Superset instance
- Airbyte for data sync

## Acceptance Criteria
- Data sync completes within 5 minutes
- Dashboards load in under 3 seconds
- All sensitive data is properly masked

## Implementation Notes
Use Airbyte for CDC sync and Superset's SQL Lab for ad-hoc queries.
'''
    }
    
    # Classify the issue
    analysis = classifier.classify_issue(
        issue_data['number'],
        issue_data['title'],
        issue_data['body']
    )
    
    # Generate plan.yaml
    plan = classifier.generate_plan_yaml(analysis)
    
    print("Issue Analysis:")
    print(f"Decision: {analysis.decision.value}")
    print(f"Area: {analysis.area.value}")
    print(f"Domain: {analysis.domain}")
    
    print("\nGenerated plan.yaml:")
    print(yaml.dump(plan, default_flow_style=False))

if __name__ == "__main__":
    main()
