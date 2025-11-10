#!/usr/bin/env python3
"""
OCA Module Manager for Odoo 18.0
Automated installation with dependency resolution and branch detection

Usage:
    python3 scripts/admin/oca_module_manager.py insightpulse status
    python3 scripts/admin/oca_module_manager.py insightpulse install
"""

import logging
import requests
import sys
import json
from typing import List, Dict, Optional

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


class OCAModuleManager:
    """Manage OCA module installation with 18.0/19.0 readiness tracking"""

    # OCA repositories with 18.0 support and 19.0 expectations
    OCA_REPOS = {
        'account-financial-reporting': {
            'priority': 1,
            'modules': ['account_financial_report', 'mis_builder', 'report_xlsx'],
            'branch_18': True,
            'branch_19_expected': '2026-03',
            'description': 'Financial reporting and MIS Builder',
        },
        'dms': {
            'priority': 2,
            'modules': ['dms', 'dms_field', 'attachment_preview'],
            'branch_18': True,
            'branch_19_expected': '2026-03',
            'description': 'Document Management System',
        },
        'helpdesk': {
            'priority': 2,
            'modules': ['helpdesk_mgmt', 'helpdesk_mgmt_timesheet'],
            'branch_18': True,
            'branch_19_expected': '2026-03',
            'description': 'Helpdesk management',
        },
        'server-tools': {
            'priority': 1,
            'modules': ['base_tier_validation', 'base_automation'],
            'branch_18': True,
            'branch_19_expected': '2026-04',
            'description': 'Server tools and utilities',
        },
        'purchase-workflow': {
            'priority': 2,
            'modules': ['purchase_order_approval', 'purchase_request'],
            'branch_18': True,
            'branch_19_expected': '2026-04',
            'description': 'Purchase workflow enhancements',
        },
        'hr': {
            'priority': 2,
            'modules': ['hr_expense_advance_clearing', 'hr_holidays_leave_auto_approve'],
            'branch_18': True,
            'branch_19_expected': '2026-04',
            'description': 'HR and expense management',
        },
        'payroll': {
            'priority': 3,
            'modules': ['hr_payroll_account', 'hr_payroll_expense'],
            'branch_18': True,
            'branch_19_expected': '2026-04',
            'description': 'Payroll accounting integration',
        },
        'hr-attendance': {
            'priority': 3,
            'modules': ['hr_attendance_overtime', 'hr_attendance_report_theoretical_time'],
            'branch_18': True,
            'branch_19_expected': '2026-04',
            'description': 'Attendance and timesheet',
        },
        'manufacture': {
            'priority': 3,
            'modules': ['quality_control', 'quality_control_stock'],
            'branch_18': True,
            'branch_19_expected': '2026-05',
            'description': 'Quality control',
        },
        'calendar': {
            'priority': 3,
            'modules': ['resource_booking', 'resource_calendar'],
            'branch_18': True,
            'branch_19_expected': '2026-05',
            'description': 'Resource scheduling',
        },
    }

    # InsightPulse Finance SSC Stack for Odoo 18.0
    FINANCE_SSC_STACK = [
        # Core Accounting (CE)
        'account',
        'account_accountant',

        # OCA Accounting
        'account_financial_report',
        'mis_builder',
        'report_xlsx',

        # HR & Payroll
        'hr',
        'hr_expense',
        'hr_payroll_account',

        # Procurement
        'purchase',
        'purchase_order_approval',

        # Document Management
        'dms',
        'dms_field',

        # Approvals
        'base_tier_validation',

        # Custom Modules
        'insightpulse_travel_expense',
        'insightpulse_bir_compliance',
        'insightpulse_ppm',
    ]

    def __init__(self, db_name: str, odoo_version: str = '18.0'):
        self.db_name = db_name
        self.odoo_version = odoo_version

    def check_branch_availability(self, repo: str, branch: str = '18.0') -> Dict:
        """Check if OCA repo has specified branch"""
        url = f"https://api.github.com/repos/OCA/{repo}/branches/{branch}"

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                commit_data = response.json().get('commit', {})
                return {
                    'available': True,
                    'repo': repo,
                    'branch': branch,
                    'sha': commit_data.get('sha'),
                    'last_commit': commit_data.get('commit', {}).get('author', {}).get('date'),
                }
            else:
                return {
                    'available': False,
                    'repo': repo,
                    'branch': branch,
                    'status_code': response.status_code,
                }
        except Exception as e:
            _logger.error(f"Error checking branch {repo}/{branch}: {e}")
            return {'available': False, 'error': str(e)}

    def get_readiness_status(self) -> Dict:
        """Check readiness of OCA modules for current Odoo version"""
        status = {
            'repositories': [],
            'summary': {
                'total_repos': len(self.OCA_REPOS),
                'branch_18_available': 0,
                'branch_19_available': 0,
                'odoo_version': self.odoo_version,
            }
        }

        for repo_name, repo_info in self.OCA_REPOS.items():
            # Check 18.0 branch (current)
            branch_18_status = self.check_branch_availability(repo_name, '18.0')

            # Check 19.0 branch (future)
            branch_19_status = self.check_branch_availability(repo_name, '19.0')

            repo_status = {
                'repo': repo_name,
                'description': repo_info['description'],
                'branch_18_available': branch_18_status['available'],
                'branch_18_last_commit': branch_18_status.get('last_commit'),
                'branch_19_available': branch_19_status['available'],
                'branch_19_expected': repo_info['branch_19_expected'],
                'priority': repo_info['priority'],
                'modules': repo_info['modules'],
            }

            status['repositories'].append(repo_status)

            if branch_18_status['available']:
                status['summary']['branch_18_available'] += 1
            if branch_19_status['available']:
                status['summary']['branch_19_available'] += 1

        return status

    def install_module_stack(self, module_list: List[str], force: bool = False) -> Dict:
        """Install modules with dependency resolution"""
        try:
            import odoo
            from odoo import api, SUPERUSER_ID
        except ImportError:
            _logger.error("Cannot import Odoo - make sure PYTHONPATH includes Odoo directory")
            return {
                'installed': [],
                'failed': [{'module': 'N/A', 'reason': 'Odoo not in PYTHONPATH'}],
                'skipped': [],
            }

        registry = odoo.registry(self.db_name)

        results = {
            'installed': [],
            'failed': [],
            'skipped': [],
        }

        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            Module = env['ir.module.module']

            # Update module list
            _logger.info("Updating module list...")
            Module.update_list()

            for module_name in module_list:
                module = Module.search([('name', '=', module_name)])

                if not module:
                    results['failed'].append({
                        'module': module_name,
                        'reason': 'Module not found',
                    })
                    continue

                if module.state == 'installed':
                    results['skipped'].append({
                        'module': module_name,
                        'reason': 'Already installed',
                    })
                    continue

                if module.state == 'uninstallable' and not force:
                    results['failed'].append({
                        'module': module_name,
                        'reason': 'Uninstallable (Enterprise dependency?)',
                    })
                    continue

                try:
                    _logger.info(f"Installing {module_name}...")
                    module.button_immediate_install()
                    results['installed'].append(module_name)
                except Exception as e:
                    _logger.error(f"Failed to install {module_name}: {e}")
                    results['failed'].append({
                        'module': module_name,
                        'reason': str(e),
                    })

            cr.commit()

        return results


def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/admin/oca_module_manager.py <db_name> <command>")
        print("Commands: status, install")
        sys.exit(1)

    db_name = sys.argv[1]
    command = sys.argv[2] if len(sys.argv) > 2 else 'status'

    manager = OCAModuleManager(db_name, odoo_version='18.0')

    if command == 'status':
        # Check OCA branch status
        status = manager.get_readiness_status()
        print(json.dumps(status, indent=2))

    elif command == 'install':
        # Install Finance SSC stack
        results = manager.install_module_stack(
            OCAModuleManager.FINANCE_SSC_STACK
        )
        print(json.dumps(results, indent=2))

    else:
        print(f"Unknown command: {command}")
        print("Available commands: status, install")
        sys.exit(1)


if __name__ == '__main__':
    main()
