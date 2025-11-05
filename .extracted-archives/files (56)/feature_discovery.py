#!/usr/bin/env python3
"""
Automated Feature Discovery System for InsightPulse Odoo
Scans __manifest__.py files and extracts module metadata for backlog management
"""

import os
import ast
import json
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime


@dataclass
class FeatureModule:
    """Represents a discovered Odoo feature module"""
    module_name: str
    display_name: str
    description: str
    version: str
    author: str
    category: str
    depends: List[str]
    external_dependencies: Dict[str, List[str]]
    file_path: str
    business_area: str
    deployment_status: str
    priority: str
    story_points: Optional[int]
    epic: str
    tags: List[str]
    github_url: str
    discovered_at: str
    external_id: str  # For Notion deduplication


class FeatureClassifier:
    """Classifies features by business area and determines deployment status"""
    
    # Business area classification rules
    BUSINESS_AREAS = {
        'Finance & Accounting': [
            'account', 'invoice', 'payment', 'tax', 'bir', 'vat', 
            'finance', 'treasury', 'budget', 'cost', 'expense'
        ],
        'Procurement & Supply Chain': [
            'purchase', 'procurement', 'vendor', 'supplier', 'po', 
            'ariba', 'cxml', 'sourcing', 'rfq'
        ],
        'Project & Portfolio Management': [
            'project', 'ppm', 'program', 'portfolio', 'task', 
            'timesheet', 'clarity', 'resource'
        ],
        'Document & Data Management': [
            'doc', 'document', 'ocr', 'ai', 'attachment', 
            'scan', 'upload', 'paddleocr'
        ],
        'Integration & API': [
            'mcp', 'integration', 'api', 'connector', 'sync', 
            'webhook', 'supabase', 'notion', 'superset'
        ],
        'Compliance & Governance': [
            'consent', 'gdpr', 'audit', 'compliance', 'policy', 
            'approval', 'workflow', 'gate'
        ],
        'HR & Employee Management': [
            'hr', 'employee', 'leave', 'attendance', 'payroll', 
            'recruitment', 'appraisal'
        ],
        'Analytics & Reporting': [
            'report', 'dashboard', 'analytics', 'bi', 'tableau', 
            'superset', 'metric', 'kpi'
        ],
        'Core Infrastructure': [
            'core', 'base', 'framework', 'utility', 'helper', 
            'multi_company', 'tenant'
        ]
    }
    
    # Epic classification
    EPICS = {
        'Finance SSC Automation': ['bir', 'tax', 'vat', 'closing', 'finance', 'account'],
        'SAP Replacement Suite': ['ariba', 'concur', 'clarity', 'procurement', 'expense'],
        'AI Document Processing': ['doc_ai', 'ocr', 'paddle', 'extraction', 'entity'],
        'Enterprise Integration': ['mcp', 'integration', 'api', 'sync', 'connector'],
        'PPM & Resource Planning': ['ppm', 'project', 'program', 'portfolio', 'resource'],
        'Approval & Workflow Engine': ['approval', 'workflow', 'escalation', 'gate'],
        'Compliance & Audit': ['consent', 'gdpr', 'audit', 'compliance', 'policy'],
        'Cost & Margin Management': ['cost', 'margin', 'pricing', 'budget', 'sheet']
    }
    
    @staticmethod
    def classify_business_area(module_name: str, description: str, category: str) -> str:
        """Determine business area based on module characteristics"""
        text = f"{module_name} {description} {category}".lower()
        
        scores = {}
        for area, keywords in FeatureClassifier.BUSINESS_AREAS.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                scores[area] = score
        
        if scores:
            return max(scores, key=scores.get)
        return 'Other'
    
    @staticmethod
    def classify_epic(module_name: str, description: str) -> str:
        """Determine which epic this feature belongs to"""
        text = f"{module_name} {description}".lower()
        
        scores = {}
        for epic, keywords in FeatureClassifier.EPICS.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                scores[epic] = score
        
        if scores:
            return max(scores, key=scores.get)
        return 'Unclassified'
    
    @staticmethod
    def determine_status(module_path: str, manifest_data: Dict) -> str:
        """Determine deployment status based on location and version"""
        # Check if in production paths
        if 'addons/custom' in module_path or 'addons/insightpulse' in module_path:
            version = manifest_data.get('version', '0.0.0')
            if version.startswith('1.') or version.startswith('2.'):
                return 'Production'
            return 'Staging'
        
        if 'odoo_addons' in module_path:
            return 'Development'
        
        if 'experimental' in module_path or 'draft' in module_path:
            return 'Backlog'
        
        return 'Planning'
    
    @staticmethod
    def estimate_story_points(manifest_data: Dict, description: str) -> int:
        """Estimate story points based on complexity indicators"""
        points = 3  # Base points
        
        # Complexity from dependencies
        depends = manifest_data.get('depends', [])
        if len(depends) > 5:
            points += 2
        elif len(depends) > 10:
            points += 5
        
        # Complexity from external dependencies
        external_deps = manifest_data.get('external_dependencies', {})
        if external_deps:
            points += len(external_deps) * 2
        
        # Complexity from description keywords
        complex_keywords = ['integration', 'sync', 'migration', 'automation', 
                          'workflow', 'reporting', 'ai', 'ml']
        complexity_score = sum(1 for keyword in complex_keywords if keyword in description.lower())
        points += complexity_score
        
        # Cap at 13 (Fibonacci)
        fibonacci = [1, 2, 3, 5, 8, 13]
        return min([f for f in fibonacci if f >= points], default=13)
    
    @staticmethod
    def assign_priority(epic: str, status: str, dependencies: List[str]) -> str:
        """Assign priority based on strategic importance and dependencies"""
        # High priority epics
        high_priority_epics = [
            'Finance SSC Automation', 
            'SAP Replacement Suite',
            'AI Document Processing'
        ]
        
        # Core infrastructure dependencies indicate high priority
        core_deps = ['ipai_core', 'base', 'account', 'purchase']
        has_core_deps = any(dep in core_deps for dep in dependencies)
        
        if epic in high_priority_epics or status == 'Production':
            return 'P0 - Critical'
        elif has_core_deps or status == 'Staging':
            return 'P1 - High'
        elif status == 'Development':
            return 'P2 - Medium'
        else:
            return 'P3 - Low'
    
    @staticmethod
    def extract_tags(module_name: str, category: str, manifest_data: Dict) -> List[str]:
        """Extract relevant tags for filtering and search"""
        tags = []
        
        # Category-based tags
        if category:
            tags.append(category)
        
        # Technology tags
        if 'mcp' in module_name.lower():
            tags.append('MCP')
        if 'ai' in module_name.lower() or 'ml' in module_name.lower():
            tags.append('AI/ML')
        if 'api' in module_name.lower():
            tags.append('API')
        
        # Integration tags
        external_deps = manifest_data.get('external_dependencies', {})
        if 'python' in external_deps:
            for dep in external_deps['python']:
                if dep in ['supabase', 'notion', 'paddleocr', 'openai']:
                    tags.append(dep.upper())
        
        # BIR/Compliance tags
        if 'bir' in module_name.lower():
            tags.append('BIR')
            tags.append('Philippine Tax')
        
        # Agency tags (from Jake's context)
        agencies = ['RIM', 'CKVC', 'BOM', 'JPAL', 'JLI', 'JAP', 'LAS', 'RMQB']
        for agency in agencies:
            if agency.lower() in module_name.lower():
                tags.append(f'Agency-{agency}')
        
        return list(set(tags))  # Remove duplicates


