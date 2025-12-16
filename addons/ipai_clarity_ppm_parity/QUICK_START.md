# Clarity PPM Parity - Quick Start Guide

**5-Minute Installation & Verification**

---

## Prerequisites

✅ Odoo 18.0 Community Edition installed
✅ Git access to https://github.com/OCA/project
✅ Database with demo data (recommended for first install)

---

## Installation (3 Steps)

### Step 1: Clone OCA Repository

```bash
# Create OCA addons directory
sudo mkdir -p /opt/odoo/oca-addons

# Clone OCA project repository (Odoo 18.0 branch)
sudo git clone https://github.com/OCA/project.git -b 18.0 /opt/odoo/oca-addons/project
```

### Step 2: Update Odoo Configuration

```bash
# Backup current config
sudo cp /etc/odoo/odoo.conf /etc/odoo/odoo.conf.backup.$(date +%Y%m%d)

# Add OCA path to addons_path
sudo nano /etc/odoo/odoo.conf
```

**Add OCA path**:
```ini
[options]
addons_path = /opt/odoo/addons,/opt/odoo/oca-addons/project,/opt/odoo/custom-addons
```

**Restart Odoo**:
```bash
sudo systemctl restart odoo
```

### Step 3: Install Modules

**Via Odoo UI** (Recommended):
1. Apps → Update Apps List
2. Remove "Apps" filter to see all modules
3. Install in this exact order:
   - `project_key` - Unique project codes
   - `project_category` - Portfolios/programs
   - `project_wbs` - Work Breakdown Structure
   - `project_parent_task_filter` - Parent/child management
   - `project_milestone` - Milestone entity
   - `project_task_milestone` - Task-milestone linking
   - `project_task_dependency` - Task dependencies
   - `project_task_checklist` - To-Do items
   - `project_timeline` - Gantt chart
4. Install `InsightPulse Clarity PPM Parity`

**Via CLI** (Advanced):
```bash
cd /opt/odoo
./odoo-bin -d production \
  -i project_key,project_category,project_wbs,project_parent_task_filter,\
project_milestone,project_task_milestone,project_task_dependency,\
project_task_checklist,project_timeline,ipai_clarity_ppm_parity \
  --stop-after-init
```

---

## Verification (2 Minutes)

### Quick Visual Check

1. **Go to Project → Projects**
2. **Find "ERP Implementation Q1 2025"** (PRJ-2025-001)
3. **Open project form**

**✅ Should see**:
- Clarity ID field: `PRJ-2025-001`
- Health Status: Green badge
- Stat buttons: Phases (6), Milestones (4), Health
- New tabs: "Baseline & Variance", "Phases", "Milestones"

### Database Verification

```sql
-- Connect to database
psql -U odoo -d production

-- Check projects loaded
SELECT id, name, clarity_id, health_status, phase_count, milestone_count
FROM project_project
WHERE clarity_id IN ('PRJ-2025-001', 'PRJ-2025-002');
-- Expected: 2 rows

-- Check phases loaded
SELECT COUNT(*) as phase_count
FROM project_task
WHERE is_phase = true;
-- Expected: 8

-- Check milestones loaded
SELECT COUNT(*) as milestone_count
FROM project_milestone;
-- Expected: 6

-- Check tasks loaded
SELECT COUNT(*) as task_count
FROM project_task
WHERE is_phase = false;
-- Expected: 11

-- Check to-do items loaded
SELECT COUNT(*) as todo_count
FROM project_task_checklist_item;
-- Expected: 13
```

---

## First Test: Create Project

### 1. Create New Project

**Project → Configuration → Projects → Create**

```yaml
Name: "Mobile App Development 2025"
Clarity ID: "PRJ-2025-003"
Portfolio: "IT Infrastructure" (or create new)
Health Status: Green
Overall Status: On Track
Baseline Start: 2025-02-01
Baseline Finish: 2025-06-30
```

**Save**

### 2. Add Phase

**Phases tab → Add a line**

```yaml
Name: "Planning Phase"
Is Phase: ✓ (checkbox)
Phase Type: Planning
Has Phase Gate: ✓
Date Deadline: 2025-02-28
Gate Decision: Pending
```

**Save**

### 3. Add Milestone

**Milestones tab → Create**

```yaml
Name: "Planning Gate Approval"
Milestone Type: Phase Gate
Project: Mobile App Development 2025
Deadline: 2025-02-28
Approval Required: ✓
Approver: [Select user]
Completion Criteria: "Requirements approved, charter signed"
Alert Days Before: 7
```

**Save**

### 4. Add Task

**Tasks tab → Create**

