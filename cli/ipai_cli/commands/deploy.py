# -*- coding: utf-8 -*-
"""Deployment Commands"""

import click
import subprocess
import time
from tabulate import tabulate


APP_IDS = {
    'ade-ocr': 'b1bb1b07-46a6-4bbb-85a2-e1e8c7f263b9',
    'expense-flow': '7f7b673b-35ed-4b20-a2ae-11e74c2109bf',
    'superset': '73af11cb-dab2-4cb1-9770-291c536531e6',
    'pulse-hub-web': '844b0bb2-0208-4694-bf86-12e750b7f790',
    'pulser-hub-mcp': '60a13dec-1b31-4daf-b4c3-bfe8ca0dbfc8',
}

SPEC_FILES = {
    'ade-ocr': 'infra/do/ade-ocr-service.yaml',
    'expense-flow': 'infra/do/expense-flow-api.yaml',
}


@click.command()
@click.argument('service', type=click.Choice(list(APP_IDS.keys())))
@click.option('--env', default='production', type=click.Choice(['production', 'staging']),
              help='Deployment environment')
@click.option('--force-rebuild', is_flag=True, help='Force rebuild from source')
@click.option('--wait/--no-wait', default=True, help='Wait for deployment to complete')
@click.pass_context
def deploy(ctx, service, env, force_rebuild, wait):
    """
    Deploy service to DigitalOcean App Platform

    \b
    Examples:
      ipai deploy ade-ocr --env production --force-rebuild
      ipai deploy expense-flow --no-wait
    """
    app_id = APP_IDS[service]
    spec_file = SPEC_FILES.get(service)

    click.echo(f"🚀 Deploying {service} to {env}...")

    # Update app spec if available
    if spec_file:
        click.echo(f"📝 Updating app spec from {spec_file}")
        cmd = ['doctl', 'apps', 'update', app_id, '--spec', spec_file]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            click.echo(f"❌ Failed to update app spec: {result.stderr}", err=True)
            sys.exit(1)

    # Create deployment
    click.echo("🔨 Creating deployment...")
    cmd = ['doctl', 'apps', 'create-deployment', app_id]

    if force_rebuild:
        cmd.append('--force-rebuild')

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        click.echo(f"❌ Deployment failed: {result.stderr}", err=True)
        sys.exit(1)

    # Extract deployment ID from output
    deployment_id = result.stdout.strip().split()[-1] if result.stdout else 'unknown'

    click.echo(f"✅ Deployment created: {deployment_id}")

    # Wait for deployment
    if wait:
        click.echo("⏳ Waiting for deployment to complete...")
        _wait_for_deployment(app_id, deployment_id)

    # Run health check
    click.echo("🏥 Running health check...")
    _health_check(service)


def _wait_for_deployment(app_id, deployment_id, timeout=600):
    """Wait for deployment to complete"""
    import sys

    start_time = time.time()

    with click.progressbar(length=timeout, label='Deploying') as bar:
        while True:
            # Check deployment status
            cmd = ['doctl', 'apps', 'get-deployment', app_id, deployment_id, '--format', 'Phase']
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                phase = result.stdout.strip()

                if phase == 'ACTIVE':
                    bar.update(timeout)
                    click.echo("\n✅ Deployment complete!")
                    return True
                elif phase in ['ERROR', 'FAILED', 'CANCELED']:
                    click.echo(f"\n❌ Deployment {phase.lower()}", err=True)
                    return False

            # Check timeout
            elapsed = time.time() - start_time
            if elapsed > timeout:
                click.echo("\n⏰ Deployment timeout", err=True)
                return False

            bar.update(min(int(elapsed), timeout))
            time.sleep(5)


def _health_check(service):
    """Run health check on deployed service"""
    health_urls = {
        'ade-ocr': 'https://ade-ocr-backend-d9dru.ondigitalocean.app/health',
        'pulse-hub-web': 'https://pulse-hub-web-an645.ondigitalocean.app',
    }

    url = health_urls.get(service)
    if not url:
        click.echo("⚠️ No health check URL configured")
        return

    import requests

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            click.echo(f"✅ Health check passed: {url}")
        else:
            click.echo(f"⚠️ Health check returned {response.status_code}", err=True)
    except Exception as e:
        click.echo(f"❌ Health check failed: {str(e)}", err=True)
