# Odoo.sh Deployment Reference

Complete guide for deploying custom Odoo modules to Odoo.sh containers.

## Container Environment

### Directory Structure

```
/home/odoo/
├── src/
│   ├── odoo/          # Odoo Community (v19.0)
│   ├── enterprise/    # Odoo Enterprise
│   ├── themes/        # Odoo Themes
│   └── user/          # Your custom modules (Git repository)
├── data/
│   ├── filestore/     # Database attachments
│   └── sessions/      # User sessions
├── logs/
│   ├── odoo.log       # Server logs
│   ├── install.log    # Installation logs
│   ├── update.log     # Update logs
│   └── pip.log        # Python package logs
└── .config/
    └── odoo/
        └── odoo.conf  # Odoo configuration
```

### Python Environment

**Python Version:** Python 3.10+ (Odoo 19)

**Standard Libraries:**
- `/usr/lib/python3/dist-packages/` - System libraries
- `/usr/local/lib/python3/dist-packages/` - Third-party libraries

**Virtual Environment:** Not required (packages install globally)

## Custom Dependencies

### requirements.txt

Create in your **repository root** (not module folder):

```txt
# requirements.txt

# Data Processing
pandas>=1.5.0
numpy>=1.23.0

# API Clients
requests>=2.28.0
python-dotenv>=0.20.0

# OCR & AI
paddleocr>=2.6.0
paddlepaddle>=2.4.0

# Database
supabase>=1.0.0
psycopg2-binary>=2.9.0

# Philippine Services
paymongo>=1.0.0

# Image Processing
pillow>=9.0.0

# Utilities
python-dateutil>=2.8.0
pytz>=2022.1
```

**Installation:** Odoo.sh automatically installs on build

**Multiple Files:** Submodule requirements.txt also supported

### Python Version Requirements

```txt
# Minimum Python 3.10
python-requires = >=3.10
```

## Module Deployment Workflow

### 1. Git Repository Setup

```bash
# Your repository structure
your-repo/
├── requirements.txt
├── custom_modules/
│   ├── bir_tax_filing/
│   ├── travel_expense_management/
│   └── connection_manager/
├── .gitignore
└── README.md
```

### 2. Push to Git

```bash
# Add custom modules
git add custom_modules/

# Commit
git commit -m "Add custom modules"

# Push to branch
git push origin staging  # For staging environment
git push origin production  # For production
```

### 3. Auto-Deployment

**Odoo.sh automatically:**
1. Pulls latest code
2. Installs `requirements.txt` dependencies
3. Updates module list
4. Runs tests (if configured)
5. Deploys to container

### 4. Install Module in Database

```bash
# SSH into container
ssh <project>-<branch>.odoo.sh

# Install module
odoo-bin -i custom_module --stop-after-init

# Update module
odoo-bin -u custom_module --stop-after-init
```

## Database Shell Access

### Accessing PostgreSQL

```bash
# Connect to database
psql

# You're now in PostgreSQL shell
project-branch=> SELECT * FROM ir_module_module WHERE state = 'installed';
```

### Safe SQL Practices

**ALWAYS use transactions:**

```sql
-- Start transaction
BEGIN;

-- Make changes
UPDATE res_partner SET email = 'test@example.com' WHERE id = 1;

-- Review changes
SELECT * FROM res_partner WHERE id = 1;

-- Commit if correct, or ROLLBACK if mistake
COMMIT;  -- or ROLLBACK;
```

**Never forget to commit/rollback!** Open transactions lock tables.

## Odoo Shell

### Launching Odoo Shell

```bash
odoo-bin shell
```

### Common Shell Operations

```python
>>> # Get environment
>>> env = self.env

>>> # Search records
>>> partners = env['res.partner'].search([('customer_rank', '>', 0)])
>>> len(partners)
1250

>>> # Read data
>>> partner = partners[0]
>>> partner.name
'ABC Corporation'

>>> # Create records
>>> new_partner = env['res.partner'].create({
...     'name': 'New Customer',
...     'email': 'customer@example.com',
... })

>>> # Update records
>>> partner.write({'phone': '+639123456789'})

>>> # Commit changes
>>> env.cr.commit()

>>> # Exit
>>> exit()
```

## Running Tests

### Unit Tests

```bash
# Install with tests
odoo-bin -i custom_module --test-enable --log-level=test --stop-after-init

# Update with tests
odoo-bin -u custom_module --test-enable --log-level=test --stop-after-init
```

### Test Output

```
test_create_bir_form (tests.test_bir_form.TestBIRForm) ... ok
test_compute_withholding (tests.test_bir_form.TestBIRForm) ... ok
test_filing_deadline (tests.test_bir_form.TestBIRForm) ... ok

----------------------------------------------------------------------
Ran 3 tests in 2.45s

OK
```

## Debugging

### Using pdb

```python
# In your code
import sys
if sys.__stdin__.isatty():
    import pdb; pdb.set_trace()
```

### Debug in Shell

```bash
# Launch Odoo shell
odoo-bin shell

# Trigger the code with debugger
>>> self.env['bir.form.1601c'].browse(1).action_compute_withholding()
# Debugger activates here
(Pdb) 
```

### Using ipdb (Better Interface)

1. **Add to requirements.txt:**
```txt
ipdb>=0.13.0
```

2. **Use in code:**
```python
import sys
if sys.__stdin__.isatty():
    import ipdb; ipdb.set_trace()
```

