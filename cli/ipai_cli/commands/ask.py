# -*- coding: utf-8 -*-
"""Natural Language Agent Commands"""

import click
import requests
import os


@click.command()
@click.argument('query', nargs=-1, required=True)
@click.option('--agent-url', envvar='IPAI_AGENT_URL',
              default='https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run/chat',
              help='AI Agent API URL')
@click.option('--api-key', envvar='IPAI_AGENT_API_KEY', help='API key for authentication')
@click.pass_context
def ask(ctx, query, agent_url, api_key):
    """
    Ask AI agent using natural language

    \b
    Examples:
      ipai ask "Deploy OCR service to production"
      ipai ask "Show me pending expenses for RIM"
      ipai ask "Generate BIR 1601-C form for CKVC"
    """
    query_str = ' '.join(query)

    click.echo(f"🤖 Asking AI agent: {query_str}")

    # Build context
    context = {
        'user': {
            'name': os.getenv('USER', 'CLI User'),
            'email': os.getenv('USER_EMAIL', 'cli@insightpulseai.net'),
        },
        'channel': 'CLI',
        'timestamp': click.get_current_context().obj.get('timestamp', ''),
    }

    # Build payload
    payload = {
        'message': query_str,
        'context': context,
        'tools': ['digitalocean', 'supabase', 'github', 'odoo'],
        'max_tokens': 4096,
    }

    # Build headers
    headers = {
        'Content-Type': 'application/json',
    }

    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'

    # Call agent API
    try:
        response = requests.post(
            agent_url,
            json=payload,
            headers=headers,
            timeout=60
        )

        response.raise_for_status()
        result = response.json()

        # Display response
        click.echo("\n" + "="*60)
        click.echo(result.get('message', ''))
        click.echo("="*60)

        # Display actions if any
        actions = result.get('actions', [])
        if actions:
            click.echo("\n📋 Actions:")
            for i, action in enumerate(actions, 1):
                status = '✅' if action.get('success') else '❌'
                click.echo(f"{i}. {status} {action.get('type')}: {action.get('description', '')}")

        # Display execution time
        exec_time = result.get('execution_time', 0)
        if exec_time:
            click.echo(f"\n⏱️ Execution time: {exec_time:.2f}s")

    except requests.exceptions.RequestException as e:
        click.echo(f"❌ Agent API error: {str(e)}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {str(e)}", err=True)
        sys.exit(1)