class FeatureDiscovery:
    """Main feature discovery engine"""
    
    def __init__(self, repo_path: str = ".", github_repo: str = "jgtolentino/insightpulse-odoo"):
        self.repo_path = Path(repo_path)
        self.github_repo = github_repo
        self.classifier = FeatureClassifier()
        self.features: List[FeatureModule] = []
    
    def parse_manifest(self, manifest_path: Path) -> Optional[Dict]:
        """Parse __manifest__.py file and extract data"""
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract the dictionary using ast
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Dict):
                    # Convert AST node to dict
                    manifest_dict = ast.literal_eval(content.split('=', 1)[1].strip())
                    return manifest_dict
            
            return None
        except Exception as e:
            print(f"Error parsing {manifest_path}: {e}")
            return None
    
    def discover_modules(self) -> List[FeatureModule]:
        """Scan repository and discover all feature modules"""
        print("🔍 Starting feature discovery...")
        
        # Find all __manifest__.py files
        manifest_files = list(self.repo_path.rglob("__manifest__.py"))
        print(f"Found {len(manifest_files)} manifest files")
        
        for manifest_path in manifest_files:
            manifest_data = self.parse_manifest(manifest_path)
            if not manifest_data:
                continue
            
            module_dir = manifest_path.parent
            module_name = module_dir.name
            
            # Extract basic info
            display_name = manifest_data.get('name', module_name)
            description = manifest_data.get('summary', manifest_data.get('description', ''))
            version = manifest_data.get('version', '0.0.0')
            author = manifest_data.get('author', 'InsightPulse')
            category = manifest_data.get('category', 'Uncategorized')
            depends = manifest_data.get('depends', [])
            external_deps = manifest_data.get('external_dependencies', {})
            
            # Relative path from repo root
            rel_path = str(manifest_path.relative_to(self.repo_path))
            
            # Classify
            business_area = self.classifier.classify_business_area(
                module_name, description, category
            )
            epic = self.classifier.classify_epic(module_name, description)
            status = self.classifier.determine_status(rel_path, manifest_data)
            story_points = self.classifier.estimate_story_points(manifest_data, description)
            priority = self.classifier.assign_priority(epic, status, depends)
            tags = self.classifier.extract_tags(module_name, category, manifest_data)
            
            # GitHub URL
            github_url = f"https://github.com/{self.github_repo}/blob/main/{rel_path}"
            
            # External ID for Notion deduplication
            external_id = f"odoo_module_{module_name}"
            
            feature = FeatureModule(
                module_name=module_name,
                display_name=display_name,
                description=description,
                version=version,
                author=author,
                category=category,
                depends=depends,
                external_dependencies=external_deps,
                file_path=rel_path,
                business_area=business_area,
                deployment_status=status,
                priority=priority,
                story_points=story_points,
                epic=epic,
                tags=tags,
                github_url=github_url,
                external_id=external_id,
                discovered_at=datetime.now().isoformat()
            )
            
            self.features.append(feature)
            print(f"✅ Discovered: {display_name} ({business_area})")
        
        print(f"\n🎉 Discovery complete! Found {len(self.features)} features")
        return self.features
    
    def export_to_json(self, output_path: str = "feature_backlog.json"):
        """Export discovered features to JSON"""
        data = {
            "discovered_at": datetime.now().isoformat(),
            "repository": self.github_repo,
            "total_features": len(self.features),
            "features": [asdict(f) for f in self.features]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"📄 Exported to {output_path}")
        return output_path
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate summary statistics"""
        if not self.features:
            return {}
        
        summary = {
            "total_features": len(self.features),
            "by_business_area": {},
            "by_status": {},
            "by_priority": {},
            "by_epic": {},
            "total_story_points": 0,
            "top_dependencies": {}
        }
        
        # Count by business area
        for feature in self.features:
            area = feature.business_area
            summary["by_business_area"][area] = summary["by_business_area"].get(area, 0) + 1
            
            status = feature.deployment_status
            summary["by_status"][status] = summary["by_status"].get(status, 0) + 1
            
            priority = feature.priority
            summary["by_priority"][priority] = summary["by_priority"].get(priority, 0) + 1
            
            epic = feature.epic
            summary["by_epic"][epic] = summary["by_epic"].get(epic, 0) + 1
            
            summary["total_story_points"] += feature.story_points or 0
            
            # Track dependencies
            for dep in feature.depends:
                summary["top_dependencies"][dep] = summary["top_dependencies"].get(dep, 0) + 1
        
        # Sort top dependencies
        summary["top_dependencies"] = dict(
            sorted(summary["top_dependencies"].items(), key=lambda x: x[1], reverse=True)[:10]
        )
        
        return summary
    
    def print_summary(self):
        """Print human-readable summary"""
        summary = self.generate_summary_report()
        
        print("\n" + "="*80)
        print("📊 FEATURE BACKLOG SUMMARY")
        print("="*80)
        print(f"\nTotal Features: {summary['total_features']}")
        print(f"Total Story Points: {summary['total_story_points']}")
        
        print("\n📂 By Business Area:")
        for area, count in sorted(summary['by_business_area'].items(), key=lambda x: x[1], reverse=True):
            print(f"  • {area}: {count}")
        
        print("\n🚀 By Deployment Status:")
        for status, count in sorted(summary['by_status'].items(), key=lambda x: x[1], reverse=True):
            print(f"  • {status}: {count}")
        
        print("\n⚡ By Priority:")
        for priority, count in sorted(summary['by_priority'].items()):
            print(f"  • {priority}: {count}")
        
        print("\n📋 By Epic:")
        for epic, count in sorted(summary['by_epic'].items(), key=lambda x: x[1], reverse=True):
            print(f"  • {epic}: {count}")
        
        print("\n🔗 Top Dependencies:")
        for dep, count in list(summary['top_dependencies'].items())[:10]:
            print(f"  • {dep}: {count} modules")
        
        print("\n" + "="*80)


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Automated Feature Discovery for Odoo')
    parser.add_argument('--repo-path', default='.', help='Path to Odoo repository')
    parser.add_argument('--output', default='feature_backlog.json', help='Output JSON file')
    parser.add_argument('--github-repo', default='jgtolentino/insightpulse-odoo', 
                       help='GitHub repository name')
    
    args = parser.parse_args()
    
    # Run discovery
    discovery = FeatureDiscovery(
        repo_path=args.repo_path,
        github_repo=args.github_repo
    )
    
    features = discovery.discover_modules()
    discovery.export_to_json(args.output)
    discovery.print_summary()
    
    print(f"\n✅ Feature discovery complete!")
    print(f"📦 Run notion_sync.py to push features to Notion")


if __name__ == "__main__":
    main()
