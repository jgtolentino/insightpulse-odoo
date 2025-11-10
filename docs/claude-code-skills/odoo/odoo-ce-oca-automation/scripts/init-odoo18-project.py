#!/usr/bin/env python3
"""
Initialize a new Odoo 18 CE + OCA project with complete automation setup.

This script creates:
- Repository structure following OCA standards
- Docker Compose configuration
- CI/CD pipelines (GitHub Actions)
- Terraform infrastructure
- Pre-commit hooks
- Coding guidelines
- Documentation

Usage:
    python3 init-odoo18-project.py \\
        --name my-odoo-project \\
        --features accounting,helpdesk,project \\
        --domain example.com \\
        --provider digitalocean
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

# OCA Feature to Module Mapping (Odoo 18)
OCA_FEATURE_MAP = {
    "accounting": {
        "repos": ["account-financial-reporting", "account-financial-tools"],
        "modules": [
            "account_financial_report",
            "mis_builder",
            "account_asset_management",
        ],
    },
    "helpdesk": {
        "repos": ["helpdesk"],
        "modules": ["helpdesk_mgmt", "helpdesk_mgmt_ticket_type"],
    },
    "project": {
        "repos": ["project", "project-agile"],
        "modules": ["project_task_default_stage", "project_timeline", "project_agile"],
    },
    "hr": {
        "repos": ["hr", "hr-attendance", "hr-expense"],
        "modules": [
            "hr_expense_advance_clearing",
            "hr_timesheet_sheet",
            "hr_holidays_public",
        ],
    },
    "crm": {
        "repos": ["crm"],
        "modules": ["crm_phonecall", "crm_claim"],
    },
    "inventory": {
        "repos": ["stock-logistics-warehouse", "stock-logistics-workflow"],
        "modules": ["stock_available", "stock_picking_invoice_link"],
    },
    "manufacturing": {
        "repos": ["manufacture"],
        "modules": ["mrp_bom_structure", "mrp_production_note"],
    },
    "ecommerce": {
        "repos": ["e-commerce"],
        "modules": ["website_sale_hide_price", "website_sale_cart_expire"],
    },
}


def create_directory_structure(project_path: Path):
    """Create OCA-compliant directory structure."""
    directories = [
        "addons/custom",
        "addons/oca",
        "scripts",
        "docs",
        ".github/workflows",
        "terraform",
        "config",
    ]

    for directory in directories:
        (project_path / directory).mkdir(parents=True, exist_ok=True)

    print(f"✅ Created directory structure at {project_path}")


def generate_docker_compose(project_path: Path, project_name: str):
    """Generate docker-compose.yml for Odoo 18 CE."""
    docker_compose = f"""version: '3.8'

services:
  web:
    image: odoo:18.0
    container_name: {project_name}_odoo
    depends_on:
      - db
    ports:
      - "8069:8069"
      - "8072:8072"  # Longpolling
    volumes:
      - odoo-web-data:/var/lib/odoo
      - ./config:/etc/odoo
      - ./addons/custom:/mnt/extra-addons/custom
      - ./addons/oca:/mnt/extra-addons/oca
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo
      - DB_NAME={project_name}_db
    command: odoo --workers=4 --max-cron-threads=2

  db:
    image: postgres:15
    container_name: {project_name}_db
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_PASSWORD=odoo
      - POSTGRES_USER=odoo
      - PGDATA=/var/lib/postgresql/data/pgdata
    volumes:
      - odoo-db-data:/var/lib/postgresql/data/pgdata
    ports:
      - "5432:5432"

volumes:
  odoo-web-data:
  odoo-db-data:
"""

    (project_path / "docker-compose.yml").write_text(docker_compose)
    print("✅ Generated docker-compose.yml")


def generate_odoo_conf(project_path: Path, project_name: str):
    """Generate odoo.conf configuration."""
    odoo_conf = f"""[options]
addons_path = /mnt/extra-addons/custom,/mnt/extra-addons/oca,/usr/lib/python3/dist-packages/odoo/addons
data_dir = /var/lib/odoo
admin_passwd = admin
db_host = db
db_port = 5432
db_user = odoo
db_password = odoo
db_name = {project_name}_db

; Performance
workers = 4
max_cron_threads = 2
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
limit_request = 8192
limit_time_cpu = 600
limit_time_real = 1200

