# -*- coding: utf-8 -*-
"""Task Queue Commands"""

import click
import requests
from tabulate import tabulate


@click.command()
@click.argument('action', type=click.Choice(['sync', 'list', 'cancel', 'retry']))
@click.option('--status', type=click.Choice(['pending', 'processing', 'completed', 'failed', 'cancelled']),
              help='Filter by status')
@click.option('--task-id', type=int, help='Specific task ID')
@click.option('--limit', default=50, type=int, help='Maximum number of tasks to show')
@click.pass_context
def task(ctx, action, status, task_id, limit):
    """
    Manage Supabase task queue

    \b
    Examples:
      ipai task list --status pending
      ipai task sync --status processing
      ipai task cancel --task-id 123
      ipai task retry --task-id 456
    """
    supabase_url = ctx.obj['SUPABASE_URL']
    service_key = ctx.obj['SUPABASE_SERVICE_ROLE_KEY']

    if not supabase_url or not service_key:
        click.echo("❌ Supabase credentials not configured", err=True)
        sys.exit(1)

    if action == 'list':
        _list_tasks(supabase_url, service_key, status, limit)
    elif action == 'sync':
        _sync_tasks(supabase_url, service_key, status)
    elif action == 'cancel':
        if not task_id:
            click.echo("❌ --task-id required for cancel", err=True)
            sys.exit(1)
        _cancel_task(supabase_url, service_key, task_id)
    elif action == 'retry':
        if not task_id:
            click.echo("❌ --task-id required for retry", err=True)
            sys.exit(1)
        _retry_task(supabase_url, service_key, task_id)


def _list_tasks(supabase_url, service_key, status, limit):
    """List tasks from queue"""
    headers = {
        'apikey': service_key,
        'Authorization': f'Bearer {service_key}',
        'Content-Type': 'application/json',
    }

    # Build query
    url = f'{supabase_url}/rest/v1/task_queue'
    params = {'limit': limit, 'order': 'created_at.desc'}

    if status:
        params['status'] = f'eq.{status}'

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        click.echo(f"❌ Failed to fetch tasks: {response.text}", err=True)
        return

    tasks = response.json()

    if not tasks:
        click.echo("📭 No tasks found")
        return

    # Format as table
    table_data = []
    for task in tasks:
        table_data.append([
            task['id'],
            task['kind'],
            task['status'],
            task.get('pr_number', '-'),
            task['created_at'][:19],
        ])

    headers_list = ['ID', 'Kind', 'Status', 'PR #', 'Created']
    click.echo(tabulate(table_data, headers=headers_list, tablefmt='grid'))
    click.echo(f"\n📊 Total: {len(tasks)} tasks")


def _sync_tasks(supabase_url, service_key, status):
    """Sync and process tasks"""
    click.echo(f"🔄 Syncing tasks{f' with status {status}' if status else ''}...")

    headers = {
        'apikey': service_key,
        'Authorization': f'Bearer {service_key}',
        'Content-Type': 'application/json',
    }

    # Call route_and_enqueue RPC
    url = f'{supabase_url}/rest/v1/rpc/route_and_enqueue'
    payload = {'p_kind': 'TASK_SYNC', 'p_payload': {'status': status}}

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        click.echo(f"❌ Sync failed: {response.text}", err=True)
        return

    result = response.json()
    click.echo(f"✅ Sync completed: {result}")


def _cancel_task(supabase_url, service_key, task_id):
    """Cancel a task"""
    click.echo(f"🛑 Cancelling task {task_id}...")

    headers = {
        'apikey': service_key,
        'Authorization': f'Bearer {service_key}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation',
    }

    url = f'{supabase_url}/rest/v1/task_queue?id=eq.{task_id}'
    payload = {'status': 'cancelled'}

    response = requests.patch(url, headers=headers, json=payload)

    if response.status_code != 200:
        click.echo(f"❌ Cancel failed: {response.text}", err=True)
        return

    click.echo("✅ Task cancelled")


def _retry_task(supabase_url, service_key, task_id):
    """Retry a failed task"""
    click.echo(f"🔄 Retrying task {task_id}...")

    headers = {
        'apikey': service_key,
        'Authorization': f'Bearer {service_key}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation',
    }

    url = f'{supabase_url}/rest/v1/task_queue?id=eq.{task_id}'
    payload = {'status': 'pending', 'retry_count': 0}

    response = requests.patch(url, headers=headers, json=payload)

    if response.status_code != 200:
        click.echo(f"❌ Retry failed: {response.text}", err=True)
        return

    click.echo("✅ Task queued for retry")
