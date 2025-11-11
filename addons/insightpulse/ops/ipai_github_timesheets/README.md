# InsightPulse GitHub Timesheets Integration

**Automate the connection between GitHub development activity and Odoo financial tracking.**

---

## Overview

This module bridges the gap between your **GitHub development factory** and your **Odoo finance system**, enabling complete visibility from strategic OKRs down to individual developer costs and feature ROI.

### Key Features

✅ **GitHub → Odoo Sync**
- Sync GitHub PRs → Odoo project tasks
- Sync GitHub Issues → Odoo project tasks
- Track GitHub Projects with budgets and spend
- Real-time webhook integration

✅ **Automated Timesheet Prompts**
- Post GitHub comments prompting timesheet entry when PR is merged
- Link timesheets to specific PRs and features
- Auto-calculate project costs based on employee rates

✅ **Financial Tracking**
- Track project budget vs. actual spend
- CapEx vs. OpEx expense classification
- Budget utilization monitoring
- Sync cost data back to GitHub Projects API

✅ **CFO Dashboards**
- Project burn rate analysis
- CapEx/OpEx split reporting
- Feature ROI calculation
- Developer productivity metrics

---

## Installation

### Prerequisites

```bash
# Install Python dependencies
pip install requests PyGithub
```

### Install Module

1. Copy module to Odoo addons path: `addons/insightpulse/ops/ipai_github_timesheets/`
2. Update app list: `Odoo → Apps → Update Apps List`
3. Search for "InsightPulse GitHub Timesheets"
4. Click **Install**

---

## Configuration

### 1. GitHub API Setup

**Generate Personal Access Token:**

