#!/usr/bin/env python3
"""
Suggest Skills Based on Code Analysis

This script analyzes the codebase to suggest new skills that should be created.
It uses complexity metrics, change frequency, and coupling analysis to identify
code areas that warrant dedicated skill documentation.

Usage:
    python suggest-skills.py
    python suggest-skills.py --repo /path/to/repo --output suggestions.json
    python suggest-skills.py --min-complexity 10 --min-changes 5
"""

import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from collections import defaultdict
import subprocess
import ast
import re

try:
    from radon.complexity import cc_visit
    from radon.metrics import mi_visit, h_visit
    RADON_AVAILABLE = True
except ImportError:
    RADON_AVAILABLE = False
    print("⚠️  Warning: radon not installed. Install with: pip install radon")


class SkillSuggester:
    """Suggest new skills based on code analysis."""

    def __init__(
        self,
        repo_path: str = ".",
        min_complexity: int = 10,
        min_changes: int = 5,
        days_back: int = 90
    ):
        self.repo_path = repo_path
        self.min_complexity = min_complexity
        self.min_changes = min_changes
        self.days_back = days_back
        self.suggestions = []

    def analyze_and_suggest(self) -> List[Dict]:
        """
        Analyze codebase and generate skill suggestions.

        Returns:
            List of skill suggestions with priority scores
        """
        print(f"🔍 Analyzing repository: {self.repo_path}")
        print(f"   Min complexity: {self.min_complexity}")
        print(f"   Min changes: {self.min_changes}")
        print(f"   Time period: {self.days_back} days")

        # 1. Analyze complexity
        print("\n📊 Analyzing code complexity...")
        complex_modules = self._analyze_complexity()

        # 2. Analyze change frequency
        print("\n📈 Analyzing change frequency...")
        frequently_changed = self._analyze_change_frequency()

        # 3. Analyze coupling
        print("\n🔗 Analyzing module coupling...")
        highly_coupled = self._analyze_coupling()

        # 4. Analyze missing patterns
        print("\n🎯 Analyzing missing patterns...")
        missing_patterns = self._analyze_missing_patterns()

        # 5. Generate suggestions
        print("\n💡 Generating skill suggestions...")
        self._generate_suggestions(
            complex_modules,
            frequently_changed,
            highly_coupled,
            missing_patterns
        )

        # 6. Sort by priority
        self.suggestions.sort(key=lambda x: x['priority_score'], reverse=True)

        print(f"\n✅ Generated {len(self.suggestions)} skill suggestions")

        return self.suggestions

    def _analyze_complexity(self) -> List[Dict]:
        """Analyze code complexity to find candidates for skill documentation."""
        complex_modules = []

        if not RADON_AVAILABLE:
            print("   ⚠️  Radon not available, skipping complexity analysis")
            return complex_modules

        for root, dirs, files in os.walk(self.repo_path):
            # Skip common directories
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}]

            for file in files:
                if not file.endswith('.py'):
                    continue

                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r') as f:
                        source_code = f.read()

                    # Calculate complexity
                    complexity_results = cc_visit(source_code)
                    total_complexity = sum(block.complexity for block in complexity_results)
                    avg_complexity = total_complexity / len(complexity_results) if complexity_results else 0

                    # Calculate maintainability index
                    mi_score = mi_visit(source_code, multi=True)

                    if avg_complexity >= self.min_complexity or mi_score < 20:
                        complex_modules.append({
                            'file_path': file_path,
                            'avg_complexity': avg_complexity,
                            'total_complexity': total_complexity,
                            'maintainability_index': mi_score,
                            'num_functions': len(complexity_results),
                            'reason': 'high_complexity'
                        })

                except Exception as e:
                    pass  # Skip files that can't be parsed

        print(f"   Found {len(complex_modules)} complex modules")
        return complex_modules

    def _analyze_change_frequency(self) -> List[Dict]:
        """Analyze git history to find frequently changed files."""
        frequently_changed = []

        try:
            # Check if we're in a git repository
            subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                cwd=self.repo_path,
                capture_output=True,
                check=True
            )

            # Get commit history for last N days
            since_date = (datetime.now() - timedelta(days=self.days_back)).strftime('%Y-%m-%d')

            result = subprocess.run(
                ['git', 'log', f'--since={since_date}', '--name-only', '--pretty=format:'],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                # Count changes per file
                change_counts = defaultdict(int)
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if line and line.endswith('.py'):
                        change_counts[line] += 1

                # Filter by minimum changes
                for file_path, count in change_counts.items():
                    if count >= self.min_changes:
                        full_path = os.path.join(self.repo_path, file_path)
                        if os.path.exists(full_path):
                            frequently_changed.append({
                                'file_path': full_path,
                                'change_count': count,
                                'reason': 'high_change_frequency'
                            })

                print(f"   Found {len(frequently_changed)} frequently changed files")
            else:
                print("   ⚠️  Could not analyze git history")

        except subprocess.CalledProcessError:
            print("   ⚠️  Not a git repository or git not available")
        except Exception as e:
            print(f"   ⚠️  Error analyzing git history: {e}")

        return frequently_changed

    def _analyze_coupling(self) -> List[Dict]:
        """Analyze import dependencies to find highly coupled modules."""
        highly_coupled = []
        import_graph = defaultdict(set)

        # Build import graph
        for root, dirs, files in os.walk(self.repo_path):
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}]

            for file in files:
                if not file.endswith('.py'):
                    continue

                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r') as f:
                        source_code = f.read()

                    tree = ast.parse(source_code)
                    imports = set()

                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                imports.add(alias.name.split('.')[0])
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                imports.add(node.module.split('.')[0])

                    import_graph[file_path] = imports

                except Exception:
                    pass

        # Calculate coupling (number of imports + number of modules importing this one)
        for file_path, imports in import_graph.items():
            # Count how many other files import this module
            imported_by = sum(
                1 for other_imports in import_graph.values()
                if any(imp in str(file_path) for imp in other_imports)
            )

            total_coupling = len(imports) + imported_by

            if total_coupling >= 10:  # Highly coupled threshold
                highly_coupled.append({
                    'file_path': file_path,
                    'imports': len(imports),
                    'imported_by': imported_by,
                    'total_coupling': total_coupling,
                    'reason': 'high_coupling'
                })

        print(f"   Found {len(highly_coupled)} highly coupled modules")
        return highly_coupled

    def _analyze_missing_patterns(self) -> List[Dict]:
        """Analyze codebase for common patterns that lack skill documentation."""
        missing_patterns = []

        # Define pattern signatures
        patterns = {
            'api_integration': {
                'keywords': ['requests', 'httpx', 'aiohttp', 'API', 'endpoint', 'webhook'],
                'description': 'API Integration & External Service Communication'
            },
            'state_machine': {
                'keywords': ['state', 'workflow', 'transition', 'FSM', 'status'],
                'description': 'State Machine & Workflow Management'
            },
            'data_validation': {
                'keywords': ['validate', 'validator', 'schema', 'pydantic', 'marshmallow'],
                'description': 'Data Validation & Schema Management'
            },
            'caching': {
                'keywords': ['cache', 'redis', 'memcached', '@lru_cache', 'memoize'],
                'description': 'Caching & Performance Optimization'
            },
            'async_processing': {
                'keywords': ['async', 'await', 'celery', 'queue', 'background', 'task'],
                'description': 'Asynchronous Processing & Background Jobs'
            },
            'security': {
                'keywords': ['auth', 'permission', 'security', 'encrypt', 'jwt', 'token'],
                'description': 'Security & Authentication'
            },
            'testing': {
                'keywords': ['test_', 'pytest', 'unittest', 'mock', 'fixture'],
                'description': 'Testing & Quality Assurance'
            },
            'database': {
                'keywords': ['query', 'SQL', 'ORM', 'migration', 'transaction'],
                'description': 'Database Design & Query Optimization'
            }
        }

        # Scan codebase for pattern usage
        pattern_files = defaultdict(list)

        for root, dirs, files in os.walk(self.repo_path):
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}]

            for file in files:
                if not file.endswith('.py'):
                    continue

                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()

                    for pattern_name, pattern_info in patterns.items():
                        for keyword in pattern_info['keywords']:
                            if re.search(rf'\b{re.escape(keyword)}\b', content, re.IGNORECASE):
                                pattern_files[pattern_name].append(file_path)
                                break

                except Exception:
                    pass

        # Suggest skills for patterns with significant usage
        for pattern_name, files in pattern_files.items():
            if len(files) >= 3:  # Pattern used in 3+ files
                pattern_info = patterns[pattern_name]
                missing_patterns.append({
                    'pattern_name': pattern_name,
                    'description': pattern_info['description'],
                    'file_count': len(files),
                    'files': files[:5],  # First 5 examples
                    'reason': 'missing_pattern_skill'
                })

        print(f"   Found {len(missing_patterns)} missing pattern skills")
        return missing_patterns

    def _generate_suggestions(
        self,
        complex_modules: List[Dict],
        frequently_changed: List[Dict],
        highly_coupled: List[Dict],
        missing_patterns: List[Dict]
    ):
        """Generate skill suggestions from analysis results."""

        # Combine all analysis results
        file_scores = defaultdict(lambda: {
            'reasons': [],
            'metrics': {},
            'priority_score': 0.0
        })

        # Process complex modules
        for module in complex_modules:
            file_path = module['file_path']
            file_scores[file_path]['reasons'].append('High complexity')
            file_scores[file_path]['metrics']['complexity'] = module['avg_complexity']
            file_scores[file_path]['priority_score'] += module['avg_complexity'] * 2

        # Process frequently changed files
        for module in frequently_changed:
            file_path = module['file_path']
            file_scores[file_path]['reasons'].append('Frequently changed')
            file_scores[file_path]['metrics']['change_count'] = module['change_count']
            file_scores[file_path]['priority_score'] += module['change_count'] * 3

        # Process highly coupled modules
        for module in highly_coupled:
            file_path = module['file_path']
            file_scores[file_path]['reasons'].append('Highly coupled')
            file_scores[file_path]['metrics']['coupling'] = module['total_coupling']
            file_scores[file_path]['priority_score'] += module['total_coupling'] * 1.5

        # Generate suggestions for individual modules
        for file_path, data in file_scores.items():
            # Generate skill ID
            rel_path = os.path.relpath(file_path, self.repo_path)
            skill_id = self._generate_skill_id(rel_path)

            # Generate skill name
            module_name = Path(file_path).stem
            skill_name = self._humanize_name(module_name)

            suggestion = {
                'skill_id': skill_id,
                'skill_name': f"{skill_name} Specialist",
                'category': self._infer_category(file_path),
                'file_path': file_path,
                'reasons': data['reasons'],
                'metrics': data['metrics'],
                'priority_score': data['priority_score'],
                'suggested_expertise_level': self._suggest_expertise_level(data['metrics']),
                'type': 'module_skill'
            }

            self.suggestions.append(suggestion)

        # Generate suggestions for missing patterns
        for pattern in missing_patterns:
            suggestion = {
                'skill_id': f"{pattern['pattern_name']}-specialist",
                'skill_name': pattern['description'],
                'category': 'Cross-Cutting Concern',
                'pattern_name': pattern['pattern_name'],
                'file_count': pattern['file_count'],
                'example_files': pattern['files'],
                'reasons': ['Pattern used across multiple modules without dedicated skill'],
                'metrics': {'file_count': pattern['file_count']},
                'priority_score': pattern['file_count'] * 5,  # High priority for cross-cutting concerns
                'suggested_expertise_level': 'Advanced',
                'type': 'pattern_skill'
            }

            self.suggestions.append(suggestion)

    def _generate_skill_id(self, rel_path: str) -> str:
        """Generate skill ID from file path."""
        parts = Path(rel_path).parts
        # Take last 2-3 meaningful parts
        meaningful_parts = [p for p in parts if p not in {'custom', 'addons', 'src', 'lib'}]
        skill_id = '-'.join(meaningful_parts[-2:]).replace('.py', '')
        skill_id = re.sub(r'[^a-z0-9-]', '-', skill_id.lower())
        return skill_id

    def _humanize_name(self, name: str) -> str:
        """Convert snake_case to Title Case."""
        return ' '.join(word.capitalize() for word in name.split('_'))

    def _infer_category(self, file_path: str) -> str:
        """Infer skill category from file path."""
        path_lower = file_path.lower()

        if 'finance' in path_lower or 'accounting' in path_lower:
            return 'Finance & Accounting'
        elif 'expense' in path_lower or 'reimbursement' in path_lower:
            return 'Expense Management'
        elif 'procurement' in path_lower or 'purchase' in path_lower:
            return 'Procurement'
        elif 'workflow' in path_lower or 'approval' in path_lower:
            return 'Workflow Automation'
        elif 'report' in path_lower or 'dashboard' in path_lower:
            return 'Reporting & Analytics'
        elif 'api' in path_lower or 'integration' in path_lower:
            return 'Integration & APIs'
        elif 'test' in path_lower:
            return 'Testing & Quality'
        elif 'model' in path_lower:
            return 'Data Modeling'
        else:
            return 'Business Logic'

    def _suggest_expertise_level(self, metrics: Dict) -> str:
        """Suggest expertise level based on metrics."""
        complexity = metrics.get('complexity', 0)
        coupling = metrics.get('coupling', 0)
        change_count = metrics.get('change_count', 0)

        # Calculate composite score
        score = complexity + (coupling * 0.5) + (change_count * 0.3)

        if score >= 30:
            return 'Expert'
        elif score >= 20:
            return 'Advanced'
        elif score >= 10:
            return 'Intermediate'
        else:
            return 'Beginner'

    def save_suggestions(self, output_path: str):
        """Save suggestions to JSON file."""
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

        output = {
            'generated_at': datetime.now().isoformat(),
            'analysis_params': {
                'repo_path': self.repo_path,
                'min_complexity': self.min_complexity,
                'min_changes': self.min_changes,
                'days_back': self.days_back
            },
            'total_suggestions': len(self.suggestions),
            'suggestions': self.suggestions
        }

        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"💾 Saved suggestions to: {output_path}")

    def print_summary(self):
        """Print human-readable summary of suggestions."""
        if not self.suggestions:
            print("\n📋 No skill suggestions generated")
            return

        print(f"\n📋 Top {min(10, len(self.suggestions))} Skill Suggestions:")
        print("=" * 80)

        for i, suggestion in enumerate(self.suggestions[:10], 1):
            print(f"\n{i}. {suggestion['skill_name']}")
            print(f"   ID: {suggestion['skill_id']}")
            print(f"   Category: {suggestion['category']}")
            print(f"   Priority Score: {suggestion['priority_score']:.1f}")
            print(f"   Expertise Level: {suggestion['suggested_expertise_level']}")
            print(f"   Reasons: {', '.join(suggestion['reasons'])}")

            if suggestion['type'] == 'module_skill':
                print(f"   File: {suggestion['file_path']}")
                if 'complexity' in suggestion['metrics']:
                    print(f"   Avg Complexity: {suggestion['metrics']['complexity']:.1f}")
            else:  # pattern_skill
                print(f"   Pattern: {suggestion['pattern_name']}")
                print(f"   Used in {suggestion['file_count']} files")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Suggest skills based on code analysis"
    )
    parser.add_argument(
        '--repo',
        default='.',
        help='Repository path to analyze'
    )
    parser.add_argument(
        '--output',
        default='skills/suggestions.json',
        help='Output path for suggestions JSON'
    )
    parser.add_argument(
        '--min-complexity',
        type=int,
        default=10,
        help='Minimum complexity threshold'
    )
    parser.add_argument(
        '--min-changes',
        type=int,
        default=5,
        help='Minimum number of changes in time period'
    )
    parser.add_argument(
        '--days-back',
        type=int,
        default=90,
        help='Number of days to look back for change frequency'
    )

    args = parser.parse_args()

    # Create suggester
    suggester = SkillSuggester(
        repo_path=args.repo,
        min_complexity=args.min_complexity,
        min_changes=args.min_changes,
        days_back=args.days_back
    )

    # Analyze and suggest
    suggester.analyze_and_suggest()

    # Save suggestions
    suggester.save_suggestions(args.output)

    # Print summary
    suggester.print_summary()

    print("\n✨ Suggestion generation complete!")


if __name__ == '__main__':
    main()
