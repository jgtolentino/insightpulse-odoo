#!/usr/bin/env python3
"""
Validator Agent - Code Quality & Security
Validates generated code for linting, tests, security issues
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class ValidatorAgent:
    """Validates Odoo module code quality and security"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.min_coverage = 80  # Minimum test coverage %

    def validate_module(self, generated_files: dict) -> dict:
        """
        Run all validation checks

        Returns:
        {
            "passed": bool,
            "linting": {...},
            "tests": {...},
            "security": {...},
            "errors": [...]
        }
        """
        logger.info("Starting validation checks")

        module_path = Path(generated_files['module_path'])

        results = {
            'passed': True,
            'linting': {},
            'tests': {},
            'security': {},
            'errors': [],
        }

        # VALIDATION 1: Linting (Black, Flake8, Pylint)
        logger.info("Running linting checks")
        linting_result = self._validate_linting(module_path)
        results['linting'] = linting_result
        if not linting_result['passed']:
            results['passed'] = False
            results['errors'].extend(linting_result['errors'])

        # VALIDATION 2: Tests (pytest with coverage)
        logger.info("Running tests")
        test_result = self._validate_tests(module_path)
        results['tests'] = test_result
        if not test_result['passed']:
            results['passed'] = False
            results['errors'].extend(test_result['errors'])

        # VALIDATION 3: Security (Bandit)
        logger.info("Running security checks")
        security_result = self._validate_security(module_path)
        results['security'] = security_result
        if not security_result['passed']:
            results['passed'] = False
            results['errors'].extend(security_result['errors'])

        # VALIDATION 4: OCA Compliance
        logger.info("Checking OCA compliance")
        oca_result = self._validate_oca_compliance(module_path)
        results['oca_compliance'] = oca_result
        if not oca_result['passed']:
            results['passed'] = False
            results['errors'].extend(oca_result['errors'])

        logger.info(f"Validation complete. Passed: {results['passed']}")
        return results

    def _validate_linting(self, module_path: Path) -> dict:
        """Run Black, Flake8, Pylint"""
        errors = []

        # Black formatting check
        try:
            result = subprocess.run(
                ['black', '--check', '--line-length=88', str(module_path)],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode != 0:
                errors.append({
                    'tool': 'black',
                    'message': 'Code formatting issues found',
                    'details': result.stderr,
                })
        except Exception as e:
            errors.append({'tool': 'black', 'message': str(e)})

        # Flake8 style check
        try:
            result = subprocess.run(
                ['flake8', '--max-line-length=88', '--extend-ignore=E203,W503',
                 str(module_path)],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode != 0:
                errors.append({
                    'tool': 'flake8',
                    'message': 'Style violations found',
                    'details': result.stdout,
                })
        except Exception as e:
            errors.append({'tool': 'flake8', 'message': str(e)})

        # Pylint code quality
        try:
            result = subprocess.run(
                ['pylint', '--rcfile=.pylintrc', str(module_path)],
                capture_output=True,
                text=True,
                timeout=120
            )
            # Pylint returns non-zero for warnings, but we only fail on errors
            if result.returncode >= 4:  # Error threshold
                errors.append({
                    'tool': 'pylint',
                    'message': 'Code quality issues found',
                    'details': result.stdout,
                })
        except Exception as e:
            errors.append({'tool': 'pylint', 'message': str(e)})

        return {
            'passed': len(errors) == 0,
            'errors': errors,
        }

    def _validate_tests(self, module_path: Path) -> dict:
        """Run pytest with coverage"""
        errors = []
        coverage_pct = 0

        try:
            # Run pytest with coverage
            result = subprocess.run(
                [
                    'pytest',
                    str(module_path / 'tests'),
                    '--cov=' + str(module_path),
                    '--cov-report=json',
                    '--cov-report=term',
                    '-v'
                ],
                capture_output=True,
                text=True,
                timeout=300
            )

            # Parse coverage report
            coverage_json = module_path / 'coverage.json'
            if coverage_json.exists():
                with open(coverage_json) as f:
                    cov_data = json.load(f)
                    coverage_pct = cov_data.get('totals', {}).get('percent_covered', 0)

            # Check if tests passed
            if result.returncode != 0:
                errors.append({
                    'tool': 'pytest',
                    'message': 'Tests failed',
                    'details': result.stdout,
                })

            # Check coverage threshold
            if coverage_pct < self.min_coverage:
                errors.append({
                    'tool': 'pytest',
                    'message': f'Coverage {coverage_pct}% below minimum {self.min_coverage}%',
                    'details': f'Increase test coverage to {self.min_coverage}%',
                })

        except Exception as e:
            errors.append({'tool': 'pytest', 'message': str(e)})

        return {
            'passed': len(errors) == 0,
            'coverage': coverage_pct,
            'errors': errors,
        }

    def _validate_security(self, module_path: Path) -> dict:
        """Run Bandit security scanner"""
        errors = []

        try:
            result = subprocess.run(
                [
                    'bandit',
                    '-r',
                    str(module_path),
                    '-f', 'json',
                    '-ll',  # Only report medium/high severity
                ],
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode != 0:
                # Parse Bandit JSON output
                try:
                    bandit_data = json.loads(result.stdout)
                    for issue in bandit_data.get('results', []):
                        errors.append({
                            'tool': 'bandit',
                            'message': issue['issue_text'],
                            'file': issue['filename'],
                            'line': issue['line_number'],
                            'severity': issue['issue_severity'],
                        })
                except:
                    errors.append({
                        'tool': 'bandit',
                        'message': 'Security issues found',
                        'details': result.stdout,
                    })

        except Exception as e:
            errors.append({'tool': 'bandit', 'message': str(e)})

        return {
            'passed': len(errors) == 0,
            'errors': errors,
        }

    def _validate_oca_compliance(self, module_path: Path) -> dict:
        """Check OCA module structure compliance"""
        errors = []

        # Required files
        required_files = [
            '__init__.py',
            '__manifest__.py',
            'README.rst',
            'models/__init__.py',
            'security/ir.model.access.csv',
        ]

        for req_file in required_files:
            file_path = module_path / req_file
            if not file_path.exists():
                errors.append({
                    'tool': 'oca_compliance',
                    'message': f'Missing required file: {req_file}',
                })

        # Check manifest structure
        manifest_path = module_path / '__manifest__.py'
        if manifest_path.exists():
            with open(manifest_path) as f:
                manifest_code = f.read()

                # Required manifest keys
                required_keys = ['name', 'version', 'license', 'author', 'depends']
                for key in required_keys:
                    if f"'{key}'" not in manifest_code and f'"{key}"' not in manifest_code:
                        errors.append({
                            'tool': 'oca_compliance',
                            'message': f'Missing required manifest key: {key}',
                        })

                # Check license
                if 'LGPL-3' not in manifest_code and 'AGPL-3' not in manifest_code:
                    errors.append({
                        'tool': 'oca_compliance',
                        'message': 'Module must use LGPL-3 or AGPL-3 license',
                    })

        return {
            'passed': len(errors) == 0,
            'errors': errors,
        }


if __name__ == '__main__':
    import sys

    # Load generated files info
    with open(sys.argv[1]) as f:
        generated_files = json.load(f)

    # Validate
    validator = ValidatorAgent(Path.cwd())
    result = validator.validate_module(generated_files)

    # Output result
    print(json.dumps(result, indent=2))

    # Exit code
    exit(0 if result['passed'] else 1)
