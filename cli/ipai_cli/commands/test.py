# -*- coding: utf-8 -*-
"""Testing Commands"""

import click
import subprocess


@click.command()
@click.argument('test_type', type=click.Choice(['visual', 'unit', 'integration', 'e2e']))
@click.option('--routes', default='/expenses,/tasks', help='Routes to test (comma-separated)')
@click.option('--threshold', default=0.97, type=float, help='SSIM threshold for visual tests')
@click.option('--base-url', default='http://localhost:4173', help='Base URL for testing')
@click.option('--output', default='./screenshots', help='Output directory for screenshots')
@click.pass_context
def test(ctx, test_type, routes, threshold, base_url, output):
    """
    Run automated tests

    \b
    Examples:
      ipai test visual --routes /expenses,/tasks --threshold 0.97
      ipai test unit
      ipai test e2e --base-url https://atomic-crm.vercel.app
    """
    if test_type == 'visual':
        _run_visual_tests(routes, threshold, base_url, output)
    elif test_type == 'unit':
        _run_unit_tests()
    elif test_type == 'integration':
        _run_integration_tests()
    elif test_type == 'e2e':
        _run_e2e_tests(base_url)


def _run_visual_tests(routes, threshold, base_url, output):
    """Run visual parity tests"""
    click.echo(f"📸 Running visual parity tests...")
    click.echo(f"   Routes: {routes}")
    click.echo(f"   Threshold: {threshold}")
    click.echo(f"   Base URL: {base_url}")

    # Capture screenshots
    click.echo("\n1️⃣ Capturing screenshots...")
    cmd = [
        'node', 'scripts/snap.js',
        f'--routes={routes}',
        f'--base-url={base_url}',
        f'--output={output}'
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        click.echo(f"❌ Screenshot capture failed: {result.stderr}", err=True)
        return

    click.echo(result.stdout)

    # Compare screenshots
    click.echo("\n2️⃣ Comparing screenshots...")
    cmd = [
        'node', 'scripts/ssim.js',
        f'--routes={routes}',
        f'--odoo-version=19.0',
        f'--screenshots={output}'
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        click.echo(f"❌ Visual tests failed: {result.stderr}", err=True)
    else:
        click.echo("✅ Visual tests passed")
        click.echo(result.stdout)


def _run_unit_tests():
    """Run unit tests"""
    click.echo("🧪 Running unit tests...")

    cmd = ['pytest', 'tests/unit', '-v', '--cov=packages']
    result = subprocess.run(cmd, capture_output=True, text=True)

    click.echo(result.stdout)

    if result.returncode != 0:
        click.echo("❌ Unit tests failed", err=True)
    else:
        click.echo("✅ Unit tests passed")


def _run_integration_tests():
    """Run integration tests"""
    click.echo("🔗 Running integration tests...")

    cmd = ['pytest', 'tests/integration', '-v']
    result = subprocess.run(cmd, capture_output=True, text=True)

    click.echo(result.stdout)

    if result.returncode != 0:
        click.echo("❌ Integration tests failed", err=True)
    else:
        click.echo("✅ Integration tests passed")


def _run_e2e_tests(base_url):
    """Run E2E tests with Playwright"""
    click.echo(f"🌐 Running E2E tests against {base_url}...")

    cmd = ['npx', 'playwright', 'test', '--base-url', base_url]
    result = subprocess.run(cmd, capture_output=True, text=True)

    click.echo(result.stdout)

    if result.returncode != 0:
        click.echo("❌ E2E tests failed", err=True)
    else:
        click.echo("✅ E2E tests passed")