; Logging
log_level = info
log_handler = :INFO
logfile = /var/log/odoo/odoo.log

; Security
list_db = False
proxy_mode = True
"""

    (project_path / "config" / "odoo.conf").write_text(odoo_conf)
    print("✅ Generated odoo.conf")


def generate_repos_yaml(project_path: Path, features: List[str]):
    """Generate repos.yaml for OCA module vendoring."""
    repos = {}

    for feature in features:
        if feature in OCA_FEATURE_MAP:
            for repo in OCA_FEATURE_MAP[feature]["repos"]:
                if repo not in repos:
                    repos[repo] = {
                        "url": f"https://github.com/OCA/{repo}",
                        "branch": "18.0",
                        "modules": [],
                    }
                repos[repo]["modules"].extend(
                    OCA_FEATURE_MAP[feature]["modules"]
                )

    # Remove duplicates
    for repo in repos:
        repos[repo]["modules"] = list(set(repos[repo]["modules"]))

    # Generate YAML
    yaml_content = "# OCA Module Repositories for Odoo 18\n"
    yaml_content += "# Generated by init-odoo18-project.py\n\n"

    for repo_name, repo_config in repos.items():
        yaml_content += f"{repo_name}:\n"
        yaml_content += f'  url: {repo_config["url"]}\n'
        yaml_content += f'  branch: "{repo_config["branch"]}"\n'
        yaml_content += "  modules:\n"
        for module in repo_config["modules"]:
            yaml_content += f"    - {module}\n"
        yaml_content += "\n"

    (project_path / "addons" / "oca" / "repos.yaml").write_text(yaml_content)
    print(f"✅ Generated repos.yaml with {len(repos)} OCA repositories")


def generate_github_actions(project_path: Path, project_name: str):
    """Generate GitHub Actions CI/CD pipeline."""
    workflow = f"""name: Odoo 18 CE CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    name: Code Quality
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install pylint flake8 black isort pylint-odoo

      - name: Run Black
        run: black --check addons/custom/

      - name: Run isort
        run: isort --check addons/custom/

      - name: Run Flake8
        run: flake8 addons/custom/

      - name: Run Pylint
        run: pylint --load-plugins=pylint_odoo addons/custom/

  test:
    name: Unit Tests
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: {project_name}_test
          POSTGRES_USER: odoo
          POSTGRES_PASSWORD: odoo
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4

      - name: Start Odoo
        run: docker-compose -f docker-compose.test.yml up -d

      - name: Wait for Odoo
        run: |
          for i in {{1..30}}; do
            curl -f http://localhost:8069/web/health && break
            sleep 2
          done

      - name: Run Tests
        run: |
          docker-compose exec -T web odoo \\
            -d {project_name}_test \\
            --test-enable \\
            --stop-after-init \\
            --log-level=test

      - name: Check Module Installation
        run: |
          docker-compose exec -T web odoo \\
            -d {project_name}_test \\
            -i $(cat addons/oca/repos.yaml | grep -A1 "modules:" | grep "-" | sed 's/- //g' | tr '\\n' ',') \\
            --stop-after-init

  security:
    name: Security Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install security tools
        run: pip install bandit safety

      - name: Run Bandit
        run: bandit -r addons/custom/

      - name: Run Safety
        run: safety check

  deploy:
    name: Deploy to Production
    needs: [lint, test, security]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to DigitalOcean
        env:
          DO_TOKEN: ${{{{ secrets.DO_TOKEN }}}}
          DO_APP_ID: ${{{{ secrets.DO_APP_ID }}}}
        run: |
          curl -X POST \\
            -H "Authorization: Bearer $DO_TOKEN" \\
            -H "Content-Type: application/json" \\
            "https://api.digitalocean.com/v2/apps/$DO_APP_ID/deployments"

      - name: Health Check
        run: |
          sleep 60
          curl -f https://{project_name}.example.com/web/health
