#!/usr/bin/env python3
"""
Deployer Agent - Module Deployment
Deploys Odoo modules to Docker/DigitalOcean
"""

import subprocess
import json
import time
from pathlib import Path
from typing import Dict
import logging
import os

logger = logging.getLogger(__name__)


class DeployerAgent:
    """Deploys Odoo modules to production environments"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.docker_compose_file = project_root / 'docker-compose.yml'
        self.odoo_addons_path = project_root / 'odoo' / 'addons'

    def deploy(self, generated_files: dict) -> dict:
        """
        Deploy module to Odoo

        Steps:
        1. Copy module to addons directory
        2. Restart Odoo container
        3. Install module via odoo-bin
        4. Verify installation

        Returns:
        {
            "success": bool,
            "url": "http://localhost:8069",
            "module_installed": bool,
            "errors": [...]
        }
        """
        logger.info("Starting deployment")

        module_path = Path(generated_files['module_path'])
        module_name = module_path.name

        result = {
            'success': False,
            'module_name': module_name,
            'errors': [],
        }

        try:
            # STEP 1: Copy module to addons directory
            logger.info(f"Copying module to {self.odoo_addons_path}")
            target_path = self.odoo_addons_path / module_name

            if target_path.exists():
                logger.warning(f"Module already exists at {target_path}, removing")
                subprocess.run(['rm', '-rf', str(target_path)], check=True)

            subprocess.run(
                ['cp', '-r', str(module_path), str(self.odoo_addons_path)],
                check=True
            )
            logger.info(f"Module copied to {target_path}")

            # STEP 2: Restart Odoo container
            logger.info("Restarting Odoo container")
            restart_result = self._restart_odoo_container()
            if not restart_result['success']:
                result['errors'].extend(restart_result['errors'])
                return result

            # Wait for Odoo to be ready
            logger.info("Waiting for Odoo to be ready (30 seconds)")
            time.sleep(30)

            # STEP 3: Install module
            logger.info(f"Installing module: {module_name}")
            install_result = self._install_module(module_name)
            if not install_result['success']:
                result['errors'].extend(install_result['errors'])
                return result

            # STEP 4: Verify installation
            logger.info("Verifying installation")
            verify_result = self._verify_installation(module_name)
            if not verify_result['success']:
                result['errors'].extend(verify_result['errors'])
                return result

            result['success'] = True
            result['url'] = 'http://localhost:8069'
            result['module_installed'] = True

            logger.info(f"Deployment successful: {module_name}")
            return result

        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            result['errors'].append({'message': str(e)})
            return result

    def _restart_odoo_container(self) -> dict:
        """Restart Odoo Docker container"""
        try:
            # Stop Odoo container
            subprocess.run(
                ['docker-compose', 'stop', 'odoo'],
                cwd=str(self.project_root),
                check=True,
                capture_output=True,
                timeout=60
            )

            # Start Odoo container
            subprocess.run(
                ['docker-compose', 'up', '-d', 'odoo'],
                cwd=str(self.project_root),
                check=True,
                capture_output=True,
                timeout=120
            )

            return {'success': True}

        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'errors': [{
                    'step': 'restart_container',
                    'message': f'Failed to restart Odoo: {e.stderr.decode()}',
                }],
            }
        except Exception as e:
            return {
                'success': False,
                'errors': [{
                    'step': 'restart_container',
                    'message': str(e),
                }],
            }

    def _install_module(self, module_name: str) -> dict:
        """Install module using odoo-bin"""
        try:
            # Get database name from environment or use default
            db_name = os.getenv('ODOO_DB_NAME', 'odoo')

            # Install module via docker exec
            result = subprocess.run(
                [
                    'docker-compose', 'exec', '-T', 'odoo',
                    'odoo-bin',
                    '-d', db_name,
                    '-i', module_name,
                    '--stop-after-init',
                    '--log-level=warn',
                ],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode != 0:
                return {
                    'success': False,
                    'errors': [{
                        'step': 'install_module',
                        'message': f'Module installation failed: {result.stderr}',
                    }],
                }

            # Restart Odoo after installation
            subprocess.run(
                ['docker-compose', 'restart', 'odoo'],
                cwd=str(self.project_root),
                check=True,
                timeout=60
            )

            # Wait for restart
            time.sleep(15)

            return {'success': True}

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'errors': [{
                    'step': 'install_module',
                    'message': 'Module installation timed out (>5 minutes)',
                }],
            }
        except Exception as e:
            return {
                'success': False,
                'errors': [{
                    'step': 'install_module',
                    'message': str(e),
                }],
            }

    def _verify_installation(self, module_name: str) -> dict:
        """Verify module was installed successfully"""
        try:
            db_name = os.getenv('ODOO_DB_NAME', 'odoo')

            # Check if module is installed via SQL
            result = subprocess.run(
                [
                    'docker-compose', 'exec', '-T', 'db',
                    'psql', '-U', 'odoo', '-d', db_name,
                    '-c', f"SELECT state FROM ir_module_module WHERE name='{module_name}'",
                ],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=30
            )

            if 'installed' in result.stdout:
                return {'success': True}
            else:
                return {
                    'success': False,
                    'errors': [{
                        'step': 'verify_installation',
                        'message': f'Module {module_name} not found in database',
                    }],
                }

        except Exception as e:
            return {
                'success': False,
                'errors': [{
                    'step': 'verify_installation',
                    'message': str(e),
                }],
            }

    def deploy_to_digitalocean(self, module_path: Path) -> dict:
        """
        Deploy to DigitalOcean App Platform

        Uses doctl CLI to update app spec and trigger deployment
        """
        try:
            # Get DigitalOcean app ID from environment
            app_id = os.getenv('DO_APP_ID')
            if not app_id:
                return {
                    'success': False,
                    'errors': [{
                        'message': 'DO_APP_ID environment variable not set',
                    }],
                }

            # Update app spec
            spec_file = self.project_root / 'infra' / 'do' / 'odoo-app-spec.yaml'
            result = subprocess.run(
                ['doctl', 'apps', 'update', app_id, '--spec', str(spec_file)],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                return {
                    'success': False,
                    'errors': [{
                        'message': f'Failed to update app spec: {result.stderr}',
                    }],
                }

            # Trigger deployment
            result = subprocess.run(
                ['doctl', 'apps', 'create-deployment', app_id, '--force-rebuild'],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                return {
                    'success': False,
                    'errors': [{
                        'message': f'Failed to trigger deployment: {result.stderr}',
                    }],
                }

            deployment_id = result.stdout.strip()

            return {
                'success': True,
                'deployment_id': deployment_id,
                'app_url': f'https://cloud.digitalocean.com/apps/{app_id}',
            }

        except Exception as e:
            return {
                'success': False,
                'errors': [{'message': str(e)}],
            }


if __name__ == '__main__':
    import sys

    # Load generated files info
    with open(sys.argv[1]) as f:
        generated_files = json.load(f)

    # Deploy
    deployer = DeployerAgent(Path.cwd())
    result = deployer.deploy(generated_files)

    # Output result
    print(json.dumps(result, indent=2))

    # Exit code
    exit(0 if result['success'] else 1)
