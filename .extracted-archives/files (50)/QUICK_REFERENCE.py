# SAP FIORI DESIGN SYSTEM - QUICK REFERENCE CARD
# InsightPulse AI | Finance Shared Service Center

"""
┌─────────────────────────────────────────────────────────────────┐
│                    SUPERSET SAP DESIGN SYSTEM                   │
│                         QUICK REFERENCE                         │
└─────────────────────────────────────────────────────────────────┘
"""

# ============================================================================
# CORE COLORS (Copy-Paste Ready)
# ============================================================================

PRIMARY_COLORS = {
    'SAP Blue':        '#0a6ed1',  # Primary actions, links, highlights
    'SAP Dark Blue':   '#0854a0',  # Hover states, dark mode
    'SAP Light Blue':  '#ebf5fb',  # Backgrounds, subtle highlights
}

SEMANTIC_COLORS = {
    'Success':         '#107e3e',  # Approved, Compliant, Positive
    'Warning':         '#e9730c',  # Pending, Review Required
    'Error':           '#bb0000',  # Rejected, Violation, Critical
    'Info':            '#0a6ed1',  # Information, Neutral
    'Neutral':         '#6a6d70',  # Gray, Disabled states
}

AGENCY_COLORS = {
    'RIM':   '#0a6ed1',  # SAP Blue
    'CKVC':  '#5d36b8',  # Purple
    'BOM':   '#c0399f',  # Magenta
    'JPAL':  '#107e3e',  # Green
    'JLI':   '#2b7c2e',  # Dark Green
    'JAP':   '#e9730c',  # Orange
    'LAS':   '#d17a00',  # Dark Orange
    'RMQB':  '#5d36b8',  # Purple
}

EXPENSE_COLORS = {
    'Airfare':          '#0a6ed1',  # Blue
    'Hotel':            '#107e3e',  # Green
    'Meals':            '#e9730c',  # Orange
    'Ground Transport': '#5d36b8',  # Purple
    'Car Rental':       '#c0399f',  # Magenta
    'Fuel':             '#d17a00',  # Dark Orange
    'Parking':          '#2b7c2e',  # Dark Green
}

# ============================================================================
# CSS CLASSES (Ready to Use in SQL)
# ============================================================================

STATUS_BADGES = """
-- Expense Report Status
CASE status
    WHEN 'draft'     THEN '<span class="expense-status draft">Draft</span>'
    WHEN 'submitted' THEN '<span class="expense-status submitted">Submitted</span>'
    WHEN 'approved'  THEN '<span class="expense-status approved">Approved</span>'
    WHEN 'rejected'  THEN '<span class="expense-status rejected">Rejected</span>'
    WHEN 'paid'      THEN '<span class="expense-status paid">Paid</span>'
END as status_badge
"""

POLICY_BADGES = """
-- Policy Compliance
CASE 
    WHEN policy_compliant THEN '<span class="policy-badge compliant">Compliant</span>'
    WHEN has_warning      THEN '<span class="policy-badge warning">Warning</span>'
    ELSE                      '<span class="policy-badge violation">Violation</span>'
END as compliance_badge
"""

AGENCY_BADGES = """
-- Agency Indicator
CASE agency_code
    WHEN 'RIM'  THEN '<span class="agency-indicator rim">RIM</span>'
    WHEN 'CKVC' THEN '<span class="agency-indicator ckvc">CKVC</span>'
    WHEN 'BOM'  THEN '<span class="agency-indicator bom">BOM</span>'
    WHEN 'JPAL' THEN '<span class="agency-indicator jpal">JPAL</span>'
    WHEN 'JLI'  THEN '<span class="agency-indicator jli">JLI</span>'
    WHEN 'JAP'  THEN '<span class="agency-indicator jap">JAP</span>'
    WHEN 'LAS'  THEN '<span class="agency-indicator las">LAS</span>'
    WHEN 'RMQB' THEN '<span class="agency-indicator rmqb">RMQB</span>'
END as agency_badge
"""

BIR_BADGES = """
-- BIR Compliance Status
CASE 
    WHEN filing_date <= due_date 
        THEN '<span class="bir-compliance compliant">Compliant</span>'
    WHEN filing_date IS NULL AND due_date < CURRENT_DATE 
        THEN '<span class="bir-compliance overdue">Overdue</span>'
    ELSE '<span class="bir-compliance pending">Pending</span>'
END as bir_status
"""

# ============================================================================
# COMMON SQL PATTERNS
# ============================================================================

