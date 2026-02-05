#!/usr/bin/env python3
"""
Orchestrator Agent - Master Controller
Coordinates all specialized agents for complete module lifecycle
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """Master agent coordinating specialized agents"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.agents = {}
        self.context = {}
        self.results = {
            'workflow': None,
            'started_at': None,
            'completed_at': None,
            'steps': [],
            'success': False,
        }

    def initialize_agents(self):
        """Initialize all specialized agents"""
        from planner import PlannerAgent
        from generator import GeneratorAgent
        from validator import ValidatorAgent
        from deployer import DeployerAgent
        from monitor import MonitorAgent

        self.agents = {
            'planner': PlannerAgent(self.project_root),
            'generator': GeneratorAgent(self.project_root),
            'validator': ValidatorAgent(self.project_root),
            'deployer': DeployerAgent(self.project_root),
            'monitor': MonitorAgent(self.project_root),
        }

        logger.info("All agents initialized")

    def execute_workflow(self, workflow: str, params: dict) -> dict:
        """
        Execute complete workflow with specialized agents

        Workflows:
        - generate_module: Full module lifecycle (plan → generate → validate → deploy → monitor)
        - validate_only: Run validation on existing module
        - deploy_only: Deploy existing module
        - monitor_only: Run health checks

        Returns:
        {
            "success": bool,
            "workflow": str,
            "steps": [...],
            "errors": [...]
        }
        """
        logger.info(f"Starting workflow: {workflow}")

        self.results['workflow'] = workflow
        self.results['started_at'] = datetime.now().isoformat()

        try:
            if workflow == 'generate_module':
                return self._workflow_generate_module(params)
            elif workflow == 'validate_only':
                return self._workflow_validate_only(params)
            elif workflow == 'deploy_only':
                return self._workflow_deploy_only(params)
            elif workflow == 'monitor_only':
                return self._workflow_monitor_only(params)
            else:
                return {
                    'success': False,
                    'errors': [{'message': f'Unknown workflow: {workflow}'}],
                }

        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            return {
                'success': False,
                'errors': [{'message': str(e)}],
            }

        finally:
            self.results['completed_at'] = datetime.now().isoformat()

    def _workflow_generate_module(self, params: dict) -> dict:
        """
        Complete module generation workflow

        Steps:
        1. Planner: Create architecture plan
        2. Generator: Generate module code
        3. Validator: Validate code quality
        4. Generator: Fix validation issues (if needed)
        5. Deployer: Deploy to Docker/DigitalOcean
        6. Monitor: Run health checks
        """
        logger.info("Executing generate_module workflow")

        # STEP 1: Planning
        logger.info("Step 1: Planning module architecture")
        plan = self.agents['planner'].create_plan(params)

        if not plan.get('valid'):
            self.results['steps'].append({
                'agent': 'planner',
                'status': 'failed',
                'errors': plan.get('errors', []),
            })
            self.results['success'] = False
            return self.results

        self.results['steps'].append({
            'agent': 'planner',
            'status': 'success',
            'output': plan,
        })
        self.context['plan'] = plan

        # STEP 2: Generation
        logger.info("Step 2: Generating module code")
        generated_files = self.agents['generator'].generate_module(plan)

        if not generated_files.get('success'):
            self.results['steps'].append({
                'agent': 'generator',
                'status': 'failed',
                'errors': generated_files.get('errors', []),
            })
            self.results['success'] = False
            return self.results

        self.results['steps'].append({
            'agent': 'generator',
            'status': 'success',
            'output': generated_files,
        })
        self.context['generated_files'] = generated_files

        # STEP 3: Validation
        logger.info("Step 3: Validating generated code")
        validation_result = self.agents['validator'].validate_module(generated_files)

        if not validation_result['passed']:
            self.results['steps'].append({
                'agent': 'validator',
                'status': 'failed',
                'errors': validation_result['errors'],
            })

            # Try to auto-fix validation issues
            logger.info("Attempting auto-fix for validation issues")
            fixed_files = self.agents['generator'].fix_issues(
                generated_files,
                validation_result['errors']
            )

            # Re-validate after fixes
            validation_result = self.agents['validator'].validate_module(fixed_files)

            if not validation_result['passed']:
                logger.error("Validation still failed after auto-fix")
                self.results['success'] = False
                return self.results

            # Update generated files with fixed version
            generated_files = fixed_files
            self.context['generated_files'] = generated_files

        self.results['steps'].append({
            'agent': 'validator',
            'status': 'success',
            'output': validation_result,
        })

        # STEP 4: Deployment
        logger.info("Step 4: Deploying module")
        deploy_target = params.get('deploy_target', 'docker')  # docker or digitalocean

        if deploy_target == 'docker':
            deploy_result = self.agents['deployer'].deploy(generated_files)
        else:
            deploy_result = self.agents['deployer'].deploy_to_digitalocean(
                Path(generated_files['module_path'])
            )

        if not deploy_result['success']:
            self.results['steps'].append({
                'agent': 'deployer',
                'status': 'failed',
                'errors': deploy_result['errors'],
            })
            self.results['success'] = False
            return self.results

        self.results['steps'].append({
            'agent': 'deployer',
            'status': 'success',
            'output': deploy_result,
        })
        self.context['deployment'] = deploy_result

        # STEP 5: Monitoring
        logger.info("Step 5: Running health checks")
        base_url = deploy_result.get('url', 'http://localhost:8069')
        health_result = self.agents['monitor'].health_check(base_url)

        if not health_result['healthy']:
            self.results['steps'].append({
                'agent': 'monitor',
                'status': 'warning',
                'errors': health_result['errors'],
            })
            # Don't fail workflow for health check issues
        else:
            self.results['steps'].append({
                'agent': 'monitor',
                'status': 'success',
                'output': health_result,
            })

        # Smoke test
        module_name = generated_files['module_name']
        smoke_result = self.agents['monitor'].smoke_test(module_name, base_url)

        if not smoke_result['passed']:
            self.results['steps'].append({
                'agent': 'monitor',
                'status': 'warning',
                'test': 'smoke_test',
                'errors': smoke_result['errors'],
            })
        else:
            self.results['steps'].append({
                'agent': 'monitor',
                'status': 'success',
                'test': 'smoke_test',
                'output': smoke_result,
            })

        self.results['success'] = True
        logger.info("Workflow completed successfully")
        return self.results

    def _workflow_validate_only(self, params: dict) -> dict:
        """Run validation only on existing module"""
        logger.info("Executing validate_only workflow")

        module_path = params.get('module_path')
        if not module_path:
            return {
                'success': False,
                'errors': [{'message': 'module_path required'}],
            }

        generated_files = {'module_path': module_path}
        validation_result = self.agents['validator'].validate_module(generated_files)

        self.results['steps'].append({
            'agent': 'validator',
            'status': 'success' if validation_result['passed'] else 'failed',
            'output': validation_result,
        })

        self.results['success'] = validation_result['passed']
        return self.results

    def _workflow_deploy_only(self, params: dict) -> dict:
        """Deploy existing module"""
        logger.info("Executing deploy_only workflow")

        module_path = params.get('module_path')
        deploy_target = params.get('deploy_target', 'docker')

        if not module_path:
            return {
                'success': False,
                'errors': [{'message': 'module_path required'}],
            }

        generated_files = {'module_path': module_path}

        if deploy_target == 'docker':
            deploy_result = self.agents['deployer'].deploy(generated_files)
        else:
            deploy_result = self.agents['deployer'].deploy_to_digitalocean(
                Path(module_path)
            )

        self.results['steps'].append({
            'agent': 'deployer',
            'status': 'success' if deploy_result['success'] else 'failed',
            'output': deploy_result,
        })

        self.results['success'] = deploy_result['success']
        return self.results

    def _workflow_monitor_only(self, params: dict) -> dict:
        """Run health checks and monitoring"""
        logger.info("Executing monitor_only workflow")

        base_url = params.get('base_url', 'http://localhost:8069')
        module_name = params.get('module_name')

        # Health check
        health_result = self.agents['monitor'].health_check(base_url)

        self.results['steps'].append({
            'agent': 'monitor',
            'status': 'success' if health_result['healthy'] else 'warning',
            'test': 'health_check',
            'output': health_result,
        })

        # Smoke test (if module_name provided)
        if module_name:
            smoke_result = self.agents['monitor'].smoke_test(module_name, base_url)

            self.results['steps'].append({
                'agent': 'monitor',
                'status': 'success' if smoke_result['passed'] else 'warning',
                'test': 'smoke_test',
                'output': smoke_result,
            })

            self.results['success'] = health_result['healthy'] and smoke_result['passed']
        else:
            self.results['success'] = health_result['healthy']

        return self.results


if __name__ == '__main__':
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='Orchestrator Agent')
    parser.add_argument('--workflow', required=True, help='Workflow to execute')
    parser.add_argument('--params', required=True, help='JSON file with parameters')

    args = parser.parse_args()

    # Load parameters
    with open(args.params) as f:
        params = json.load(f)

    # Initialize orchestrator
    orchestrator = OrchestratorAgent(Path.cwd())
    orchestrator.initialize_agents()

    # Execute workflow
    result = orchestrator.execute_workflow(args.workflow, params)

    # Output result
    print(json.dumps(result, indent=2))

    # Exit code
    exit(0 if result['success'] else 1)
