# November 2025 Monthly Close - Installation & Testing Guide

**Start Date**: Monday, 24 November 2025
**Review Due**: Tuesday, 25 November 2025 (AM)
**Approval Due**: Tuesday, 25 November 2025 (EOD)
**Month End**: Friday, 28 November 2025

---

## Quick Installation (5 minutes)

### Step 1: Install Module

```bash
# SSH to Odoo server
ssh root@erp.insightpulseai.net

# Navigate to addons
cd /opt/odoo-ce/addons

# Pull latest from Git
git pull origin feature/add-expense-equipment-prd

# Restart Odoo
systemctl restart odoo

# Check Odoo is running
systemctl status odoo
```

### Step 2: Install via UI

1. Open browser: `https://erp.insightpulseai.net`
2. Login as admin
3. **Apps** → Click **Update Apps List**
4. Search: **"PPM Monthly Close"**
5. Click **Install**

### Step 3: Verify Installation

Navigate to: **Monthly Close** (new menu should appear in top menu bar)

You should see 3 submenus:
- Close Schedules
- Tasks
- Templates

---

## Verify Template Data (1 minute)

**Monthly Close → Templates**

You should see **10 pre-configured templates**:

| Agency | Task Category | Owner | Reviewer | Approver |
|--------|---------------|-------|----------|----------|
| RIM | Rent & Leases | jtolentino | jgtolentino | finance_manager |
| CKVC | Accounts Payable | ap_specialist | jtolentino | finance_manager |
| BOM | Payroll Processing | payroll_admin | hr_manager | finance_manager |
| JPAL | Revenue Recognition | revenue_analyst | jtolentino | cfo |
| JLI | Bank Reconciliation | treasury_analyst | treasury_manager | finance_manager |
| JAP | Fixed Assets Depreciation | asset_accountant | jtolentino | finance_manager |
| LAS | Inventory Count | warehouse_supervisor | operations_manager | finance_manager |
| RMQB | Expense Accruals | expense_analyst | jtolentino | finance_manager |
| RIM | Consolidated Reporting | jtolentino | cfo | ceo |
| RIM | BIR Compliance | tax_specialist | jtolentino | finance_manager |

**Action Required**: Update employee codes to match your actual Odoo users
- Click **Edit** on each template
- Replace placeholder codes with real employee logins
- Click **Save**

---

## Create November 2025 Close (2 minutes)

### Option A: Manual Creation (Recommended for first time)

1. **Monthly Close → Close Schedules**
2. Click **Create**
3. Set **Close Month**: `2025-11-01` (November 2025)
4. Click **Save**

**Verify Computed Dates**:
- ✅ Month End (C): **28 Nov 2025** (Friday)
- ✅ Prep Start (S): **24 Nov 2025** (Monday)
- ✅ Review Due: **25 Nov 2025** (Tuesday)
- ✅ Approval Due: **25 Nov 2025** (Tuesday)

5. Click **Generate Tasks** button
   - Should create **10 tasks** from templates
   - Status changes to **Scheduled**

6. Click **Start Close Process** button
   - Status changes to **In Progress**
   - Notifications sent to all task owners

### Option B: Wait for Cron (Automatic)

**Cron Schedule**:
- Runs **daily at 2 AM**
- Auto-creates schedule for next month **on S date**
- For November 2025: Will create on **24 Nov 2025 at 2 AM**

**To trigger manually**:
```bash
# SSH to Odoo server
ssh root@erp.insightpulseai.net

# Run Odoo shell
odoo-bin shell -d production

# Execute cron
>>> env['ppm.monthly.close'].cron_create_monthly_close()
# Should create November 2025 schedule if today is 24 Nov

# Verify
>>> close = env['ppm.monthly.close'].search([('close_month', '=', '2025-11-01')])
>>> print(f"Close: {close.name}")
>>> print(f"Tasks: {len(close.task_ids)}")
>>> print(f"Prep Start: {close.prep_start_date}")
```

---

## Test Workflow (5 minutes)

### As Task Owner (e.g., jtolentino)

1. **Monthly Close → Tasks**
2. Filter: **My Tasks** (owner_code = jtolentino)
3. Open first task: **"Rent & Leases"**

**Workflow Steps**:

**Step 1: Start Preparation**
- Status: **To Do** → Click **Start Prep**
- Status changes to: **In Progress**
- Do your closing work (reconcile, prepare entries, etc.)

**Step 2: Submit for Review**
- When done: Click **Submit for Review**
- Status changes to: **For Review**
- System sets **Prep Completed Date** and **Prep Completed By**
- Notification sent to reviewer (jgtolentino)

### As Reviewer (e.g., jgtolentino)

1. Open task (status: **For Review**)
2. Review the work
3. **Two options**:
   - ✅ **Submit for Approval**: Work is good → Click **Submit for Approval**
   - ❌ **Reject**: Needs corrections → Click **Reject** (returns to owner)

**If Approved**:
- Status changes to: **For Approval**
- System sets **Review Completed Date** and **Review Completed By**
- Notification sent to approver (finance_manager)

### As Approver (e.g., finance_manager)

1. Open task (status: **For Approval**)
2. Final validation
3. **Two options**:
   - ✅ **Approve**: Click **Approve** → Status: **Done**
   - ❌ **Reject**: Click **Reject** (returns to owner)

