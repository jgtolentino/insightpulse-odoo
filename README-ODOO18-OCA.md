# Odoo 18 + OCA Production Stack

**Production-grade project structure for Odoo 18 CE + OCA + IPAI custom modules**

This repository provides a clean, reproducible, and version-pinned setup for running Odoo 18 Community Edition with OCA (Odoo Community Association) modules and custom IPAI modules.

---

## 📁 Repository Structure

```
insightpulse-odoo/
├── docker/
│   ├── docker-compose.odoo18.yml    # Docker Compose for Odoo 18
│   ├── odoo.conf                     # Odoo configuration
│   └── entrypoint.d/
│       └── 10-gen-addons-path.sh     # Auto-generate addons_path
├── scripts/
│   ├── clone_oca.sh                  # Clone OCA 18.0 repositories
│   ├── install_waves.sh              # Install modules in waves
│   └── check_api_mismatches.sh       # API compatibility guard
├── addons/
│   ├── ipai_core/                    # Base custom module
│   ├── ipai_hr/                      # HR custom modules
│   └── ipai_stock/                   # Stock custom modules
├── oca/                               # OCA repos (18.0 only) - created by init
│   ├── sale-workflow/
│   ├── server-tools/
│   ├── stock-logistics-workflow/
│   └── ...
├── waves/
│   ├── 00_base.txt                   # Core modules
│   ├── 10_web_ux.txt                 # Web UX modules
│   ├── 20_sales_inventory.txt        # Sales & inventory
│   ├── 30_accounting.txt             # Accounting modules
│   ├── 40_hr_project.txt             # HR & project
│   ├── 50_ipai_custom.txt            # Custom IPAI modules
│   └── 90_optional.txt               # Optional modules
├── .env.odoo18.example               # Environment configuration
├── Makefile.odoo18                   # Make commands
└── README-ODOO18-OCA.md              # This file
```

---

## 🚀 Quick Start

### 1. Prerequisites

- Docker & Docker Compose
- Git
- Make (optional, but recommended)

### 2. Initial Setup

```bash
# Clone the repository (if not already done)
cd insightpulse-odoo

# Copy environment configuration
cp .env.odoo18.example .env

# Initialize the stack (clone OCA, build addons_path, run checks)
make -f Makefile.odoo18 init
```

### 3. Install Modules in Waves

```bash
# Install all modules in predefined order
make -f Makefile.odoo18 waves
```

### 4. Access Odoo

Open your browser to: **http://localhost:8069**

**Default credentials:**
- Database: `odoo18`
- Email: `admin`
- Password: `admin`

---

## 🛠️ Common Operations

### Start/Stop Services

```bash
# Start Odoo 18 stack
make -f Makefile.odoo18 up

# Stop stack (preserve data)
make -f Makefile.odoo18 down

# Restart stack
make -f Makefile.odoo18 restart
```

### Install/Update Modules

```bash
# Install a specific module
make -f Makefile.odoo18 install-module MODULE=sale_management

# Update a module
make -f Makefile.odoo18 update-module MODULE=ipai_core
```

### Debugging

```bash
# View logs (follow mode)
make -f Makefile.odoo18 logs

# Open shell in Odoo container
make -f Makefile.odoo18 shell

# Open PostgreSQL shell
make -f Makefile.odoo18 psql
```

### Run Checks

```bash
# Run API compatibility checks
make -f Makefile.odoo18 check
```

---

## 📦 Module Installation Waves

Modules are installed in **waves** (ordered batches) to ensure dependencies are met:

| Wave | File                     | Description                  |
|------|--------------------------|------------------------------|
| 00   | `00_base.txt`            | Core Odoo modules            |
| 10   | `10_web_ux.txt`          | Web interface enhancements   |
| 20   | `20_sales_inventory.txt` | Sales & inventory management |
| 25   | `25_localization.txt`    | Localization & accounting    |
| 30   | `30_accounting.txt`      | Advanced accounting          |
| 40   | `40_hr_project.txt`      | HR & project management      |
| 50   | `50_ipai_custom.txt`     | Custom IPAI modules          |
| 90   | `90_optional.txt`        | Optional modules             |

