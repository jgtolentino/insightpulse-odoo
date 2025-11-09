# Odoo Addons Structure

**Last Updated:** 2025-11-09
**Purpose:** Document Odoo module structure, configuration, and management

---

## Overview

InsightPulse Odoo uses a three-tier addons structure:

1. **Custom Modules** - InsightPulse-specific functionality
2. **OCA Modules** - Community-maintained modules (17 repositories)
3. **Core Modules** - Standard Odoo CE modules

**Module Precedence:** Custom → OCA → Core (allows custom modules to override OCA/Core)

---

## Module Inventory

### Custom Modules (3 modules)

Located in `custom_addons/` (mapped to `/mnt/extra-addons/custom` in container):

| Module | Purpose | Status |
|--------|---------|--------|
| `ip_expense_mvp` | InsightPulse Expense Management MVP | Active |
| `ipai_mattermost_bridge` | Mattermost chat integration | Active |
| `pulser_webhook` | Pulser v4.0.0 AI webhook integration | Active |

### OCA Modules (17 repositories)

Located in `bundle/addons/oca/` (mapped to `/mnt/extra-addons/oca/*` in container):

#### Finance & Accounting (Critical for BIR Compliance)
| Repository | Purpose | Module Count |
|-----------|---------|--------------|
| `account-invoicing` | Invoice management, portal | ~15 modules |
| `account-payment` | Payment terms, reconciliation | ~12 modules |
| `account-reconcile` | Bank reconciliation | ~8 modules |
| `account-financial-reporting` | Financial statements | ~10 modules |
| `account-financial-tools` | Financial utilities | ~8 modules |
| `account-budgeting` | Budget management | ~5 modules |
| `bank-payment` | Bank integrations | ~10 modules |

#### Procurement & HR
| Repository | Purpose | Module Count |
|-----------|---------|--------------|
| `purchase-workflow` | Purchase orders, RFQs | ~12 modules |
| `partner-contact` | Contact management | ~15 modules |
| `hr` | HR extensions | ~8 modules |

#### Server & Infrastructure
| Repository | Purpose | Module Count |
|-----------|---------|--------------|
| `server-auth` | OAuth, LDAP, SSO | ~8 modules |
| `server-tools` | Utilities, date range, cron | ~20 modules |
| `server-backend` | Backend enhancements | ~10 modules |
| `queue` | Job queues, async tasks | ~5 modules |
| `rest-framework` | REST API framework | ~3 modules |

#### Reporting & Web
| Repository | Purpose | Module Count |
|-----------|---------|--------------|
| `reporting-engine` | Report generation | ~8 modules |
| `web` | Web interface enhancements | ~15 modules |

**Total OCA Modules:** ~200+ modules across 17 repositories

---

## Configuration

### addons_path (odoo.conf)

```ini
addons_path = /mnt/extra-addons/custom,
              /mnt/extra-addons/oca/account-invoicing,
              /mnt/extra-addons/oca/account-payment,
              /mnt/extra-addons/oca/account-reconcile,
              /mnt/extra-addons/oca/account-financial-reporting,
              /mnt/extra-addons/oca/account-financial-tools,
              /mnt/extra-addons/oca/bank-payment,
              /mnt/extra-addons/oca/server-auth,
              /mnt/extra-addons/oca/server-tools,
              /mnt/extra-addons/oca/server-backend,
              /mnt/extra-addons/oca/queue,
              /mnt/extra-addons/oca/rest-framework,
              /mnt/extra-addons/oca/web,
              /mnt/extra-addons/oca/purchase-workflow,
              /mnt/extra-addons/oca/partner-contact,
              /mnt/extra-addons/oca/hr,
              /mnt/extra-addons/oca/reporting-engine,
              /mnt/extra-addons/oca/account-budgeting,
              /usr/lib/python3/dist-packages/odoo/addons
```

**Precedence Explanation:**
- Odoo searches paths **left to right**
- First match wins (allows overrides)
- Custom modules can override OCA/Core modules
- OCA modules can override Core modules

### Volume Mounts (docker-compose.yml)

```yaml
volumes:
  # Custom InsightPulse modules
  - ./custom_addons:/mnt/extra-addons/custom:ro

  # OCA Modules - Finance & Accounting
  - ./bundle/addons/oca/account-invoicing:/mnt/extra-addons/oca/account-invoicing:ro
  - ./bundle/addons/oca/account-payment:/mnt/extra-addons/oca/account-payment:ro
  # ... (15 more OCA repositories)

  # Configuration
  - ./odoo.conf:/etc/odoo/odoo.conf:ro
```

**Security Notes:**
- All mounts use `:ro` (read-only) flag
- Prevents container from modifying host files
- Configuration file also read-only

---

## Adding New Modules

### Adding Custom Modules

1. **Create module directory:**
   ```bash
   mkdir -p custom_addons/my_new_module
   cd custom_addons/my_new_module
   ```