**If Approved**:
- Status changes to: **Done**
- System sets **Approval Completed Date** and **Approval Completed By**
- Progress bar updates

---

## Monitor Progress

**Dashboard View**: **Monthly Close → Close Schedules**

**Key Metrics**:
- **Total Tasks**: 10
- **Completed Tasks**: Updates as tasks are approved
- **Progress %**: Visual progress bar

**Views Available**:
- **Tree View**: List of all close periods
- **Form View**: Detailed view with task list
- **Calendar View**: See close dates on calendar
- **Gantt View**: Timeline visualization

---

## Complete the Close

**When ALL tasks are done**:

1. Open **FIN CLOSE – November 2025**
2. Verify: **Progress % = 100%**
3. Click **Complete Close** button
4. System validates all tasks are done
5. Status changes to: **Done**

**If tasks are pending**:
- System shows error: *"Cannot complete close. X tasks are still pending"*
- Lists which tasks are incomplete

---

## Run Automated Tests (Optional)

```bash
# SSH to Odoo server
ssh root@erp.insightpulseai.net

# Run module tests
odoo-bin -d production -i ipai_ppm_monthly_close --test-enable --stop-after-init --log-level=test

# Expected output:
# - test_01_november_2025_date_calculations: PASS
# - test_02_task_generation_from_templates: PASS
# - test_03_task_workflow_states: PASS
# - test_04_task_rejection_workflow: PASS
# - test_05_progress_tracking: PASS
# - test_06_complete_close_validation: PASS
# - test_07_business_day_calculations: PASS
# - test_08_multi_agency_support: PASS
# - test_09_template_fields: PASS
# - test_10_cron_create_monthly_close: PASS
```

**All tests should PASS**. If any fail, check logs.

---

## Daily Reminders (Automatic)

**Cron Schedule**: Daily at 8 AM

**Sends notifications for**:
- Tasks in **To Do** on prep_start date (24 Nov)
- Tasks in **For Review** on review_due date (25 Nov)
- Tasks in **For Approval** on approval_due date (25 Nov)

**To trigger manually**:
```bash
odoo-bin shell -d production

>>> env['ppm.close.task'].cron_send_daily_reminders()
# Sends reminders based on today's date
```

---

## n8n Integration (Optional)

**Workflow**: `automations/n8n/workflows/ppm_monthly_close_automation.json`

**Setup**:
```bash
# Import to n8n
curl -X POST "https://ipa.insightpulseai.net/api/v1/workflows" \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  -H "Content-Type: application/json" \
  -d @automations/n8n/workflows/ppm_monthly_close_automation.json

# Activate workflow
# n8n UI → Workflows → "PPM Monthly Close" → Activate
```

**What it does**:
- Triggers daily at 8 AM
- Calls Odoo cron via JSON-RPC
- Sends confirmation to Mattermost channel

---

## Troubleshooting

### Templates Not Found

**Symptom**: "No active task templates found"

**Solution**:
```sql
-- Check templates exist
SELECT COUNT(*) FROM ppm_close_template WHERE active = true;

-- Should return >= 10

-- If 0, reload data:
odoo-bin -d production -i ipai_ppm_monthly_close --stop-after-init
```

### Wrong Dates Calculated

**Symptom**: prep_start_date is not 24 Nov 2025

**Solution**:
```bash
# Verify close_month is set correctly
# Should be 2025-11-01 (first day of month)

# Delete and recreate if needed
```

### Cron Not Running

**Symptom**: Schedule not auto-created

**Solution**:
1. **Settings → Technical → Scheduled Actions**
2. Search: **"Create Next Month's Close Schedule"**
3. Verify: **Active = Yes**
4. Check **Next Execution Date**
5. Click **Run Manually** to test

### No Notifications Sent

**Symptom**: Users not getting notified

**Solution**:
- Check logs: `grep "Notification sent" /var/log/odoo/odoo.log`
- Verify n8n workflow is active
- **TODO**: Email integration (currently only logs notifications)

---

## Next Steps

### After November 2025 Close

1. **Review Results**: Analyze which tasks took longer than expected
2. **Update Templates**: Adjust prep/review/approval days based on actuals
3. **Add Custom Tasks**: Create agency-specific templates as needed
4. **Enable Email Notifications**: Configure Odoo email server
5. **Philippine Holidays**: Integrate with resource.calendar

### For December 2025 Close

**Auto-creation date**: **Monday, 22 Dec 2025** (3 business days before 31 Dec)
- Month End (C): Wednesday, 31 Dec 2025
- Prep Start (S): Monday, 22 Dec 2025 (C - 3 business days, skips weekend)
- Review Due: Tuesday, 23 Dec 2025
- Approval Due: Tuesday, 23 Dec 2025

**Cron will auto-create** on 22 Dec 2025 at 2 AM.

---

## Support

**Issues**: https://github.com/jgtolentino/odoo-ce/issues
**Contact**: jgtolentino_rn@yahoo.com
**Documentation**: `addons/ipai_ppm_monthly_close/README.md`

---

**Last Updated**: 23 Nov 2025
**Module Version**: 1.0.0
**Tested On**: Odoo CE 18.0
