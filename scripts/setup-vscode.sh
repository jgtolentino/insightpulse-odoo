#!/usr/bin/env bash
set -euo pipefail

echo "🚀 Setting up VS Code configuration for InsightPulse Odoo..."

mkdir -p .vscode

cat > .vscode/extensions.json <<'JSON'
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "charliermarsh.ruff",
    "ms-python.black-formatter",
    "ms-python.isort",
    "redhat.vscode-yaml",
    "eamodio.gitlens",
    "EditorConfig.EditorConfig",
    "Gruntfuggly.todo-tree",
    "aaron-bond.better-comments",
    "wholroyd.jinja",
    "dotjoshjohnson.xml",
    "littlefoxteam.vscode-python-test-adapter",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "ms-azuretools.vscode-docker",
    "ms-vscode-remote.remote-containers",
    "ms-vscode-remote.remote-ssh",
    "ms-kubernetes-tools.vscode-kubernetes-tools",
    "mtxr.sqltools",
    "mtxr.sqltools-driver-pg",
    "sqlfluff.sqlfluff",
    "innoverio.vscode-dbt-power-user",
    "alexcvzz.vscode-sqlite",
    "hashicorp.terraform",
    "github.vscode-github-actions",
    "ms-vscode.remote-explorer",
    "humao.rest-client",
    "christian-kohler.path-intellisense",
    "VisualStudioExptTeam.vscodeintellicode"
  ]
}
JSON

cat > .vscode/settings.json <<'JSON'
{
  "editor.formatOnSave": true,
  "files.trimTrailingWhitespace": true,
  "files.insertFinalNewline": true,

  "python.testing.pytestEnabled": true,
  "python.analysis.typeCheckingMode": "basic",
  "ruff.importStrategy": "fromEnvironment",

  "[python]": { "editor.defaultFormatter": "charliermarsh.ruff" },
  "[json]":   { "editor.defaultFormatter": "esbenp.prettier-vscode" },
  "[yaml]":   { "editor.defaultFormatter": "esbenp.prettier-vscode" },
  "[markdown]": { "editor.defaultFormatter": "esbenp.prettier-vscode" },

  "sqlfluff.dialect": "postgres",

  "files.associations": {
    "*.xml": "jinja",
    "*.qweb": "jinja"
  },

  "docker.composeCommand": "docker compose",

  "terraform.languageServer": {
    "enabled": true
  },

  "terminal.integrated.env.osx": {
    "ODOO_ENV": "dev"
  }
}
JSON

cat > .vscode/launch.json <<'JSON'
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Odoo: Run Server",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/odoo-bin",
      "args": [
        "-c", "${workspaceFolder}/config/odoo/odoo.conf",
        "-d", "${input:dbName}",
        "--dev=reload,qweb,assets"
      ],
      "console": "integratedTerminal",
      "justMyCode": false,
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    },
    {
      "name": "Odoo: Update Module",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/odoo-bin",
      "args": [
        "-c", "${workspaceFolder}/config/odoo/odoo.conf",
        "-d", "${input:dbName}",
        "-u", "${input:moduleName}",
        "--stop-after-init"
      ],
      "console": "integratedTerminal",
      "justMyCode": false
    },
    {
      "name": "Pytest (Current File)",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": [
        "-q",
        "${file}"
      ],
      "console": "integratedTerminal",
      "justMyCode": false
    },
    {
      "name": "Superset: Dev Server (inside venv)",
      "type": "python",
      "request": "launch",
      "module": "flask",
      "cwd": "${workspaceFolder}",
      "env": {
        "FLASK_APP": "superset.app:create_app()",
        "FLASK_ENV": "development",
        "SUPERSET_CONFIG_PATH": "${workspaceFolder}/superset_config.py"
      },
      "args": [
        "run",
        "--host", "0.0.0.0",
        "--port", "8088"
      ],
      "console": "integratedTerminal",
      "justMyCode": false
    }
  ],
  "inputs": [
    {
      "id": "dbName",
      "type": "promptString",
      "description": "Odoo database name",
      "default": "odoo_dev"
    },
    {
      "id": "moduleName",
      "type": "promptString",
      "description": "Odoo module to update",
      "default": "base"
    }
  ]
}
JSON

cat > .vscode/tasks.json <<'JSON'
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Docker: Compose Up",
      "type": "shell",
      "command": "docker compose up -d",
      "problemMatcher": []
    },
    {
      "label": "Docker: Compose Down",
      "type": "shell",
      "command": "docker compose down",
      "problemMatcher": []
    },
    {
      "label": "Ruff: Lint",
      "type": "shell",
      "command": "ruff check .",
      "problemMatcher": []
    },
    {
      "label": "Ruff: Format",
      "type": "shell",
      "command": "ruff format .",
      "problemMatcher": []
    },
    {
      "label": "SQLFluff: Lint",
      "type": "shell",
      "command": "sqlfluff lint .",
      "problemMatcher": []
    },
    {
      "label": "Odoo: Update Base (CLI)",
      "type": "shell",
      "command": "python odoo-bin -c ./config/odoo/odoo.conf -d ${input:dbName} -u base --stop-after-init",
      "problemMatcher": []
    },
    {
      "label": "Superset: Init (CLI)",
      "type": "shell",
      "command": "superset fab create-admin || true && superset db upgrade && superset init",
      "problemMatcher": []
    }
  ],
  "inputs": [
    {
      "id": "dbName",
      "type": "promptString",
      "description": "Odoo database name",
      "default": "odoo_dev"
    }
  ]
}
JSON

echo "✅ VS Code configuration completed!"
echo "📋 Next steps:"
echo "   1. Open VS Code and install recommended extensions"
echo "   2. Configure Python interpreter (Ctrl+Shift+P → 'Python: Select Interpreter')"
echo "   3. Use F5 to debug Odoo or Superset"
echo "   4. Use Ctrl+Shift+P → 'Tasks: Run Task' for common operations"
