# Scheduled Jobs Inventory

**Generated:** 2025-11-09
**Updated:** 2025-11-09 (Odoo 19 CE Compatibility)
**Branch:** claude/inventory-scheduled-jobs-011CUxA7R3jK2Cgy3FeX8kAr
**Odoo Version:** 19.0 CE
**Status:** No running Odoo instance detected

## Overview

This document provides an inventory of all scheduled recurring jobs (cron jobs) configured in the InsightPulse Odoo 19 CE system. All cron jobs have been updated to follow Odoo 19 CE best practices.

## Instance Status

- **Docker Instance:** Not running / Not available
- **Database Connection:** Not configured
- **Note:** This inventory is based on cron job definitions found in the codebase

---

## Scheduled Jobs

### 1. Cleanup Expired Superset Tokens

**Module:** `superset_connector`
**Definition:** `addons/custom/superset_connector/data/cron_jobs.xml:5`

| Property | Value |
|----------|-------|
| **ID** | `ir_cron_cleanup_expired_tokens` |
| **Name** | Cleanup Expired Superset Tokens |
| **Model** | `superset.token` |
| **Method** | `model.cleanup_expired_tokens()` |
| **Interval** | Every 1 day(s) |
| **Active** | True |
| **Priority** | 10 |
| **Number of Calls** | -1 (unlimited) |
| **Do All** | False |
| **Purpose** | Removes expired authentication tokens for Superset integration |

---

### 2. Odoo Forum Scraper

**Module:** `odoo_knowledge_agent`
**Definition:** `addons/custom/odoo_knowledge_agent/data/cron_forum_scraper.xml:6`

| Property | Value |
|----------|-------|
| **ID** | `cron_forum_scraper` |
| **Name** | Odoo Forum Scraper |
| **Model** | `odoo.knowledge.agent` |
| **Method** | `model.cron_scrape_forum()` |
| **Interval** | Every 1 week(s) |
| **Active** | True |
| **Priority** | 50 |
| **Number of Calls** | -1 (unlimited) |
| **Do All** | False |
| **Purpose** | Scrapes Odoo forums for knowledge base updates and issue resolution patterns |

---

### 3. IPAI Subscriptions Invoicing

**Module:** `ipai_subscriptions`
**Definition:** `addons/custom/ipai_subscriptions/data/cron.xml:2`

| Property | Value |
|----------|-------|
| **ID** | `cron_ipai_invoice` |
| **Name** | IPAI Subscriptions Invoicing |
| **Model** | `ipai.subscription` |
| **Method** | `model._cron_generate_invoices()` |
| **Interval** | Every 1 day(s) |
| **Active** | True |
| **Priority** | Not specified (default) |
| **Number of Calls** | -1 (unlimited) |
| **Do All** | Not specified |
| **Purpose** | Generates invoices for active subscriptions on their billing cycle |

---

### 4. Refresh Apps Index

**Module:** `apps_admin_enhancements`
**Definition:** `addons/custom/apps_admin_enhancements/data/cron_refresh.xml:2`

| Property | Value |
|----------|-------|
| **ID** | `ir_cron_refresh_apps_index` |
| **Name** | Refresh Apps Index |
| **Model** | `ir.module.module` |
| **Method** | `model.update_list()` |
| **Interval** | Every 24 hour(s) |
| **Active** | True |
| **Priority** | Not specified (default) |
| **Number of Calls** | Not specified |
| **Do All** | Not specified |
| **Purpose** | Updates the available apps/modules index from configured repositories |

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| **Total Jobs** | 4 |
| **Active Jobs** | 4 |
| **Daily Jobs** | 2 |
| **Weekly Jobs** | 1 |
| **Hourly Jobs** | 1 |

## Execution Schedule

| Time Frequency | Jobs |
|----------------|------|
| **Daily (24h)** | Cleanup Expired Superset Tokens, IPAI Subscriptions Invoicing |
| **Weekly (7d)** | Odoo Forum Scraper |
| **Every 24 Hours** | Refresh Apps Index |

## Runtime Status

**Note:** To check the actual runtime status of these jobs, you need:

1. A running Odoo instance with these modules installed
2. Database access to query the `ir_cron` table
3. Access to check job execution logs in `ir_logging` or cron-specific tables

### To Check Job Status (when instance is running):

```sql
-- Check all cron jobs
SELECT
    name,
    active,
    interval_number,
    interval_type,
    nextcall,
    lastcall,
    numbercall
FROM ir_cron
WHERE name IN (
    'Cleanup Expired Superset Tokens',
    'Odoo Forum Scraper',
    'IPAI Subscriptions Invoicing',
    'Refresh Apps Index'
)
ORDER BY nextcall;
```

```sql
-- Check cron execution logs
SELECT
    c.name as job_name,
    l.create_date,
    l.type,
    l.message
FROM ir_logging l
JOIN ir_cron c ON l.name = c.name
WHERE l.name LIKE '%cron%'
ORDER BY l.create_date DESC
LIMIT 50;
```

## Odoo 19 CE Compatibility Updates

All scheduled jobs have been updated to comply with Odoo 19 CE best practices:

### Changes Made:

1. **XML Declaration**: Added proper `<?xml version="1.0" encoding="utf-8"?>` header to all files
2. **Data Protection**: Ensured all cron definitions use `<data noupdate="1">` to prevent overwrites on module upgrades
3. **User Context**: Added `user_id` field referencing `base.user_admin` for proper execution context
4. **Boolean Fields**: Standardized boolean fields using `eval="True"` and `eval="False"` syntax
5. **Field Completeness**: Added missing fields like `numbercall` and `doall` where needed
6. **Documentation**: Enhanced inline XML comments with purpose, frequency, and dependencies
7. **Module Versions**: All modules use 19.0.x.x.x versioning scheme

### Odoo 19 CE Features Utilized:

- **Proper User Context**: All cron jobs run under `base.user_admin` ensuring correct permissions
- **No Update Flag**: Protects cron configuration from being reset during module updates
- **Complete Field Definitions**: All recommended fields are explicitly set for clarity
- **Enhanced Comments**: Inline documentation improves maintainability and understanding

## Recommendations

1. **Monitoring:** Set up monitoring for cron job execution to track success/failure rates
2. **Logs:** Implement comprehensive logging for each cron job execution
3. **Alerts:** Configure alerts for failed cron jobs, especially for critical jobs like invoicing
4. **Performance:** Monitor execution time for jobs that may grow in complexity (forum scraper, token cleanup)
5. **Testing:** Ensure each cron job can be manually triggered for testing purposes
6. **User Context:** Consider creating a dedicated technical user for cron jobs instead of using base.user_admin
7. **Queue Jobs:** For long-running operations, consider integrating with queue_job module for better control

## Related Files

- `addons/custom/superset_connector/data/cron_jobs.xml`
- `addons/custom/odoo_knowledge_agent/data/cron_forum_scraper.xml`
- `addons/custom/ipai_subscriptions/data/cron.xml`
- `addons/custom/apps_admin_enhancements/data/cron_refresh.xml`

---

*Last Updated: 2025-11-09*
*Branch: claude/inventory-scheduled-jobs-011CUxA7R3jK2Cgy3FeX8kAr*