## Log Monitoring

### View Logs

```bash
# Real-time logs
tail -f ~/logs/odoo.log

# Installation logs
cat ~/logs/install.log

# Python package logs
cat ~/logs/pip.log

# Search for errors
grep ERROR ~/logs/odoo.log
```

### Log Levels

```python
import logging
_logger = logging.getLogger(__name__)

_logger.debug('Debug message')
_logger.info('Info message')
_logger.warning('Warning message')
_logger.error('Error message')
_logger.critical('Critical message')
```

## Addons Path

### Finding Addons Path

```bash
# Check logs for addons paths
grep "addons paths" ~/logs/odoo.log
```

**Output:**
```
odoo: addons paths: [
    '/home/odoo/data/addons/19.0',
    '/home/odoo/src/user',           # Your custom modules
    '/home/odoo/src/enterprise',
    '/home/odoo/src/themes',
    '/home/odoo/src/odoo/addons',
    '/home/odoo/src/odoo/odoo/addons'
]
```

## Configuration File

### odoo.conf Location

`/home/odoo/.config/odoo/odoo.conf`

### Common Settings

```ini
[options]
addons_path = /home/odoo/src/user,/home/odoo/src/enterprise,/home/odoo/src/odoo/addons
data_dir = /home/odoo/data
logfile = /home/odoo/logs/odoo.log
log_level = info
workers = 4
max_cron_threads = 2
```

## Environment Variables

### Setting Environment Variables

**In Odoo.sh Project Settings:**
1. Go to project settings
2. Add environment variables
3. Redeploy

**Format:**
```
SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
SUPABASE_KEY=your_api_key
PADDLEOCR_API_URL=http://paddleocr-service:8000
```

**Access in Python:**
```python
import os
supabase_url = os.getenv('SUPABASE_URL')
```

## Branch Strategy

### Recommended Branches

1. **Development**: Feature development and testing
2. **Staging**: Pre-production testing with production data copy
3. **Production**: Live environment

### Workflow

```bash
# Develop in development branch
git checkout development
git add .
git commit -m "Add feature"
git push origin development

# Test passes? Merge to staging
git checkout staging
git merge development
git push origin staging

# Staging tests pass? Merge to production
git checkout production
git merge staging
git push origin production
```

## Backup & Restore

### Automatic Backups

Odoo.sh automatically creates daily backups of production databases.

### Manual Backup

```bash
# Download database
# From Odoo.sh interface or API
```

### Restore from Backup

```bash
# Upload backup via Odoo.sh interface
# Or use database manager
```

## Performance Optimization

### Database Indexing

```python
# Add index to frequently queried field
class BIRForm(models.Model):
    tin = fields.Char(string='TIN', index=True)  # Indexed
    filing_period = fields.Date(string='Period', index=True)
```

### Computed Field Storage

```python
# Store computed field for performance
total_amount = fields.Monetary(
    string='Total',
    compute='_compute_total',
    store=True  # Stored in database
)
```

### Query Optimization

```python
# Bad: N+1 queries
for partner in partners:
    print(partner.country_id.name)  # Separate query each time

# Good: Prefetch
partners = env['res.partner'].search([...])
partners.mapped('country_id')  # Prefetch all countries
for partner in partners:
    print(partner.country_id.name)  # No additional queries
```

## Security Considerations

### Access Control

Always define in `security/ir.model.access.csv`:

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_bir_form_user,bir_form_user,model_bir_form_1601c,base.group_user,1,1,1,0
access_bir_form_manager,bir_form_manager,model_bir_form_1601c,base.group_system,1,1,1,1
```

### Record Rules

```xml
<record id="bir_form_multi_agency_rule" model="ir.rule">
    <field name="name">BIR Form: Multi-Agency Access</field>
    <field name="model_id" ref="model_bir_form_1601c"/>
    <field name="domain_force">[('agency_code', '=', user.agency_code)]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>
```

### Password Fields

```python
# Never store plain text passwords
api_key = fields.Char(string='API Key', password=True)
```

## Troubleshooting

### Module Not Found

```bash
# Update module list
odoo-bin --stop-after-init --update=base
```

### Import Errors

```bash
# Check Python packages
pip list

# Reinstall if missing
pip install package_name --break-system-packages
```

### Permission Denied

```bash
# Check file permissions
ls -la custom_modules/

# Fix if needed
chmod -R 755 custom_modules/
```

### Database Errors

```bash
# Check database logs
tail -f ~/logs/odoo.log | grep ERROR

# Access database directly
psql
```

## Best Practices

1. **Version Control Everything**: All custom code in git
2. **Test Before Production**: Use staging branch
3. **Monitor Logs**: Watch for errors
4. **Backup Regularly**: Although automatic, manual backups for important changes
5. **Use Transactions**: Always in database operations
6. **Document Changes**: Clear commit messages
7. **Security First**: Proper access controls
8. **Performance**: Index fields, optimize queries
9. **Code Review**: Peer review before merging
10. **Rollback Plan**: Know how to revert changes

## Resources

- [Odoo.sh Documentation](https://www.odoo.com/documentation/19.0/administration/odoo_sh.html)
- [Odoo Developer Documentation](https://www.odoo.com/documentation/19.0/developer.html)
- [OCA Guidelines](https://github.com/OCA/odoo-community.org)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
