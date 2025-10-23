# 📦 Odoo Apps Installation Guide - insightpulseai.net

## ✅ Apps List Updated

The Odoo apps list has been refreshed and all OCA modules are now available for installation via the web interface.

## 🌐 Install Apps via Web Interface

### Access the Apps Page
**URL**: https://insightpulseai.net/odoo/apps

### Login Credentials
- **Username**: `admin`
- **Password**: Set on first login (default: `admin`)

### Installation Steps

1. **Login to Odoo**
   - Navigate to: https://insightpulseai.net
   - Login with `admin` / `admin` (or your set password)
   - Click "Apps" in the main menu

2. **Update Apps List**
   - Click "Update Apps List" button
   - Wait for refresh to complete
   - This will show all available OCA modules

3. **Search and Install Modules**
   - Use search bar to find modules
   - Click "Install" button on desired modules
   - Wait for installation to complete

## 📋 Recommended OCA Modules to Install

### Essential Tools (server-tools)
- ✅ **auditlog** - Track all database changes for compliance
- ✅ **auto_backup** - Automated database backups (already have cron, but adds UI)
- ✅ **base_exception** - Exception handling framework
- ✅ **base_search_fuzzy** - Fuzzy search across fields
- ✅ **base_technical_user** - Technical features access control
- ✅ **date_range** - Date range management
- ✅ **base_fontawesome** - FontAwesome icons

### Web Enhancements (web)
- ✅ **web_responsive** - Responsive mobile-friendly interface
- ✅ **web_widget_colorpicker** - Color picker widget
- ✅ **web_dialog_size** - Resizable dialogs
- ✅ **web_no_bubble** - Remove bubble effects
- ✅ **web_timeline** - Timeline view for records
- ✅ **web_domain_field** - Advanced domain editor

### Queue & Background Jobs (queue)
- ✅ **queue_job** - Async job processing
- ✅ **queue_job_cron** - Cron integration for jobs
- ✅ **queue_job_subscribe** - Job notifications

### Reporting (reporting-engine)
- ✅ **report_xlsx** - Excel report generation
- ✅ **report_qweb_pdf_watermark** - PDF watermarks
- ✅ **report_qweb_element_page_visibility** - Conditional report elements
- ✅ **report_wkhtmltopdf_param** - Advanced PDF options

### Accounting (account-financial-tools)
- ✅ **account_move_line_menu** - Direct access to journal items
- ✅ **account_type_menu** - Account type management
- ✅ **account_fiscal_year** - Fiscal year management
- ✅ **account_lock_date_update** - Lock date controls

### HR (hr)
- ✅ **hr_employee_age** - Employee age calculations
- ✅ **hr_holidays_public** - Public holidays management
- ✅ **hr_employee_service** - Employee service tracking

### Purchase (purchase-workflow)
- ✅ **purchase_order_approval_block** - Purchase approval workflow
- ✅ **purchase_request** - Purchase requisitions
- ✅ **purchase_tier_validation** - Multi-level approvals

### Custom Addons
- ✅ **knowledge_notion_clone** - Notion-style workspace (custom)

## 🚀 Quick Install via CLI (Alternative)

If you prefer CLI installation, use the pre-installed script:

```bash
ssh root@188.166.237.231 "/opt/bundle/install-modules.sh odoo"
```

This installs a curated set of essential modules automatically.

## 📊 Module Categories in Apps Interface

### Filter by Category
- **Sales** - CRM, sales orders, quotations
- **Accounting** - Invoicing, expenses, payments
- **Inventory** - Stock, manufacturing, maintenance
- **Human Resources** - Employees, recruitment, time off
- **Marketing** - Email marketing, events, surveys
- **Website** - Website builder, eCommerce, blog
- **Productivity** - Project management, documents, calendar
- **Services** - Field service, helpdesk, appointments
- **Customizations** - Technical tools, integrations

### Search Tips
- Search by name: `web_responsive`
- Search by category: `accounting`
- Filter by: "Installed", "Not Installed", "Apps", "Themes"

## 🔍 Finding OCA Modules

### In Apps Interface
1. Click "Apps" menu
2. Remove "Apps" filter (shows all modules, not just apps)
3. Search for OCA module names
4. Look for modules with "OCA" in description

### Common OCA Module Prefixes
- `base_*` - Base framework extensions
- `web_*` - Web interface enhancements
- `account_*` - Accounting modules
- `hr_*` - HR modules
- `purchase_*` - Purchase workflow
- `sale_*` - Sales workflow
- `stock_*` - Inventory modules
- `queue_*` - Background job processing
- `report_*` - Reporting tools

## ⚙️ Post-Installation Configuration

### After Installing Modules

1. **Configure Settings**
   - Navigate to: Settings → Technical → Parameters
   - Configure module-specific settings

2. **Set Permissions**
   - Settings → Users & Companies → Groups
   - Assign module access to user groups

3. **Test Functionality**
   - Verify module features work as expected
   - Check for conflicts with existing modules

### Important Settings

**Queue Jobs** (if installed):
- Settings → Technical → Queue Jobs
- Configure job workers and channels

**Auto Backup** (if installed):
- Settings → Technical → Scheduled Actions
- Configure backup schedule and retention

**Auditlog** (if installed):
- Settings → Technical → Audit → Rules
- Configure which models to audit

## 🔧 Module Paths

All OCA modules are located at:
```
/opt/bundle/addons/oca/
├── server-tools/          # 48 modules
├── web/                   # 52 modules
├── queue/                 # 14 modules
├── reporting-engine/      # 27 modules
├── account-financial-tools/ # 39 modules
├── hr/                    # 22 modules
├── purchase-workflow/     # 82 modules
└── server-auth/           # 24 modules
```

Custom modules:
```
/opt/bundle/addons/custom/
└── knowledge_notion_clone/ # Notion-style workspace
```

## 📝 Installation via Web Interface

### Step-by-Step Example

1. **Access Apps**: https://insightpulseai.net/odoo/apps
2. **Login**: Use admin credentials
3. **Update List**: Click "Update Apps List"
4. **Search Module**: Type "web_responsive" in search
5. **Install**: Click "Install" button
6. **Wait**: Installation completes automatically
7. **Verify**: Check that module appears in "Installed" filter

### Batch Installation

For multiple modules:
1. Install one module at a time via UI
2. Wait for each installation to complete
3. Some modules have dependencies that auto-install
4. Check "Installed" filter to see all active modules

## 🎯 Next Steps

1. **Browse Available Apps**: https://insightpulseai.net/odoo/apps
2. **Install Recommended Modules**: Use search to find OCA modules
3. **Configure Settings**: Settings → Technical → Parameters
4. **Enable OCR Integration**: Install expense/invoice modules to use OCR
5. **Test Knowledge Base**: Install knowledge_notion_clone for Notion-style docs

## 📚 Additional Resources

- **OCA Documentation**: https://odoo-community.org/
- **Module Documentation**: Each module has built-in help text
- **Odoo Apps Store**: https://apps.odoo.com/ (for reference)

---

**Status**: ✅ Apps list updated, all OCA modules available
**Access**: https://insightpulseai.net/odoo/apps
**Modules Available**: 308+ OCA modules + custom addons