### Adding Custom Modules to Waves

Edit the appropriate wave file and add your module name:

```bash
echo "my_custom_module" >> waves/50_ipai_custom.txt
make -f Makefile.odoo18 waves
```

---

## 🔧 Configuration

### Environment Variables

Edit `.env` to customize your setup:

```bash
# Database
POSTGRES_DB=odoo18
POSTGRES_USER=odoo
POSTGRES_PASSWORD=odoo

# Ports
HOST_PORT_ODOO=8069
HOST_PORT_LONGPOLL=8072
HOST_PORT_DB=5433

# Admin
ADMIN_PASS=admin
```

### Adding OCA Repositories

Edit `scripts/clone_oca.sh` and add to the `REPOS` array:

```bash
REPOS=(
  web
  server-tools
  # ... existing repos ...
  your-new-oca-repo  # Add here
)
```

Then run:

```bash
bash scripts/clone_oca.sh ./oca
```

---

## 🏗️ Creating Custom Modules

### 1. Generate Module Structure

```bash
mkdir -p addons/ipai_mymodule/{models,security,views}
```

### 2. Create `__manifest__.py`

```python
{
    "name": "IPAI My Module",
    "version": "18.0.1.0.0",
    "summary": "Brief description",
    "author": "InsightPulse AI",
    "license": "LGPL-3",
    "depends": ["base", "ipai_core"],
    "data": [
        "security/ir.model.access.csv",
        "views/my_views.xml",
    ],
    "installable": True,
}
```

### 3. Create Models, Views, Security

Follow the structure in `addons/ipai_core/` as a template.

### 4. Add to Wave File

```bash
echo "ipai_mymodule" >> waves/50_ipai_custom.txt
```

### 5. Install

```bash
make -f Makefile.odoo18 install-module MODULE=ipai_mymodule
```

---

## 🛡️ API Compatibility Guards

The `check_api_mismatches.sh` script blocks known Odoo 19.x-only API patterns:

- `res.groups.user_ids` (use `res.groups.users` in 18.x)
- `group_id.user_ids` (use `group_id.users` in 18.x)

Add more patterns as needed to prevent version incompatibilities.

---

## 📋 Tips & Best Practices

### 1. Keep OCA Repos on 18.0 Branch

All OCA repositories should be on the `18.0` branch to avoid API mismatches:

```bash
bash scripts/clone_oca.sh ./oca 18.0
```

### 2. Version Pinning

Bump module versions when changing data models to force upgrade migrations:

```python
"version": "18.0.1.1.0",  # Increment when adding fields/models
```

### 3. Module Dependencies

Always declare dependencies in `__manifest__.py`:

```python
"depends": ["base", "sale", "ipai_core"],
```

### 4. Security Rules

Always include security rules (`ir.model.access.csv` and `security.xml`).

### 5. Module Testing

Test modules locally before deploying:

```bash
# Install module
make -f Makefile.odoo18 install-module MODULE=my_module

# Check logs for errors
make -f Makefile.odoo18 logs
```

---

## 🧹 Cleanup

```bash
# Remove containers, volumes, and OCA repos
make -f Makefile.odoo18 clean
```

**Warning:** This will delete all data!

---

## 📚 Resources

- [Odoo 18 Documentation](https://www.odoo.com/documentation/18.0/)
- [OCA Guidelines](https://github.com/OCA/odoo-community.org)
- [Odoo Development Guide](https://www.odoo.com/documentation/18.0/developer.html)

---

## 🆘 Support

For issues and support:
- GitHub Issues: [insightpulse-odoo/issues](https://github.com/jgtolentino/insightpulse-odoo/issues)
- Website: https://insightpulseai.net

---

## 📄 License

LGPL-3

---

## 🎯 Next Steps

If you want to ship specific IPAI modules (e.g., `ipai_procurement`, `ipai_kpi_dash`), provide the module names and I'll generate ready-to-run module skeletons plus their wave entries.

Example:

```bash
# Request module generation
# Module: ipai_procurement
# Features: Purchase request automation, vendor management
```