KPI_WITH_TREND = """
-- KPI Card with Month-over-Month Trend
SELECT 
    SUM(amount) as current_value,
    LAG(SUM(amount)) OVER (ORDER BY DATE_TRUNC('month', date)) as prior_value,
    ROUND(
        (SUM(amount) - LAG(SUM(amount)) OVER (ORDER BY DATE_TRUNC('month', date)))
        / LAG(SUM(amount)) OVER (ORDER BY DATE_TRUNC('month', date)) * 100,
        1
    ) as trend_pct
FROM table_name
WHERE date >= DATE_TRUNC('month', CURRENT_DATE)
"""

BUDGET_VARIANCE = """
-- Budget vs Actual with Variance
SELECT 
    category,
    SUM(actual_amount) as actual,
    MAX(budget_amount) as budget,
    SUM(actual_amount) - MAX(budget_amount) as variance,
    ROUND(
        (SUM(actual_amount) - MAX(budget_amount)) / MAX(budget_amount) * 100,
        1
    ) as variance_pct
FROM expenses
GROUP BY category
ORDER BY variance_pct DESC
"""

TOP_N_WITH_OTHERS = """
-- Top N Categories with "Others" Rollup
WITH ranked AS (
    SELECT 
        category,
        SUM(amount) as total,
        ROW_NUMBER() OVER (ORDER BY SUM(amount) DESC) as rank
    FROM expenses
    GROUP BY category
)
SELECT 
    CASE WHEN rank <= 5 THEN category ELSE 'Others' END as category,
    SUM(total) as total_amount
FROM ranked
GROUP BY CASE WHEN rank <= 5 THEN category ELSE 'Others' END
ORDER BY SUM(total) DESC
"""

# ============================================================================
# CHART CONFIGURATION TEMPLATES
# ============================================================================

BAR_CHART_CONFIG = {
    'viz_type': 'dist_bar',
    'color_scheme': 'expense_categories',  # or 'agencies'
    'show_legend': True,
    'rich_tooltip': True,
    'show_bar_value': True,
    'bar_stacked': False,
    'x_axis_format': ',d',
    'y_axis_format': ',.0f',
}

LINE_CHART_CONFIG = {
    'viz_type': 'line',
    'color_scheme': 'agencies',
    'line_interpolation': 'smooth',  # SAP curved lines
    'show_legend': True,
    'show_markers': True,
    'marker_size': 6,
    'x_axis_format': 'smart_date',
    'y_axis_format': ',.0f',
}

PIE_CHART_CONFIG = {
    'viz_type': 'pie',
    'color_scheme': 'expense_categories',
    'show_labels': True,
    'label_type': 'value_percent',
    'donut': True,              # SAP Analytics Cloud style
    'inner_radius': 50,
}

TABLE_CONFIG = {
    'viz_type': 'table',
    'page_length': 25,
    'show_cell_bars': True,
    'cell_bars_color': '#0a6ed1',  # SAP blue
    'align_pn': True,              # Right-align numbers
    'conditional_formatting': True,
}

BIG_NUMBER_CONFIG = {
    'viz_type': 'big_number_total',
    'header_font_size': 0.4,
    'subheader_font_size': 0.15,
    'y_axis_format': '₱,.0f',      # Philippine Peso
    'show_trend_line': True,
}

# ============================================================================
# DASHBOARD LAYOUT GRID (SAP Standard)
# ============================================================================

"""
┌────────────────────────────────────────────────────────────────┐
│                         12-COLUMN GRID                         │
├──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┤
│  1   │  2   │  3   │  4   │  5   │  6   │  7   │  8   │  9   │
└──────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┘

STANDARD WIDTHS:
- Full Width:    12 columns (filters, main content)
- Half Width:     6 columns (side-by-side charts)
- Third Width:    4 columns (KPIs, mini charts)
- Quarter Width:  3 columns (KPI cards)

SAP DASHBOARD STRUCTURE:
┌────────────────────────────────────────────────────────────────┐
│ HEADER BAR (SAP Blue Gradient)                                │
├────────────────────────────────────────────────────────────────┤
│ FILTER BAR (Native Filters, Horizontal Layout)                │
├──────────┬──────────┬──────────┬──────────┐
│  KPI 1   │  KPI 2   │  KPI 3   │  KPI 4   │  ← 3 cols each
├──────────┴──────────┼──────────┴──────────┤
│                     │                     │
│   Main Chart        │   Secondary Chart   │  ← 8 cols + 4 cols
│   (Line/Bar)        │   (Pie/Table)       │
│                     │                     │
├─────────────────────────────────────────┤
│  Detail Table (Full Width)              │  ← 12 cols
└──────────────────────────────────────────┘
"""

# ============================================================================
# COMMON TASKS - ONE-LINERS
# ============================================================================