2. **Create __manifest__.py:**
   ```python
   {
       'name': 'My New Module',
       'version': '18.0.1.0.0',
       'category': 'Custom',
       'summary': 'Brief description',
       'author': 'InsightPulse AI',
       'website': 'https://insightpulseai.net',
       'license': 'LGPL-3',
       'depends': ['base'],
       'data': [],
       'installable': True,
       'application': False,
       'auto_install': False,
   }
   ```

3. **Restart Odoo:**
   ```bash
   docker compose restart odoo
   ```

4. **Install module:**
   - Navigate to Apps
   - Update Apps List
   - Search for "My New Module"
   - Click Install

### Adding OCA Modules

1. **Clone OCA repository:**
   ```bash
   cd bundle/addons/oca
   git clone https://github.com/OCA/repository-name.git -b 18.0
   ```

2. **Add to odoo.conf:**
   ```ini
   # Add new line to addons_path (before core):
   /mnt/extra-addons/oca/repository-name,
   ```

3. **Add volume mount to docker-compose.yml:**
   ```yaml
   volumes:
     # ... existing mounts
     - ./bundle/addons/oca/repository-name:/mnt/extra-addons/oca/repository-name:ro
   ```

4. **Restart and install:**
   ```bash
   docker compose down
   docker compose up -d
   # Then install via Apps menu
   ```

---

## Module Loading Verification

### Check Addons Path

```bash
docker compose exec odoo odoo shell -c "from odoo.tools import config; print(config['addons_path'])"
```

### Check Loaded Modules

```bash
# View logs during startup
docker compose logs odoo | grep "addons paths"

# Check for module errors
docker compose logs odoo | grep -i "error" | grep -i "module"
```

### Verify Module Installation

```bash
# List installed modules
docker compose exec odoo odoo shell -c "
from odoo import api, SUPERUSER_ID
env = api.Environment(cr, SUPERUSER_ID, {})
modules = env['ir.module.module'].search([('state', '=', 'installed')])
print('\n'.join(modules.mapped('name')))
"
```

---

## Troubleshooting

### Module Not Found

**Symptom:** Module doesn't appear in Apps list

**Solutions:**
1. Verify addons_path includes module directory
2. Check __manifest__.py syntax (valid Python dict)
3. Restart Odoo: `docker compose restart odoo`
4. Update Apps List (Apps menu → Update Apps List)

### Module Import Error

**Symptom:** Error during module installation

**Solutions:**
1. Check module dependencies in __manifest__.py
2. Verify all dependency modules are installed
3. Check Python import errors in logs
4. Verify file permissions (should be readable by odoo user)

### Module Override Not Working

**Symptom:** Custom module not overriding OCA/Core

**Solutions:**
1. Verify addons_path order (custom should come first)
2. Check module names match exactly
3. Ensure __manifest__.py version is higher
4. Restart Odoo completely: `docker compose down && docker compose up -d`

### Permission Denied Errors

**Symptom:** Cannot write to module directory

**Solutions:**
1. Verify volume mounts use `:ro` flag (read-only is correct)
2. Module files should be owned by host user, not container
3. For development, temporarily remove `:ro` flag
4. Always restore `:ro` flag before production deployment

---

## Best Practices

### Module Development
- **Version Numbering:** Use Odoo convention `18.0.1.0.0` (Odoo version.major.minor.patch)
- **License:** Use LGPL-3 for compatibility with Odoo CE
- **Dependencies:** Minimize dependencies to avoid conflicts
- **Testing:** Add tests in `tests/` directory

### OCA Module Updates
- **Version Pinning:** Pin OCA repos to specific commits in production
- **Testing:** Test OCA updates in staging before production
- **Documentation:** Document which OCA modules are actively used
- **Upgrades:** Plan OCA upgrades with Odoo version upgrades

### Security
- **Read-Only Mounts:** Always use `:ro` flag in docker-compose.yml
- **File Permissions:** Module files should not be writable by container
- **Code Review:** Review all custom modules for security issues
- **OCA Modules:** Prefer well-maintained OCA modules over custom code

---

## Related Documentation

- [Platform Specification](../../spec/platform_spec.json) - Canonical source of truth
- [Docker Compose Guide](docker-compose.md) - Container configuration
- [CI/CD Workflows](workflows-ci-cd.md) - Testing and deployment
- [Odoo Documentation](https://www.odoo.com/documentation/18.0/developer.html) - Official Odoo 18 docs
- [OCA Guidelines](https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst) - OCA contribution standards

---

## Module Statistics

- **Custom Modules:** 3
- **OCA Repositories:** 17
- **OCA Modules:** ~200+
- **Core Modules:** ~100+ (standard Odoo CE)
- **Total Available:** ~300+ modules

**Installed Modules:** Run verification command above to get current count.
