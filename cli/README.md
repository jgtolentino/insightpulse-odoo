# InsightPulse CLI (ipai-cli)

Command-line automation tool for InsightPulse-Odoo project operations.

## Features

- 🚀 **Deployments**: DigitalOcean App Platform service deployments
- 📊 **Database Migrations**: Supabase PostgreSQL migration management
- ✅ **Automated Testing**: Visual parity, unit, integration, E2E tests
- 📋 **Task Queue**: Supabase task queue operations
- 🤖 **AI Agent**: Natural language command interface

## Installation

### Prerequisites

- Python 3.11+
- DigitalOcean CLI (`doctl`)
- PostgreSQL client (`psql`)
- Node.js 18+ (for test scripts)

### Install from Source

```bash
# From project root
cd cli

# Install in development mode
pip install -e .

# Verify installation
ipai --version
```

### Environment Variables

Create `.env` file in project root:

```bash
# Supabase
SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
POSTGRES_URL=postgresql://postgres:password@host:6543/postgres

# DigitalOcean
DO_ACCESS_TOKEN=your_do_token

# AI Agent (optional)
IPAI_AGENT_URL=https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run/chat
IPAI_AGENT_API_KEY=your_agent_api_key
USER_EMAIL=jgtolentino_rn@yahoo.com
```

## Usage

### Deploy Commands

```bash
# Deploy OCR service to production
ipai deploy ade-ocr --env production --force-rebuild

# Deploy expense flow API
ipai deploy expense-flow --env production

# Deploy without waiting
ipai deploy ade-ocr --no-wait
```

**Available Services**:
- `ade-ocr` - OCR backend service
- `expense-flow` - Expense flow API
- `superset` - Apache Superset BI
- `pulse-hub-web` - Pulse Hub web frontend
- `pulser-hub-mcp` - MCP service

### Migration Commands

```bash
# Apply single migration
ipai migrate apply --file packages/db/sql/00_task_bus.sql

# Apply all migrations
ipai migrate apply --all

# Check migration status
ipai migrate status

# Rollback migration
ipai migrate rollback --file packages/db/sql/00_task_bus.sql
```

### Test Commands

```bash
# Visual parity tests
ipai test visual --routes /expenses,/tasks --threshold 0.97

# Unit tests
ipai test unit

# Integration tests
ipai test integration

# E2E tests
ipai test e2e --base-url https://atomic-crm.vercel.app
```

### Task Queue Commands

```bash
# List tasks
ipai task list --status pending --limit 50

# Sync task queue
ipai task sync --status processing

# Cancel task
ipai task cancel --task-id 123

# Retry failed task
ipai task retry --task-id 456
```

### AI Agent Commands

```bash
# Ask AI agent using natural language
ipai ask "Deploy OCR service to production"

ipai ask "Show me pending expenses for RIM"

ipai ask "Generate BIR 1601-C form for CKVC, October 2025"

ipai ask "Run visual parity tests on /expenses route"
```

## Command Reference

### `ipai deploy`

Deploy service to DigitalOcean App Platform.

**Arguments**:
- `service` - Service name (ade-ocr, expense-flow, etc.)

**Options**:
- `--env` - Environment (production, staging) [default: production]
- `--force-rebuild` - Force rebuild from source
- `--wait/--no-wait` - Wait for deployment [default: wait]

**Example**:
```bash
ipai deploy ade-ocr --env production --force-rebuild
```

### `ipai migrate`

Manage database migrations.

**Arguments**:
- `action` - Migration action (apply, status, rollback)

**Options**:
- `--file` - Migration SQL file path
- `--all` - Apply all pending migrations

**Example**:
```bash
ipai migrate apply --file packages/db/sql/00_task_bus.sql
```

### `ipai test`

Run automated tests.

**Arguments**:
- `test_type` - Test type (visual, unit, integration, e2e)

**Options**:
- `--routes` - Routes to test (comma-separated) [default: /expenses,/tasks]
- `--threshold` - SSIM threshold [default: 0.97]
- `--base-url` - Base URL for testing [default: http://localhost:4173]
- `--output` - Screenshot output directory [default: ./screenshots]

**Example**:
```bash
ipai test visual --routes /expenses,/tasks --threshold 0.97
```

### `ipai task`

Manage Supabase task queue.

**Arguments**:
- `action` - Task action (sync, list, cancel, retry)

**Options**:
- `--status` - Filter by status (pending, processing, completed, failed, cancelled)
- `--task-id` - Specific task ID
- `--limit` - Maximum tasks to show [default: 50]

**Example**:
```bash
ipai task list --status pending
```

### `ipai ask`

Natural language AI agent interface.

**Arguments**:
- `query` - Natural language query (multiple words)

**Options**:
- `--agent-url` - AI Agent API URL [env: IPAI_AGENT_URL]
- `--api-key` - API key for authentication [env: IPAI_AGENT_API_KEY]

**Example**:
```bash
ipai ask "Deploy OCR service to production"
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install ipai-cli
        run: |
          cd cli
          pip install -e .

      - name: Deploy OCR service
        env:
          DO_ACCESS_TOKEN: ${{ secrets.DO_ACCESS_TOKEN }}
        run: ipai deploy ade-ocr --env production

      - name: Run visual tests
        env:
          POSTGRES_URL: ${{ secrets.POSTGRES_URL }}
        run: ipai test visual --routes /expenses,/tasks
```

## Development

### Project Structure

```
cli/
├── setup.py                # Package setup
├── ipai_cli/
│   ├── __init__.py
│   ├── cli.py             # Main CLI entry
│   └── commands/
│       ├── __init__.py
│       ├── deploy.py      # Deployment commands
│       ├── migrate.py     # Migration commands
│       ├── test.py        # Testing commands
│       ├── task.py        # Task queue commands
│       └── ask.py         # AI agent commands
└── README.md
```

### Adding New Commands

1. Create command file in `ipai_cli/commands/`:

```python
# ipai_cli/commands/my_command.py
import click

@click.command()
@click.argument('arg')
@click.option('--flag', is_flag=True)
@click.pass_context
def my_command(ctx, arg, flag):
    """My command description"""
    click.echo(f"Executing with {arg}")
```

2. Register in `ipai_cli/commands/__init__.py`:

```python
from .my_command import my_command
__all__ = ['deploy', 'migrate', 'test', 'task', 'ask', 'my_command']
```

3. Add to main CLI in `ipai_cli/cli.py`:

```python
from ipai_cli import commands
main.add_command(commands.my_command)
```

## Troubleshooting

### Command not found

```bash
# Reinstall CLI
cd cli
pip install -e .

# Check installation
which ipai
```

### Missing environment variables

```bash
# Check required variables
echo $POSTGRES_URL
echo $DO_ACCESS_TOKEN

# Load from .env
export $(cat .env | xargs)
```

### Deployment failures

```bash
# Check doctl authentication
doctl account get

# View deployment logs
doctl apps logs <app-id> --follow

# Check app status
doctl apps get <app-id>
```

## License

AGPL-3

## Author

Jake Tolentino
Email: jgtolentino_rn@yahoo.com
