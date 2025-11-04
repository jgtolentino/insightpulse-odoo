#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
InsightPulse CLI - Main Entry Point

Deterministic automation commands for:
- Deployments (DigitalOcean App Platform)
- Database migrations (Supabase PostgreSQL)
- Visual parity testing (Playwright)
- Task queue operations (Supabase RPC)
"""

import click
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from ipai_cli import commands


@click.group()
@click.version_option(version='1.0.0')
@click.pass_context
def main(ctx):
    """
    InsightPulse CLI - Automation tool for InsightPulse-Odoo project

    \b
    Examples:
      ipai deploy ade-ocr --env production
      ipai migrate apply --file 00_task_bus.sql
      ipai test visual --routes /expenses,/tasks
      ipai task sync --status pending
    """
    ctx.ensure_object(dict)

    # Load configuration
    ctx.obj['SUPABASE_URL'] = os.getenv('SUPABASE_URL')
    ctx.obj['SUPABASE_SERVICE_ROLE_KEY'] = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    ctx.obj['DO_ACCESS_TOKEN'] = os.getenv('DO_ACCESS_TOKEN')
    ctx.obj['POSTGRES_URL'] = os.getenv('POSTGRES_URL')


# Register command groups
main.add_command(commands.deploy)
main.add_command(commands.migrate)
main.add_command(commands.test)
main.add_command(commands.task)
main.add_command(commands.ask)


if __name__ == '__main__':
    main()
