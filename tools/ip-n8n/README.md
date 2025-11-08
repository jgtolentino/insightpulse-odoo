# ip-n8n CLI

Command-line interface for managing n8n workflows.

## Installation

```bash
# From repo root
make n8n-cli
```

## Configuration

```bash
# Set configuration path (optional)
export IP_N8N_CONFIG=~/.config/ip-n8n/config.json

# Login to n8n instance
./ip-n8n login --base https://n8n.insightpulseai.net --key $N8N_API_KEY
```

## Usage

### List workflows
```bash
./ip-n8n list
```

### Get workflow details
```bash
./ip-n8n get 12
```

### Run workflow
```bash
./ip-n8n run 12
```

### Activate/Deactivate workflow
```bash
./ip-n8n activate 12
./ip-n8n deactivate 12
```

### Import workflow
```bash
./ip-n8n import path/to/workflow.json
```

### Export workflow
```bash
./ip-n8n export 12 --out backup.json
```

### Execute webhook
```bash
./ip-n8n exec-webhook https://n8n.../webhook/TOKEN --data '{"text":"ping"}'
```

## Make Targets

```bash
make n8n-list           # List all workflows
make n8n-run ID=12      # Run workflow by ID
make n8n-import FILE=workflow.json  # Import workflow
```

## Configuration File

Default location: `~/.config/ip-n8n/config.json`

```json
{
  "base_url": "https://n8n.insightpulseai.net",
  "api_key": "YOUR_N8N_API_KEY"
}
```

## Requirements

- Python 3.8+
- `requests` library (installed automatically by `make n8n-cli`)

## Security

- Store API keys in the config file with `chmod 600`
- Never commit config files to version control
- Use environment-specific API keys