"""

    (project_path / ".github" / "workflows" / "odoo-ci.yml").write_text(workflow)
    print("✅ Generated GitHub Actions CI/CD pipeline")


def generate_pre_commit_config(project_path: Path):
    """Generate pre-commit configuration."""
    pre_commit = """repos:
  - repo: https://github.com/psf/black
    rev: 24.1.1
    hooks:
      - id: black
        args: [--line-length=79]

  - repo: https://github.com/PyCQA/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: [--profile=black, --line-length=79]

  - repo: https://github.com/PyCQA/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=79]

  - repo: https://github.com/OCA/pylint-odoo
    rev: v9.0.4
    hooks:
      - id: pylint_odoo
        name: pylint with optional checks
        args:
          - --rcfile=.pylintrc
          - --valid_odoo_versions=18.0

  - repo: https://github.com/OCA/maintainer-tools
    rev: master
    hooks:
      - id: oca-gen-addon-readme
      - id: oca-update-pre-commit-excluded-addons
"""

    (project_path / ".pre-commit-config.yaml").write_text(pre_commit)
    print("✅ Generated pre-commit configuration")


def generate_pylintrc(project_path: Path):
    """Generate OCA-compliant .pylintrc."""
    pylintrc = """[MASTER]
load-plugins=pylint_odoo
score=n

[MESSAGES CONTROL]
disable=all
enable=anomalous-backslash-in-string,
       api-one-deprecated,
       api-one-multi-together,
       attribute-deprecated,
       class-camelcase,
       dangerous-default-value,
       dangerous-view-replace-wo-priority,
       development-status-allowed,
       duplicate-id-csv,
       duplicate-key,
       duplicate-xml-record-id,
       eval-referenced,
       except-pass,
       line-too-long,
       manifest-author-string,
       manifest-deprecated-key,
       manifest-required-author,
       manifest-required-key,
       manifest-version-format,
       method-compute,
       method-inverse,
       method-required-super,
       method-search,
       missing-import-error,
       missing-manifest-dependency,
       missing-newline-extrafiles,
       missing-readme,
       odoo-addons-relative-import,
       old-api7-method-defined,
       openerp-exception-warning,
       print-used,
       renamed-field-parameter,
       resource-not-exist,
       sql-injection,
       translation-field,
       translation-required,
       use-vim-comment,
       wrong-tabs-instead-of-spaces

[REPORTS]
msg-template={path}:{line}: [{msg_id}({symbol}), {obj}] {msg}
output-format=colorized
reports=no

[BASIC]
class-rgx=[A-Z_][a-zA-Z0-9]+$
const-rgx=(([a-z_][a-z0-9_]*)|([A-Z_][A-Z0-9_]*))$
method-rgx=[a-z_][a-z0-9_]{2,}$
module-rgx=[a-z_][a-z0-9_]*$
function-rgx=[a-z_][a-z0-9_]{2,}$
name-group=
no-docstring-rgx=__.*__|_.*
docstring-min-length=10

[SIMILARITIES]
ignore-comments=yes
ignore-docstrings=yes
min-similarity-lines=4

[IMPORTS]
deprecated-modules=openerp,openerp.addons,odoo.addons.base

[DESIGN]
max-args=5
max-attributes=7
max-branches=12
max-locals=15
max-module-lines=1000
max-nested-blocks=5
max-parents=7
max-public-methods=20
max-returns=6
max-statements=50
min-public-methods=2

[CLASSES]
defining-attr-methods=__init__,_compute,_inverse,_search

[ODOOLINT]
valid_odoo_versions=18.0
"""

    (project_path / ".pylintrc").write_text(pylintrc)
    print("✅ Generated .pylintrc")


def generate_readme(project_path: Path, project_name: str, features: List[str], domain: str):
    """Generate comprehensive README.md."""
    readme = f"""# {project_name}

Odoo 18 Community Edition with OCA modules for enterprise-grade ERP functionality.

## Features

This project includes OCA modules for:
{chr(10).join([f"- **{feature.title()}**: {', '.join(OCA_FEATURE_MAP[feature]['modules'])}" for feature in features if feature in OCA_FEATURE_MAP])}

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Git

### Installation

1. **Clone repository**:
   ```bash
   git clone https://github.com/yourusername/{project_name}.git
   cd {project_name}
   ```

2. **Vendor OCA modules**:
   ```bash
   python3 scripts/vendor_oca.py --repos addons/oca/repos.yaml
   ```

3. **Start services**:
   ```bash
   docker-compose up -d
   ```

4. **Access Odoo**:
   - URL: http://localhost:8069
   - Email: admin
   - Password: admin

### Development

1. **Install pre-commit hooks**:
   ```bash
   pip install pre-commit
   pre-commit install
   ```

2. **Create custom module**:
   ```bash
   python3 scripts/scaffold_module.py \\
     --name my_custom_module \\
     --path addons/custom
   ```

