# BIR Compliance Dashboard Example

Complete walkthrough for creating a BIR filing status dashboard for Philippine tax compliance.

## Overview

**Purpose**: Track monthly BIR filing compliance across multiple agencies (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB)

**Forms Tracked**:
- Form 1601-C (Monthly withholding tax)
- Form 2550Q (Quarterly VAT)
- Form 1702-RT (Annual income tax)
- ATP (Authorization to Print) expiry dates

**Refresh**: Daily at 6:00 AM Manila time

## Step 1: Create Dataset

### SQL Query
```sql
CREATE OR REPLACE VIEW superset_bir_compliance AS
SELECT 
  -- Agency identification
  a.code as agency_code,
  a.name as agency_name,
  
  -- Form details
  b.form_type,
  b.period_month,
  b.period_year,
  b.filing_deadline,
  b.date_filed,
  
  -- Amounts
  b.tax_withheld,
  b.vat_payable,
  b.penalties,
  
  -- Status
  CASE 
    WHEN b.status = 'Filed' AND b.date_filed <= b.filing_deadline 
      THEN 'On Time'
    WHEN b.status = 'Filed' AND b.date_filed > b.filing_deadline 
      THEN 'Late'
    WHEN b.status != 'Filed' AND CURRENT_DATE > b.filing_deadline 
      THEN 'Overdue'
    WHEN b.status != 'Filed' 
      THEN 'Pending'
    ELSE 'Unknown'
  END as compliance_status,
  
  -- Days until deadline
  CASE 
    WHEN b.status != 'Filed' 
      THEN (b.filing_deadline - CURRENT_DATE)
    ELSE NULL
  END as days_until_deadline,
  
  -- ATP tracking
  atp.expiry_date as atp_expiry,
  CASE 
    WHEN atp.expiry_date < CURRENT_DATE + INTERVAL '30 days' 
      THEN 'Expiring Soon'
    WHEN atp.expiry_date < CURRENT_DATE 
      THEN 'Expired'
    ELSE 'Valid'
  END as atp_status

FROM agencies a
LEFT JOIN bir_filings b ON a.id = b.agency_id
LEFT JOIN bir_atp atp ON a.id = atp.agency_id
WHERE b.period_year >= EXTRACT(YEAR FROM CURRENT_DATE) - 1
ORDER BY b.filing_deadline DESC, a.code;
```

### Dataset Configuration

**In Superset UI:**
1. Go to **Data** > **Datasets** > **+ Dataset**
2. Select database: `Supabase Production`
3. Choose: **SQL**
4. Paste the SQL above
5. Dataset name: `BIR Compliance Tracker`
6. Click **Save**

**Configure Columns:**
- `agency_code`: String, dimension
- `agency_name`: String, dimension
- `form_type`: String, dimension
- `period_month`: Temporal, dimension
- `period_year`: Integer, dimension
- `filing_deadline`: Date, dimension
- `date_filed`: Date, dimension
- `tax_withheld`: Numeric, metric (SUM)
- `vat_payable`: Numeric, metric (SUM)
- `penalties`: Numeric, metric (SUM)
- `compliance_status`: String, dimension
- `days_until_deadline`: Integer, metric (AVG)
- `atp_status`: String, dimension

## Step 2: Create Charts

### Chart 1: Monthly Filing Status (Pivot Table)

**Type**: Pivot Table v2

**Configuration:**
```json
{
  "datasource": "BIR Compliance Tracker",
  "viz_type": "pivot_table_v2",
  "groupby": ["agency_code", "form_type"],
  "columns": ["period_month"],
  "metrics": [
    {
      "label": "Total Withheld",
      "expressionType": "SIMPLE",
      "column": {"column_name": "tax_withheld"},
      "aggregate": "SUM"
    }
  ],
  "row_limit": 10000,
  "conditional_formatting": [
    {
      "column": "compliance_status",
      "operator": "==",
      "value": "Overdue",
      "colorScheme": "#ff4444"
    },
    {
      "column": "compliance_status",
      "operator": "==",
      "value": "On Time",
      "colorScheme": "#44ff44"
    }
  ]
}
```

**Why this chart**: Shows at-a-glance status for all agencies and forms.

### Chart 2: Tax Withheld Trend (Timeseries)

**Type**: ECharts Timeseries

**Configuration:**
```json
{
  "datasource": "BIR Compliance Tracker",
  "viz_type": "echarts_timeseries_bar",
  "x_axis": "filing_deadline",
  "metrics": [
    {
      "label": "1601-C Tax Withheld",
      "expressionType": "SQL",
      "sqlExpression": "SUM(CASE WHEN form_type = '1601-C' THEN tax_withheld ELSE 0 END)"
    },
    {
      "label": "2550Q VAT Payable",
      "expressionType": "SQL",
      "sqlExpression": "SUM(CASE WHEN form_type = '2550Q' THEN vat_payable ELSE 0 END)"
    }
  ],
  "groupby": ["period_month"],
  "time_grain_sqla": "P1M",
  "color_scheme": "supersetColors"
}
```

**Why this chart**: Visualizes tax liability trends over time.

### Chart 3: Overdue Filings (Big Number)

**Type**: Big Number Total

**Configuration:**
```json
{
  "datasource": "BIR Compliance Tracker",
  "viz_type": "big_number_total",
  "metric": {
    "label": "Overdue Filings",
    "expressionType": "SQL",
    "sqlExpression": "COUNT(CASE WHEN compliance_status = 'Overdue' THEN 1 END)"
  },
  "y_axis_format": "SMART_NUMBER",
  "header_font_size": 0.3,
  "subheader": "Requires immediate attention",
  "subheader_font_size": 0.15
}
```

