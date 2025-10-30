# InsightPulse Rate Policy Automation

**Version**: 19.0.1.0.0
**Author**: InsightPulse AI
**License**: LGPL-3

## Overview

This module provides automated rate calculation functionality based on P60 base rates with configurable markup percentages (default: 25%).

## Features

- **Rate Policies**: Define and manage rate calculation policies
- **Policy Lines**: Associate job positions with P60 base rates
- **Automatic Calculation**: Computed fields automatically calculate rates with markup
- **Calculation Logs**: Audit trail for all rate calculations
- **State Management**: Draft → Active → Archived workflow
- **Multi-Company**: Full multi-company support

## Odoo Studio Compatibility

**Studio Support**: ✅ Full customization support

**Safe to Customize**:
- Add custom fields (client references, notes, tags)
- Create custom views (kanban, graph, pivot)
- Add automated actions (notifications, webhooks)
- Custom PDF reports

**Recommended Automations**:
- Email notifications when policy activated
- Webhook to external systems on rate changes
- Scheduled policy effectiveness reminders
- Rate variance alerts

**Protected Fields** (DO NOT modify):
- `calculated_rate` (computed field)
- `markup_percentage` calculation logic
- State transition methods

See [docs/STUDIO_GUIDE.md](../../../../docs/STUDIO_GUIDE.md) for detailed customization patterns.

## Models

### rate.policy
Core model for defining rate calculation policies.

**Fields**:
- `name`: Policy name
- `markup_percentage`: Markup % to apply (default: 25%)
- `effective_date`: When policy becomes active
- `state`: draft/active/archived
- `line_ids`: One2many to rate policy lines

**Methods**:
- `calculate_rate(p60_rate, markup_percentage)`: Calculate rate with markup
- `action_activate()`: Activate policy
- `action_archive_policy()`: Archive policy

### rate.policy.line
Individual rate calculations for specific job positions.

**Fields**:
- `policy_id`: Parent rate policy
- `role_id`: Job position (hr.job)
- `p60_base_rate`: Base P60 rate
- `calculated_rate`: Computed rate with markup

### rate.calculation.log
Audit log for rate calculations.

**Fields**:
- `policy_id`: Rate policy used
- `role_id`: Job position
- `p60_rate`: Base rate
- `markup_percentage`: Markup applied
- `calculated_rate`: Final calculated rate
- `calculation_date`: When calculation was performed
- `user_id`: Who performed the calculation

## Usage

### Creating a Rate Policy

1. Navigate to **Accounting > Rate Policies > Policies**
2. Click **Create**
3. Enter policy name and effective date
4. Set markup percentage (default: 25%)
5. Add rate lines for each job position
6. Click **Activate** to enable the policy

### Adding Rate Lines

1. Open an existing rate policy
2. Go to **Rate Lines** tab
3. Select a job position
4. Enter P60 base rate
5. The calculated rate will be computed automatically

### Viewing Calculation Logs

1. Navigate to **Accounting > Rate Policies > Calculation Logs**
2. Filter by date, policy, or job position
3. View audit trail of all calculations

## Security Groups

- **Rate Policy User**: Read-only access to policies and logs
- **Rate Policy Manager**: Full CRUD access to policies and lines

## Dependencies

- `ipai_core`: InsightPulse core module
- `hr`: Odoo HR module (for job positions)
- `account`: Odoo Accounting module

## Technical Details

### Computed Fields

The `calculated_rate` field on `rate.policy.line` is computed based on:
```python
calculated_rate = p60_base_rate * (1 + (markup_percentage / 100))
```

### State Workflow

```
draft → active → archived
```

### Data Flow

```
Job Position (hr.job)
    ↓
Rate Policy Line (p60_base_rate + markup)
    ↓
Calculated Rate (computed field)
    ↓
Rate Calculation Log (audit trail)
```

## Configuration

No additional configuration required after installation. Default markup is set to 25% but can be customized per policy.

## Known Issues

None at this time.

## Roadmap

- [ ] Bulk rate import from CSV
- [ ] Rate comparison reports
- [ ] Historical rate tracking
- [ ] Multi-currency rate conversion
- [ ] Rate approval workflows

## Support

For support, please contact InsightPulse AI support team.
