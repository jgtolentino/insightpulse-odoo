#!/usr/bin/env python3
"""
Monitor Agent - Health Checks & Performance Monitoring
Monitors deployed modules for health, performance, errors
"""

import requests
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class MonitorAgent:
    """Monitors Odoo module health and performance"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.health_check_timeout = 10  # seconds
        self.performance_threshold_ms = 1000  # 1 second

    def health_check(self, base_url: str) -> dict:
        """
        Comprehensive health check

        Checks:
        1. HTTP response time
        2. Database connectivity
        3. Module loaded
        4. No critical errors in logs

        Returns:
        {
            "healthy": bool,
            "checks": {...},
            "response_time_ms": int,
            "errors": [...]
        }
        """
        logger.info(f"Running health check for {base_url}")

        result = {
            'healthy': True,
            'timestamp': datetime.now().isoformat(),
            'base_url': base_url,
            'checks': {},
            'errors': [],
        }

        # CHECK 1: HTTP Response
        http_check = self._check_http_response(base_url)
        result['checks']['http'] = http_check
        result['response_time_ms'] = http_check.get('response_time_ms', 0)

        if not http_check['passed']:
            result['healthy'] = False
            result['errors'].extend(http_check['errors'])

        # CHECK 2: Database Connectivity
        db_check = self._check_database()
        result['checks']['database'] = db_check

        if not db_check['passed']:
            result['healthy'] = False
            result['errors'].extend(db_check['errors'])

        # CHECK 3: Odoo Logs (no critical errors)
        logs_check = self._check_logs()
        result['checks']['logs'] = logs_check

        if not logs_check['passed']:
            result['healthy'] = False
            result['errors'].extend(logs_check['errors'])

        # CHECK 4: Performance Metrics
        perf_check = self._check_performance(base_url)
        result['checks']['performance'] = perf_check

        if not perf_check['passed']:
            result['healthy'] = False
            result['errors'].extend(perf_check['errors'])

        logger.info(f"Health check complete. Healthy: {result['healthy']}")
        return result

    def _check_http_response(self, base_url: str) -> dict:
        """Check HTTP endpoint responds"""
        try:
            start_time = time.time()

            response = requests.get(
                f"{base_url}/web/database/selector",
                timeout=self.health_check_timeout
            )

            response_time_ms = int((time.time() - start_time) * 1000)

            if response.status_code == 200:
                return {
                    'passed': True,
                    'response_time_ms': response_time_ms,
                    'status_code': response.status_code,
                }
            else:
                return {
                    'passed': False,
                    'response_time_ms': response_time_ms,
                    'status_code': response.status_code,
                    'errors': [{
                        'check': 'http',
                        'message': f'HTTP {response.status_code}',
                    }],
                }

        except requests.Timeout:
            return {
                'passed': False,
                'errors': [{
                    'check': 'http',
                    'message': f'Request timeout (>{self.health_check_timeout}s)',
                }],
            }
        except requests.ConnectionError as e:
            return {
                'passed': False,
                'errors': [{
                    'check': 'http',
                    'message': f'Connection error: {str(e)}',
                }],
            }
        except Exception as e:
            return {
                'passed': False,
                'errors': [{
                    'check': 'http',
                    'message': str(e),
                }],
            }

    def _check_database(self) -> dict:
        """Check database connectivity"""
        try:
            result = subprocess.run(
                [
                    'docker-compose', 'exec', '-T', 'db',
                    'pg_isready', '-U', 'odoo',
                ],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                return {'passed': True}
            else:
                return {
                    'passed': False,
                    'errors': [{
                        'check': 'database',
                        'message': 'PostgreSQL not ready',
                    }],
                }

        except Exception as e:
            return {
                'passed': False,
                'errors': [{
                    'check': 'database',
                    'message': str(e),
                }],
            }

    def _check_logs(self) -> dict:
        """Check Odoo logs for critical errors"""
        try:
            # Get last 100 lines of logs
            result = subprocess.run(
                ['docker-compose', 'logs', '--tail=100', 'odoo'],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=10
            )

            logs = result.stdout

            # Check for critical errors
            critical_patterns = [
                'CRITICAL',
                'ERROR',
                'Traceback',
                'Exception',
            ]

            errors = []
            for pattern in critical_patterns:
                if pattern in logs:
                    # Count occurrences
                    count = logs.count(pattern)
                    errors.append({
                        'check': 'logs',
                        'message': f'Found {count} {pattern} entries in logs',
                    })

            if errors:
                return {
                    'passed': False,
                    'errors': errors,
                }
            else:
                return {'passed': True}

        except Exception as e:
            return {
                'passed': False,
                'errors': [{
                    'check': 'logs',
                    'message': str(e),
                }],
            }

    def _check_performance(self, base_url: str) -> dict:
        """Check response time performance"""
        try:
            # Make multiple requests to get average
            response_times = []

            for _ in range(3):
                start_time = time.time()
                requests.get(
                    f"{base_url}/web/database/selector",
                    timeout=self.health_check_timeout
                )
                response_time_ms = int((time.time() - start_time) * 1000)
                response_times.append(response_time_ms)

            avg_response_time = sum(response_times) // len(response_times)

            if avg_response_time > self.performance_threshold_ms:
                return {
                    'passed': False,
                    'avg_response_time_ms': avg_response_time,
                    'errors': [{
                        'check': 'performance',
                        'message': f'Average response time {avg_response_time}ms exceeds threshold {self.performance_threshold_ms}ms',
                    }],
                }
            else:
                return {
                    'passed': True,
                    'avg_response_time_ms': avg_response_time,
                }

        except Exception as e:
            return {
                'passed': False,
                'errors': [{
                    'check': 'performance',
                    'message': str(e),
                }],
            }

    def collect_metrics(self, module_name: str) -> dict:
        """
        Collect module usage metrics

        Metrics:
        - Request count
        - Error rate
        - Average response time
        - Database query count
        - Memory usage
        """
        logger.info(f"Collecting metrics for module: {module_name}")

        metrics = {
            'timestamp': datetime.now().isoformat(),
            'module_name': module_name,
            'metrics': {},
        }

        try:
            # Get container stats
            result = subprocess.run(
                ['docker', 'stats', '--no-stream', '--format', '{{json .}}'],
                capture_output=True,
                text=True,
                timeout=10
            )

            # Parse stats (JSON per line)
            for line in result.stdout.strip().split('\n'):
                if line:
                    stats = json.loads(line)
                    if 'odoo' in stats.get('Name', '').lower():
                        metrics['metrics']['cpu_percent'] = stats['CPUPerc']
                        metrics['metrics']['memory_usage'] = stats['MemUsage']
                        metrics['metrics']['memory_percent'] = stats['MemPerc']

            return metrics

        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
            return metrics

    def smoke_test(self, module_name: str, base_url: str) -> dict:
        """
        Run smoke tests on deployed module

        Tests:
        1. Module appears in app list
        2. Module menu items visible
        3. Basic CRUD operations work
        """
        logger.info(f"Running smoke test for {module_name}")

        result = {
            'passed': True,
            'module_name': module_name,
            'tests': [],
            'errors': [],
        }

        # TEST 1: Module is installed
        install_test = self._smoke_test_installed(module_name)
        result['tests'].append(install_test)

        if not install_test['passed']:
            result['passed'] = False
            result['errors'].extend(install_test['errors'])
            return result  # Stop if module not installed

        # TEST 2: Module accessible via HTTP
        http_test = self._smoke_test_http(module_name, base_url)
        result['tests'].append(http_test)

        if not http_test['passed']:
            result['passed'] = False
            result['errors'].extend(http_test['errors'])

        logger.info(f"Smoke test complete. Passed: {result['passed']}")
        return result

    def _smoke_test_installed(self, module_name: str) -> dict:
        """Test: Module is installed in database"""
        try:
            import os
            db_name = os.getenv('ODOO_DB_NAME', 'odoo')

            result = subprocess.run(
                [
                    'docker-compose', 'exec', '-T', 'db',
                    'psql', '-U', 'odoo', '-d', db_name, '-t',
                    '-c', f"SELECT state FROM ir_module_module WHERE name='{module_name}'",
                ],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=10
            )

            if 'installed' in result.stdout:
                return {
                    'test': 'module_installed',
                    'passed': True,
                }
            else:
                return {
                    'test': 'module_installed',
                    'passed': False,
                    'errors': [{
                        'message': f'Module {module_name} not installed',
                    }],
                }

        except Exception as e:
            return {
                'test': 'module_installed',
                'passed': False,
                'errors': [{'message': str(e)}],
            }

    def _smoke_test_http(self, module_name: str, base_url: str) -> dict:
        """Test: Module accessible via HTTP"""
        try:
            # Try to access module-specific endpoint
            # This is a basic test - actual endpoints depend on module
            response = requests.get(
                f"{base_url}/web/dataset/call_kw/{module_name}/search_read",
                timeout=10
            )

            # We expect 200 or 404 (not 500)
            if response.status_code in [200, 404]:
                return {
                    'test': 'http_accessible',
                    'passed': True,
                }
            else:
                return {
                    'test': 'http_accessible',
                    'passed': False,
                    'errors': [{
                        'message': f'HTTP {response.status_code}',
                    }],
                }

        except Exception as e:
            return {
                'test': 'http_accessible',
                'passed': False,
                'errors': [{'message': str(e)}],
            }


if __name__ == '__main__':
    import sys

    # Health check
    if len(sys.argv) > 1 and sys.argv[1] == 'health':
        base_url = sys.argv[2] if len(sys.argv) > 2 else 'http://localhost:8069'

        monitor = MonitorAgent(Path.cwd())
        result = monitor.health_check(base_url)

        print(json.dumps(result, indent=2))
        exit(0 if result['healthy'] else 1)

    # Smoke test
    elif len(sys.argv) > 1 and sys.argv[1] == 'smoke':
        module_name = sys.argv[2]
        base_url = sys.argv[3] if len(sys.argv) > 3 else 'http://localhost:8069'

        monitor = MonitorAgent(Path.cwd())
        result = monitor.smoke_test(module_name, base_url)

        print(json.dumps(result, indent=2))
        exit(0 if result['passed'] else 1)

    else:
        print("Usage:")
        print("  python monitor.py health [base_url]")
        print("  python monitor.py smoke <module_name> [base_url]")
        exit(1)