**Why this chart**: Highlights urgent action items.

### Chart 4: ATP Expiry Calendar (Table)

**Type**: Table

**Configuration:**
```json
{
  "datasource": "BIR Compliance Tracker",
  "viz_type": "table",
  "groupby": ["agency_code", "atp_expiry", "atp_status"],
  "all_columns": [],
  "order_by_cols": ["[\"atp_expiry\", true]"],
  "row_limit": 50,
  "conditional_formatting": [
    {
      "column": "atp_status",
      "operator": "==",
      "value": "Expired",
      "colorScheme": "#ff0000"
    },
    {
      "column": "atp_status",
      "operator": "==",
      "value": "Expiring Soon",
      "colorScheme": "#ffaa00"
    }
  ]
}
```

**Why this chart**: Ensures ATP renewals don't slip through.

### Chart 5: Compliance by Agency (Bar Chart)

**Type**: ECharts Bar

**Configuration:**
```json
{
  "datasource": "BIR Compliance Tracker",
  "viz_type": "echarts_bar",
  "x_axis": "agency_code",
  "metrics": [
    {
      "label": "On Time %",
      "expressionType": "SQL",
      "sqlExpression": "100.0 * COUNT(CASE WHEN compliance_status = 'On Time' THEN 1 END) / COUNT(*)"
    }
  ],
  "y_axis_format": ".1f",
  "color_scheme": "supersetColors",
  "show_legend": false,
  "rich_tooltip": true
}
```

**Why this chart**: Compare agency performance.

## Step 3: Assemble Dashboard

### Layout Structure

```
┌─────────────────────────────────────────────────────────┐
│  BIR Compliance Dashboard                     [Filters] │
├─────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌──────────┐  ┌──────────┐ │
│  │Overdue  │  │Pending  │  │Total Tax │  │Penalties │ │
│  │   3     │  │   5     │  │  ₱2.5M   │  │  ₱15K    │ │
│  └─────────┘  └─────────┘  └──────────┘  └──────────┘ │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐│
│  │                                                      ││
│  │     Monthly Filing Status (Pivot Table)             ││
│  │                                                      ││
│  └─────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────────────┐  ┌─────────────────────┐ │
│  │                           │  │                     │ │
│  │  Tax Withheld Trend       │  │  Compliance by      │ │
│  │  (Timeseries)             │  │  Agency (Bar)       │ │
│  │                           │  │                     │ │
│  └──────────────────────────┘  └─────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐│
│  │                                                      ││
│  │     ATP Expiry Calendar (Table)                     ││
│  │                                                      ││
│  └─────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

### Dashboard Filters

Add these global filters:

1. **Agency** - Multi-select dropdown
   - Column: `agency_code`
   - Default: All agencies

2. **Period** - Date range
   - Column: `filing_deadline`
   - Default: Last 12 months

3. **Form Type** - Multi-select dropdown
   - Column: `form_type`
   - Options: 1601-C, 2550Q, 1702-RT

4. **Status** - Multi-select dropdown
   - Column: `compliance_status`
   - Default: All statuses

## Step 4: Configure Refresh

**In Dashboard Settings:**
```json
{
  "refresh_frequency": {
    "schedule": "0 6 * * *",
    "timezone": "Asia/Manila",
    "type": "cron"
  },
  "cache_timeout": 3600
}
```

## Step 5: Set Permissions

### Row-Level Security (Supabase)

```sql
-- Create RLS policy for agency-specific access
CREATE POLICY agency_data_access ON bir_filings
FOR SELECT
USING (
  agency_id IN (
    SELECT agency_id 
    FROM user_agency_access 
    WHERE user_email = current_setting('request.jwt.claims')::json->>'email'
  )
);

-- Enable RLS
ALTER TABLE bir_filings ENABLE ROW LEVEL SECURITY;
```

### Superset Role Configuration

1. **Admin**: Full access to all agencies
2. **Finance Manager**: Read-only access to all agencies
3. **Agency User**: Read-only access to their agency only

## Success Metrics

**Before (Manual Excel Reports):**
- ⏱️ Report creation: 2 hours
- 📅 Update frequency: Monthly
- 📧 Distribution: Email attachments
- 🔍 Visibility: Last month only

**After (Superset Dashboard):**
- ⏱️ Report creation: Automated
- 📅 Update frequency: Daily (6 AM)
- 🌐 Distribution: Real-time web access
- 🔍 Visibility: Rolling 12 months

## Maintenance

### Weekly
- [ ] Review overdue filings
- [ ] Check ATP expiry status
- [ ] Verify data refresh logs

### Monthly
- [ ] Reconcile with BIR filing receipts
- [ ] Update dataset if new agencies added
- [ ] Review and optimize slow queries

### Quarterly
- [ ] Generate compliance report for management
- [ ] Update ATP renewal tracking
- [ ] Review access permissions

## Next Steps

1. ✅ Deploy dashboard to production
2. ✅ Train users on filters and drill-downs
3. ✅ Set up email alerts for overdue filings
4. ✅ Create mobile-optimized version
5. ✅ Integrate with Notion for task tracking

## Related Dashboards

- **Tax Payment Tracking**: Monitor payment vs filing
- **Penalty Analysis**: Track causes of late filings
- **Agency Performance**: Compare compliance scores
- **Year-End Summary**: Annual BIR compliance report

---

**Your BIR compliance is now fully automated!** 🎯