QUICK_COMMANDS = """
# Restart Superset (Docker)
docker-compose restart superset

# Clear Superset Cache
docker exec superset superset cache-clear

# Rebuild Frontend
cd superset-frontend && npm run build

# Import Dashboard
superset import-dashboards -f dashboard.json

# Export Dashboard
superset export-dashboards > backup.json

# Test Database Connection
docker exec superset superset test-db

# Create Admin User
docker exec superset superset fab create-admin
"""

# ============================================================================
# TROUBLESHOOTING CHECKLIST
# ============================================================================

TROUBLESHOOTING = """
□ Theme Not Loading
  → Check: superset_config.py has correct imports
  → Verify: Theme file is in pythonpath directory
  → Clear: Browser cache (Cmd+Shift+R)
  → Restart: Superset service

□ Charts Wrong Colors
  → Select: Color scheme in chart settings
  → Verify: Color scheme ID matches theme config
  → Check: Chart type supports custom colors

□ CSS Not Applying
  → Verify: CUSTOM_CSS in superset_config.py
  → Check: CSS syntax is valid
  → Clear: Superset cache
  → Rebuild: Frontend if using static files

□ Slow Performance
  → Enable: Redis caching
  → Optimize: SQL queries (< 2 sec)
  → Add: Indexes on filter columns
  → Check: Dashboard auto-refresh settings
"""

# ============================================================================
# KEYBOARD SHORTCUTS (Superset)
# ============================================================================

SHORTCUTS = """
DASHBOARD EDITING:
Cmd/Ctrl + S       Save dashboard
Cmd/Ctrl + Z       Undo
Cmd/Ctrl + Shift+Z Redo
Delete             Remove selected chart

CHART EXPLORATION:
Cmd/Ctrl + E       Edit chart
Cmd/Ctrl + D       Duplicate chart
Cmd/Ctrl + R       Refresh chart

NAVIGATION:
/                  Search dashboards
Cmd/Ctrl + K       Command palette
Cmd/Ctrl + ,       Settings
"""

# ============================================================================
# CRITICAL NUMBERS TO REMEMBER
# ============================================================================

CRITICAL_SPECS = {
    'Max Query Time':        '2 seconds',
    'Cache Expiry (Real-time)': '60 seconds',
    'Cache Expiry (Historical)': '3600 seconds (1 hour)',
    'Dashboard Load Target': '< 3 seconds',
    'Chart Render Target':   '< 1 second',
    'Table Page Size':       '25 rows',
    'Grid System':           '12 columns',
    'Mobile Breakpoint':     '768px',
    'KPI Card Height':       '2 grid units',
    'Main Chart Height':     '4 grid units',
    'Table Height':          '4-6 grid units',
}

# ============================================================================
# CONTACT & RESOURCES
# ============================================================================

RESOURCES = """
PROJECT FILES:
• README.md                          - Main documentation
• sap_fiori_superset_theme.py       - Theme configuration
• sap_concur_dashboard_templates.py - Dashboard templates
• sap_implementation_guide.py       - Step-by-step guide

INTEGRATION:
• Odoo Backend:    odoboo-workspace
• Database:        Supabase (spdtwktxdalcfigzeqrz)
• Frontend:        InsightPulse AI (insightpulseai.net)
• Infrastructure:  DigitalOcean Droplet

DOCUMENTATION:
• Superset Docs:   superset.apache.org/docs
• SAP Fiori:       experience.sap.com/fiori-design-web
• This Project:    See README.md for full details

COST SAVINGS:
• Annual:          ₱1.2M - ₱1.5M ($23,400)
• 5-Year:          ₱6M - ₱7.5M ($117,000)
"""

# ============================================================================
# PRINT THIS CARD
# ============================================================================

if __name__ == '__main__':
    print("=" * 72)
    print("SAP FIORI DESIGN SYSTEM - QUICK REFERENCE CARD")
    print("=" * 72)
    print("\n📋 Keep this handy during implementation!\n")
    print("Key Files:")
    print("  1. README.md - Start here")
    print("  2. sap_implementation_guide.py - Detailed steps")
    print("  3. sap_fiori_superset_theme.py - Theme config")
    print("  4. sap_concur_dashboard_templates.py - Dashboards")
    print("\n💡 Quick Start:")
    print("  1. Copy theme file to Superset")
    print("  2. Update superset_config.py")
    print("  3. Restart Superset")
    print("  4. Import dashboards")
    print("  5. Done! 🎉")
    print("\n" + "=" * 72)
    print("Annual Savings: ₱1.2M - ₱1.5M | SAP Quality at $0 License Cost")
    print("=" * 72)