1. Go to [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Required scopes:
   - `repo` (Full control of private repositories)
   - `project` (Full control of projects)
   - `read:org` (Read org and team membership)
   - `read:user` (Read user profile data)
4. Copy the generated token (starts with `ghp_` or `github_pat_`)

**Configure in Odoo:**

1. Navigate to: `GitHub → Configuration`
2. Fill in:
   - **Name**: GitHub API Config
   - **GitHub Organization**: `jgtolentino` (your org name)
   - **Default Repository**: `insightpulse-odoo`
   - **GitHub Personal Access Token**: (paste token)
   - **Webhook Secret**: (generate a random string for security)
3. Enable sync options:
   - ☑ Sync Pull Requests
   - ☑ Sync Issues
   - ☑ Sync GitHub Projects
   - ☑ Auto-Create Tasks
   - ☑ Prompt Timesheet on PR Merge
   - ☑ Sync Costs to GitHub
4. Click **Test Connection** to verify
5. Click **Sync Now** to perform initial sync

### 2. GitHub Webhook Setup

**Configure webhook in GitHub:**

1. Go to your GitHub repository: `Settings → Webhooks → Add webhook`
2. Configure:
   - **Payload URL**: `https://your-odoo-domain.com/github/webhook`
   - **Content type**: `application/json`
   - **Secret**: (same as configured in Odoo)
   - **SSL verification**: Enable SSL verification
   - **Events**: Select individual events:
     - ☑ Pull requests
     - ☑ Issues
     - ☑ Projects
   - **Active**: ☑ Active
3. Click **Add webhook**
4. Test by creating a test PR

### 3. Employee Rate Configuration

**Set hourly rates for employees:**

1. Navigate to: `Employees → Employees → [Select Employee]`
2. Go to **HR Settings** tab
3. Set **Hourly Cost** (e.g., $75/hour)
4. This rate will be used for timesheet cost calculations

### 4. GitHub Projects Setup

**Create GitHub Projects with financial fields:**

1. In GitHub, go to your org: `Projects → New project`
2. Create custom fields:
   - **Project Budget ($)** - Number field
   - **Project Spend ($)** - Number field
   - **Expense Type** - Single select: `R&D (OpEx)`, `Capitalizable Feature (CapEx)`, `Maintenance (OpEx)`
   - **Odoo Project ID** - Text field (for linking)
3. Sync to Odoo: `GitHub → GitHub Projects → Create` or wait for webhook

---

## Usage

### Workflow: PR → Task → Timesheet → Cost

**1. Developer Creates PR**
```bash
# Developer creates PR in GitHub
git checkout -b feature/new-dashboard
git commit -m "feat: add CFO dashboard"
git push origin feature/new-dashboard
# Opens PR on GitHub
```

**2. Webhook Creates Task in Odoo**
- Webhook triggers automatically
- Odoo creates task: `PR #123: Add CFO dashboard`
- Task is linked to GitHub Project
- Assigned to developer (auto-mapped by GitHub username)

**3. PR is Merged**
```bash
# PR is reviewed and merged
# Webhook updates task state
```

**4. Automated Timesheet Prompt**
- Odoo posts GitHub comment:
  ```
  ## 📝 Timesheet Reminder

  Hi @developer! This PR has been merged. Please log your time in Odoo:

  **Odoo Task**: https://your-odoo.com/web#id=456&model=project.task

  **Instructions**:
  1. Navigate to the Odoo task above
  2. Click "Timesheets" tab
  3. Log your hours spent on this PR
  ```

**5. Developer Logs Time**
- Developer opens Odoo task
- Clicks **Timesheets** tab
- Adds entry:
  - **Date**: 2025-01-15
  - **Hours**: 8.5
  - **Description**: "Implemented CFO dashboard with burn rate charts"
- Cost auto-calculates: `8.5 hours × $75/hour = $637.50`

**6. Project Budget Tracking**
- Project spend updates automatically
- Budget utilization: `$12,500 / $50,000 = 25%`
- Remaining budget: `$37,500`

**7. Sync Back to GitHub (Optional)**
- Click **Sync Cost to GitHub** button
- Updates GitHub Project "Project Spend ($)" field
- Visible in GitHub Projects board

---

## Financial Reporting

### CapEx vs OpEx Classification

**Expense Types:**

| Type | Description | Accounting Treatment |
|------|-------------|---------------------|
| **R&D (OpEx)** | Research and experimental features | Immediate expense |
| **Capitalizable Feature (CapEx)** | Production-ready features that add value | Capitalize as asset |
| **Maintenance (OpEx)** | Bug fixes, performance improvements | Immediate expense |
| **Bug Fix (OpEx)** | Bug fixes | Immediate expense |

**Classification Rules:**

- New features with revenue impact → **CapEx**
- Exploratory/research work → **OpEx (R&D)**
- Bug fixes → **OpEx (Bug Fix)**
- Refactoring → **OpEx (Maintenance)**

**CFO Dashboard Queries:**

See [Superset CFO Dashboard SQL](../../../docs/superset/github-financial-dashboards.md) for ready-to-use queries.

---

## Superset Integration

### CFO Dashboard Charts

**1. Project Burn Rate**
```sql
SELECT
  gp.title AS project_name,
  gp.project_budget,
  gp.project_spend,
  gp.remaining_budget,
  gp.budget_utilization_pct
FROM github_project gp
WHERE gp.github_state = 'open'
ORDER BY gp.budget_utilization_pct DESC;
```

**2. CapEx vs OpEx Split**
```sql
SELECT
  gp.expense_type,
  SUM(gp.project_spend) AS total_cost,
  COUNT(DISTINCT gp.id) AS project_count
FROM github_project gp
GROUP BY gp.expense_type;
```

**3. Feature ROI** (if tracking revenue)
```sql
SELECT
  gp.title AS feature_name,
  gp.project_spend AS development_cost,
  COALESCE(SUM(sol.price_subtotal), 0) AS revenue_generated,
  COALESCE(SUM(sol.price_subtotal), 0) - gp.project_spend AS net_roi
FROM github_project gp
LEFT JOIN sale_order_line sol ON sol.name ILIKE '%' || gp.title || '%'
GROUP BY gp.title, gp.project_spend
ORDER BY net_roi DESC;
```

---

## API Reference

### Webhook Endpoint

**URL**: `/github/webhook`

**Method**: POST

**Authentication**: HMAC-SHA256 signature verification

**Headers**:
```
X-GitHub-Event: pull_request | issues | project
X-Hub-Signature-256: sha256=<hmac>
X-GitHub-Delivery: <uuid>
```

**Payload**: GitHub webhook JSON

**Response**:
```json
{
  "status": "success",
  "pr_number": 123,
  "action": "closed"
}
```

---

## Troubleshooting

### Webhook Not Triggering

**Check webhook delivery:**
1. Go to GitHub: `Settings → Webhooks → [Your webhook]`
2. Click **Recent Deliveries**
3. Check response code:
   - `200` = Success
   - `401` = Invalid signature (check webhook secret)
   - `500` = Odoo error (check logs)

**Check Odoo logs:**
```bash
# View Odoo logs
tail -f /var/log/odoo/odoo.log | grep github
```

### Timesheet Costs Not Calculating

**Verify employee hourly rate:**
```python
# In Odoo shell
employee = env['hr.employee'].search([('name', '=', 'John Doe')])
print(employee.hourly_cost)  # Should return a number, not 0.0
```

**Check timesheet entries:**
```python
# In Odoo shell
timesheets = env['account.analytic.line'].search([('github_pr_id', '!=', False)])
for ts in timesheets:
    print(f"{ts.employee_id.name}: {ts.unit_amount}h × {ts.employee_id.hourly_cost}/h = {ts.amount}")
```

### GitHub API Rate Limits

**Check rate limit:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.github.com/rate_limit
```

**Response:**
```json
{
  "rate": {
    "limit": 5000,
    "remaining": 4999,
    "reset": 1672531200
  }
}
```

**Solutions:**
- Use authenticated requests (increases limit from 60 to 5000/hour)
- Implement caching for repeated requests
- Use conditional requests with `If-None-Match`

---

## Development

### Running Tests

```bash
# Run module tests
python -m pytest addons/insightpulse/ops/ipai_github_timesheets/tests/ -v

# Or with Odoo test framework
odoo -c odoo.conf -d test_db -i ipai_github_timesheets --test-enable --stop-after-init
```

### Extending the Module

**Add custom fields to GitHub Project:**

```python
# models/github_project.py
custom_field = fields.Char(string="Custom Field")
```

**Add custom webhook handler:**

```python
# controllers/webhook.py
def _handle_custom_event(self, payload, config):
    # Your custom logic here
    pass
```

---

## Roadmap

- [ ] **Phase 1**: Core PR/Issue sync (✅ Complete)
- [ ] **Phase 2**: Financial tracking (✅ Complete)
- [ ] **Phase 3**: Superset dashboards (🔄 In Progress)
- [ ] **Phase 4**: GitHub Actions integration (📋 Planned)
- [ ] **Phase 5**: AI-powered time estimation (📋 Planned)
- [ ] **Phase 6**: Multi-repo support (📋 Planned)

---

## Support

- **Issues**: [GitHub Issues](https://github.com/jgtolentino/insightpulse-odoo/issues)
- **Documentation**: [Full Docs](https://github.com/jgtolentino/insightpulse-odoo/tree/main/docs)
- **Email**: support@insightpulseai.net

---

## License

LGPL-3.0 - See [LICENSE](../../LICENSE) for details

---

## Credits

**Author**: InsightPulse AI Platform Team
**Maintainer**: InsightPulse AI
**Version**: 19.0.1.0.0
**Odoo Version**: 19.0 CE