```yaml
Name: "Gather Requirements"
Parent Task: Planning Phase
Milestone: Planning Gate Approval
Planned Hours: 40
Planned Value: 20000
Date Deadline: 2025-02-15
```

**Save**

### 5. Add To-Do Item

**Open task "Gather Requirements" → Checklist tab → Add**

```yaml
Name: "Interview stakeholders"
Assigned To: [Select user]
Due Date: 2025-02-05
Priority: High
Estimated Hours: 8
```

**Save**

---

## Expected Results

### Project Form

**Header**:
- Clarity ID: PRJ-2025-003
- Health Status: 🟢 Green
- Overall Status: On Track

**Stat Buttons**:
- Phases: 1
- Milestones: 1
- Health: 🟢

**Baseline & Variance Tab**:
```
Baseline Start: 2025-02-01
Baseline Finish: 2025-06-30
Actual Start: (empty)
Actual Finish: (empty)
Start Variance: 0 days
Finish Variance: 0 days
Overall Progress: 0%
Phase Count: 1
Milestone Count: 1
```

**Phases Tab**:
| Name | Phase Type | Progress | Child Tasks | Milestones | Deadline | Status |
|------|-----------|----------|-------------|------------|----------|--------|
| Planning Phase | Planning | 0% | 1 | 0 | 2025-02-28 | Not Started |

---

## Common Issues

### Issue 1: Modules Not Appearing in Apps List

**Solution**:
```bash
# Update apps list
# Apps → Update Apps List button

# Remove "Apps" filter
# Clear the "Apps" filter in search bar to see all modules
```

### Issue 2: Installation Order Matters

**Error**: `Module project_task_milestone depends on project_milestone which is not installed`

**Solution**: Install dependencies in the exact order specified:
1. project_key
2. project_category
3. project_wbs
4. project_parent_task_filter
5. project_milestone ⬅️ Install this BEFORE project_task_milestone
6. project_task_milestone
7. project_task_dependency
8. project_task_checklist
9. project_timeline

### Issue 3: Seed Data Not Loading

**Check**:
```sql
-- Verify data loaded
SELECT COUNT(*) FROM project_project WHERE clarity_id LIKE 'PRJ-%';
```

**If 0 rows**: Data file may have been skipped

**Solution**: Manually load seed data:
```bash
# Upgrade module to force data reload
./odoo-bin -d production -u ipai_clarity_ppm_parity --stop-after-init
```

### Issue 4: "Clarity ID" Field Not Visible

**Check**: Module installed?
```bash
# Via Odoo UI
# Apps → Search "Clarity PPM" → Should show "Installed"
```

**Solution**: Clear cache and refresh browser:
- Ctrl+Shift+R (hard refresh)
- Or restart Odoo: `sudo systemctl restart odoo`

---

## Next Steps

### Explore Seed Data

**Project 1**: ERP Implementation Q1 2025 (PRJ-2025-001)
- 6 Phases: Planning → Design → Implementation → Testing → Deployment → Closeout
- 4 Milestones with phase gates
- 8 Tasks across phases
- 10 To-Do items

**Project 2**: Finance PPM & BIR Compliance Q4 2025 (PRJ-2025-002)
- 2 Phases: Month-End Closing, Tax Filing
- 2 BIR Milestones (1601-C, 2550Q)
- 3 BIR Tasks (Prep → Review → Approval)
- 3 To-Do items

### Test Workflows

1. **Phase Gate Approval**:
   - Complete all tasks in Planning phase
   - Approve Planning Gate milestone
   - Approve phase gate decision (Go)
   - Proceed to Design phase

2. **Variance Tracking**:
   - Set baseline dates
   - Set actual start date (different from baseline)
   - Observe variance calculation in days

3. **Milestone Alerts**:
   - Create milestone with alert 7 days before
   - Wait for cron job (runs daily at 8 AM)
   - Check project chatter for alert message

4. **Critical Path Analysis**:
   - Create task chain with dependencies
   - Observe which tasks have zero float
   - These are on critical path

---

## Documentation

- **README.rst** - OCA-compliant documentation
- **IMPLEMENTATION_SUMMARY.md** - Complete implementation guide
- **TEST_REPORT.md** - Syntax validation results
- **SKILL.md** (in `/skills/odoo/clarity-ppm-parity/`) - Comprehensive skill guide

---

## Support

**Issues**: Report at module repository or Odoo community forums

**Known Limitations**:
- Critical path uses simplified algorithm (not full CPM)
- Earned Value metrics require manual cost input
- Resource leveling not implemented

---

**Installation Time**: ~10 minutes (including OCA modules)
**First Test**: ~5 minutes
**Total**: ~15 minutes to working Clarity PPM environment

✅ **Ready to go!**