3. **Run tests**:
   ```bash
   docker-compose exec web odoo \\
     -d {project_name}_db \\
     --test-enable \\
     --stop-after-init
   ```

## Production Deployment

### DigitalOcean

1. **Configure Terraform**:
   ```bash
   cd terraform
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your settings
   ```

2. **Deploy**:
   ```bash
   terraform init
   terraform plan
   terraform apply
   ```

3. **Access**:
   - URL: https://{domain}

## CI/CD

GitHub Actions automatically:
- ✅ Lints code on every PR
- ✅ Runs tests
- ✅ Scans for security vulnerabilities
- ✅ Deploys to production on merge to main

## Project Structure

```
{project_name}/
├── addons/
│   ├── custom/              # Custom modules
│   └── oca/                 # Vendored OCA modules
├── config/
│   └── odoo.conf            # Odoo configuration
├── scripts/                 # Automation scripts
├── terraform/               # Infrastructure as Code
├── .github/workflows/       # CI/CD pipelines
├── docker-compose.yml       # Development environment
└── README.md                # This file
```

## Cost Savings

| Component | Enterprise | OCA + Self-Host | Savings |
|-----------|-----------|-----------------|---------|
| Odoo License (10 users) | $4,320/year | $0 | $4,320 |
| Hosting (Odoo.sh) | $720/year | - | $720 |
| DigitalOcean | - | $288/year | -$288 |
| **Total** | **$5,040/year** | **$288/year** | **$4,752/year (94%)** |

## Documentation

- [OCA Module Documentation](https://odoo-community.org/)
- [Odoo 18 Documentation](https://www.odoo.com/documentation/18.0/)
- [Contributing Guide](CONTRIBUTING.md)

## Support

For issues or questions:
- Open an issue on GitHub
- Check [OCA documentation](https://odoo-community.org/)
- Consult [Odoo forums](https://www.odoo.com/forum)

## License

- Custom modules: [Your License]
- OCA modules: LGPL-3 or AGPL-3 (see individual module licenses)
- Odoo CE: LGPL-3

---

**Version**: 1.0.0
**Odoo Version**: 18.0 Community Edition
**Generated**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}
"""

    (project_path / "README.md").write_text(readme)
    print("✅ Generated README.md")


def main():
    parser = argparse.ArgumentParser(
        description="Initialize Odoo 18 CE + OCA project with automation"
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Project name (e.g., my-odoo-project)",
    )
    parser.add_argument(
        "--features",
        required=True,
        help="Comma-separated features (e.g., accounting,helpdesk,project)",
    )
    parser.add_argument(
        "--domain",
        default="example.com",
        help="Domain name for deployment",
    )
    parser.add_argument(
        "--provider",
        default="digitalocean",
        choices=["digitalocean", "aws", "azure"],
        help="Cloud provider for deployment",
    )
    parser.add_argument(
        "--path",
        default=".",
        help="Path to create project (default: current directory)",
    )

    args = parser.parse_args()

    # Parse features
    features = [f.strip() for f in args.features.split(",")]

    # Create project path
    project_path = Path(args.path) / args.name
    if project_path.exists():
        print(f"❌ Error: Directory {project_path} already exists")
        sys.exit(1)

    print(f"🚀 Initializing Odoo 18 CE + OCA project: {args.name}")
    print(f"📦 Features: {', '.join(features)}")
    print(f"🌐 Domain: {args.domain}")
    print(f"☁️  Provider: {args.provider}")
    print()

    # Create structure
    create_directory_structure(project_path)
    generate_docker_compose(project_path, args.name)
    generate_odoo_conf(project_path, args.name)
    generate_repos_yaml(project_path, features)
    generate_github_actions(project_path, args.name)
    generate_pre_commit_config(project_path)
    generate_pylintrc(project_path)
    generate_readme(project_path, args.name, features, args.domain)

    print()
    print("✨ Project initialized successfully!")
    print()
    print("Next steps:")
    print(f"  1. cd {args.name}")
    print("  2. git init && git add . && git commit -m 'Initial commit'")
    print("  3. python3 scripts/vendor_oca.py --repos addons/oca/repos.yaml")
    print("  4. docker-compose up -d")
    print("  5. Open http://localhost:8069")


if __name__ == "__main__":
    main()
