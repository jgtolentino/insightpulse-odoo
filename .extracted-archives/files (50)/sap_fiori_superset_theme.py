# SAP Fiori Design System for Apache Superset
# Finance Shared Service Center - Travel & Expense Management
# Matches SAP Concur + SAP Analytics Cloud aesthetics

"""
superset_config.py configuration for SAP-style theming
Place this in your Superset configuration directory
"""

# ============================================================================
# SAP FIORI COLOR PALETTE
# ============================================================================

SAP_FIORI_COLORS = {
    # Primary SAP Blue
    'primary': '#0a6ed1',           # SAP Main Blue
    'primary_dark': '#0854a0',      # Darker blue for hover states
    'primary_light': '#ebf5fb',     # Light blue backgrounds
    
    # Semantic Colors (SAP Standard)
    'success': '#107e3e',           # SAP Green (Approved, Compliant)
    'warning': '#e9730c',           # SAP Orange (Pending, Review)
    'error': '#bb0000',             # SAP Red (Rejected, Non-compliant)
    'info': '#0a6ed1',              # SAP Blue (Informational)
    'neutral': '#6a6d70',           # SAP Gray (Neutral status)
    
    # Expense Status Colors
    'expense_draft': '#74777a',         # Draft expenses
    'expense_submitted': '#0a6ed1',     # Submitted for approval
    'expense_approved': '#107e3e',      # Approved
    'expense_rejected': '#bb0000',      # Rejected
    'expense_paid': '#2b7c2e',          # Paid/Reimbursed
    
    # Travel Request Status
    'travel_pending': '#e9730c',        # Pending approval
    'travel_approved': '#107e3e',       # Approved
    'travel_booked': '#0a6ed1',         # Booked
    'travel_completed': '#2b7c2e',      # Completed
    'travel_cancelled': '#74777a',      # Cancelled
    
    # Policy Compliance
    'compliant': '#107e3e',             # Within policy
    'warning': '#e9730c',               # Policy warning
    'violation': '#bb0000',             # Policy violation
    
    # Background Colors (SAP Shell)
    'background': '#f7f7f7',            # Light gray (SAP shell background)
    'surface': '#ffffff',               # White (card/panel backgrounds)
    'border': '#d9d9d9',                # Light gray borders
    'hover': '#f2f2f2',                 # Hover state
    
    # Text Colors
    'text_primary': '#32363a',          # Primary text
    'text_secondary': '#6a6d70',        # Secondary text
    'text_disabled': '#b3b3b3',         # Disabled text
    
    # Agency Colors (Multi-entity Financial Reporting)
    'agency_rim': '#0a6ed1',            # RIM - SAP Blue
    'agency_ckvc': '#5d36b8',           # CKVC - Purple
    'agency_bom': '#c0399f',            # BOM - Magenta
    'agency_jpal': '#107e3e',           # JPAL - Green
    'agency_jli': '#2b7c2e',            # JLI - Dark Green
    'agency_jap': '#e9730c',            # JAP - Orange
    'agency_las': '#d17a00',            # LAS - Dark Orange
    'agency_rmqb': '#5d36b8',           # RMQB - Purple
    
    # Chart Palette (SAP Analytics Cloud)
    'chart_1': '#0a6ed1',   # Blue
    'chart_2': '#107e3e',   # Green
    'chart_3': '#e9730c',   # Orange
    'chart_4': '#5d36b8',   # Purple
    'chart_5': '#c0399f',   # Magenta
    'chart_6': '#2b7c2e',   # Dark Green
    'chart_7': '#d17a00',   # Dark Orange
    'chart_8': '#0854a0',   # Dark Blue
}

# ============================================================================
# SUPERSET THEME CONFIGURATION
# ============================================================================

THEME_OVERRIDES = {
    'typography': {
        'families': {
            'sansSerif': '"72", "72full", Arial, Helvetica, sans-serif',  # SAP 72 font
            'serif': 'Georgia, "Times New Roman", Times, serif',
            'monospace': '"Courier New", Courier, monospace',
        },
        'weights': {
            'light': 300,
            'normal': 400,
            'medium': 500,  # SAP uses medium weight prominently
            'bold': 700,
        },
        'sizes': {
            'xxs': '10px',
            'xs': '11px',
            's': '12px',
            'm': '14px',    # Base size (SAP standard)
            'l': '16px',
            'xl': '20px',
            'xxl': '24px',
        }
    },
    
    'colors': {
        **SAP_FIORI_COLORS,
        
        # Grid/Layout
        'grayscale': {
            'base': '#666666',
            'dark1': '#32363a',
            'dark2': '#1d2125',
            'light1': '#b3b3b3',
            'light2': '#d9d9d9',
            'light3': '#f2f2f2',
            'light4': '#f7f7f7',
            'light5': '#ffffff',
        }
    },
    
    'borderRadius': '6px',      # SAP standard border radius
    'gridUnit': 4,              # SAP 4px grid system
    'spacing': {
        'xs': '4px',
        's': '8px',
        'm': '12px',
        'l': '16px',
        'xl': '24px',
        'xxl': '32px',
    },
    
    'shadows': {
        'small': '0 1px 4px rgba(0, 0, 0, 0.15)',           # SAP Card shadow
        'medium': '0 2px 8px rgba(0, 0, 0, 0.15)',          # SAP Panel shadow
        'large': '0 4px 16px rgba(0, 0, 0, 0.15)',          # SAP Modal shadow
    }
}

# ============================================================================
# SAP CONCUR - EXPENSE CATEGORY COLORS
# ============================================================================

EXPENSE_CATEGORY_COLORS = {
    'airfare': '#0a6ed1',           # Blue
    'hotel': '#107e3e',             # Green
    'meals': '#e9730c',             # Orange
    'ground_transport': '#5d36b8',  # Purple
    'car_rental': '#c0399f',        # Magenta
    'fuel': '#d17a00',              # Dark Orange
    'parking': '#2b7c2e',           # Dark Green
    'communication': '#0854a0',     # Dark Blue
    'supplies': '#74777a',          # Gray
    'entertainment': '#bb0000',     # Red
    'other': '#6a6d70',             # Neutral Gray
}

# ============================================================================
# CUSTOM CSS FOR SAP FIORI STYLING
# ============================================================================

CUSTOM_CSS = """
/* ========================================================================
   SAP FIORI DESIGN SYSTEM - SUPERSET CUSTOMIZATION
   Finance Shared Service Center - Travel & Expense Management
   ======================================================================== */

/* Import SAP 72 Font (if available via CDN) */
@import url('https://fonts.cdnfonts.com/css/sap-72');

/* ========================================================================
   GLOBAL STYLES - SAP Shell
   ======================================================================== */

body {
    font-family: "72", "72full", Arial, Helvetica, sans-serif;
    font-size: 14px;
    color: #32363a;
    background-color: #f7f7f7;
}

/* ========================================================================
   DASHBOARD HEADER - SAP Fiori Shell Bar Style
   ======================================================================== */

.dashboard-header {
    background: linear-gradient(180deg, #0a6ed1 0%, #0854a0 100%);
    border-bottom: none;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    padding: 16px 24px;
    height: 64px;
    display: flex;
    align-items: center;
}

.dashboard-header .dashboard-title {
    font-size: 20px;
    font-weight: 500;
    color: #ffffff;
    letter-spacing: 0.02em;
}

/* InsightPulse AI Branding */
.dashboard-header::before {
    content: "InsightPulse AI";
    font-size: 16px;
    font-weight: 600;
    color: #ffffff;
    margin-right: 24px;
    padding-right: 24px;
    border-right: 1px solid rgba(255, 255, 255, 0.3);
}

/* ========================================================================
   DASHBOARD CARDS - SAP Fiori Card Style
   ======================================================================== */

.dashboard-chart {
    background: #ffffff;
    border: 1px solid #d9d9d9;
    border-radius: 6px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
    transition: box-shadow 0.2s ease;
}

.dashboard-chart:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

/* Chart Headers */
.dashboard-chart .chart-header {
    background: #f7f7f7;
    border-bottom: 1px solid #d9d9d9;
    padding: 12px 16px;
    font-size: 16px;
    font-weight: 500;
    color: #32363a;
}

/* ========================================================================
   KPI CARDS - SAP Analytics Cloud Style
   ======================================================================== */

.kpi-card {
    background: linear-gradient(135deg, #ffffff 0%, #f7f7f7 100%);
    border-left: 4px solid #0a6ed1;
    padding: 20px;
    margin-bottom: 16px;
}

.kpi-card .kpi-value {
    font-size: 32px;
    font-weight: 600;
    color: #32363a;
    line-height: 1.2;
}

.kpi-card .kpi-label {
    font-size: 14px;
    font-weight: 400;
    color: #6a6d70;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 8px;
}

.kpi-card .kpi-trend {
    font-size: 14px;
    font-weight: 500;
    margin-top: 8px;
}

.kpi-card .kpi-trend.positive {
    color: #107e3e;
}

.kpi-card .kpi-trend.negative {
    color: #bb0000;
}

/* ========================================================================
   EXPENSE STATUS INDICATORS
   ======================================================================== */

.expense-status {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.expense-status.draft {
    background-color: #f2f2f2;
    color: #74777a;
}

.expense-status.submitted {
    background-color: #ebf5fb;
    color: #0854a0;
}

.expense-status.approved {
    background-color: #e8f5e9;
    color: #107e3e;
}

.expense-status.rejected {
    background-color: #ffebee;
    color: #bb0000;
}

.expense-status.paid {
    background-color: #e8f5e9;
    color: #2b7c2e;
    border: 1px solid #107e3e;
}

/* ========================================================================
   POLICY COMPLIANCE BADGES
   ======================================================================== */

.policy-badge {
    display: inline-flex;
    align-items: center;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 500;
}

.policy-badge::before {
    content: "";
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 6px;
}

.policy-badge.compliant {
    background-color: #e8f5e9;
    color: #107e3e;
}

.policy-badge.compliant::before {
    background-color: #107e3e;
}

.policy-badge.warning {
    background-color: #fff3cd;
    color: #d17a00;
}

.policy-badge.warning::before {
    background-color: #e9730c;
}

.policy-badge.violation {
    background-color: #ffebee;
    color: #bb0000;
}

.policy-badge.violation::before {
    background-color: #bb0000;
}

/* ========================================================================
   AGENCY INDICATORS (Multi-entity)
   ======================================================================== */

.agency-indicator {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 3px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.agency-indicator.rim {
    background-color: #ebf5fb;
    color: #0854a0;
    border-left: 3px solid #0a6ed1;
}

.agency-indicator.ckvc {
    background-color: #f3e5f5;
    color: #4a148c;
    border-left: 3px solid #5d36b8;
}

.agency-indicator.bom {
    background-color: #fce4ec;
    color: #880e4f;
    border-left: 3px solid #c0399f;
}

/* Add more agency styles as needed */

/* ========================================================================
   FILTER PANEL - SAP Fiori Filter Bar Style
   ======================================================================== */

.dashboard-filter-panel {
    background: #ffffff;
    border: 1px solid #d9d9d9;
    border-radius: 6px;
    padding: 16px;
    margin-bottom: 16px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.dashboard-filter-panel .filter-label {
    font-size: 14px;
    font-weight: 500;
    color: #32363a;
    margin-bottom: 8px;
}

/* ========================================================================
   TABLES - SAP Fiori Table Style
   ======================================================================== */

.superset-table {
    font-size: 13px;
    border-collapse: separate;
    border-spacing: 0;
}

.superset-table thead {
    background-color: #f7f7f7;
    border-bottom: 2px solid #d9d9d9;
}

.superset-table th {
    font-weight: 600;
    color: #32363a;
    text-transform: uppercase;
    font-size: 12px;
    letter-spacing: 0.05em;
    padding: 12px 16px;
    text-align: left;
}

.superset-table tbody tr {
    border-bottom: 1px solid #f2f2f2;
    transition: background-color 0.15s ease;
}

.superset-table tbody tr:hover {
    background-color: #f7f7f7;
}

.superset-table td {
    padding: 12px 16px;
    color: #32363a;
}

/* Monetary values - right-aligned with proper formatting */
.superset-table td.amount {
    text-align: right;
    font-family: "Courier New", monospace;
    font-weight: 500;
}

/* ========================================================================
   BUTTONS - SAP Fiori Button Style
   ======================================================================== */

.btn-primary {
    background-color: #0a6ed1;
    border: none;
    color: #ffffff;
    font-weight: 500;
    padding: 8px 16px;
    border-radius: 4px;
    transition: background-color 0.2s ease;
}

.btn-primary:hover {
    background-color: #0854a0;
}

.btn-secondary {
    background-color: transparent;
    border: 1px solid #0a6ed1;
    color: #0a6ed1;
    font-weight: 500;
    padding: 8px 16px;
    border-radius: 4px;
}

.btn-secondary:hover {
    background-color: #ebf5fb;
}

/* ========================================================================
   CHARTS - SAP Analytics Cloud Style
   ======================================================================== */

/* Bar Charts */
.chart-container .bar-chart rect {
    rx: 2;  /* Rounded corners */
}

/* Line Charts */
.chart-container .line-chart .line {
    stroke-width: 2.5px;
}

/* Pie/Donut Charts */
.chart-container .pie-chart .slice {
    stroke: #ffffff;
    stroke-width: 2px;
}

/* Chart Legends */
.chart-legend {
    font-size: 12px;
    color: #6a6d70;
}

.chart-legend .legend-item {
    margin-right: 16px;
}

/* ========================================================================
   RESPONSIVE DESIGN
   ======================================================================== */

@media (max-width: 768px) {
    .dashboard-header {
        height: 56px;
        padding: 12px 16px;
    }
    
    .kpi-card .kpi-value {
        font-size: 24px;
    }
}

/* ========================================================================
   BIR COMPLIANCE INDICATORS (Philippines Tax)
   ======================================================================== */

.bir-compliance {
    display: inline-flex;
    align-items: center;
    padding: 6px 12px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
}

.bir-compliance.compliant {
    background-color: #e8f5e9;
    color: #107e3e;
}

.bir-compliance.pending {
    background-color: #fff3cd;
    color: #d17a00;
}

.bir-compliance.overdue {
    background-color: #ffebee;
    color: #bb0000;
}

/* ========================================================================
   EXPENSE RECEIPT PREVIEW
   ======================================================================== */

.receipt-preview {
    border: 1px solid #d9d9d9;
    border-radius: 6px;
    padding: 8px;
    background: #ffffff;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.receipt-preview img {
    max-width: 100%;
    border-radius: 4px;
}

/* ========================================================================
   APPROVAL WORKFLOW TIMELINE
   ======================================================================== */

.approval-timeline {
    position: relative;
    padding-left: 32px;
}

.approval-timeline::before {
    content: "";
    position: absolute;
    left: 10px;
    top: 0;
    bottom: 0;
    width: 2px;
    background-color: #d9d9d9;
}

.approval-step {
    position: relative;
    padding-bottom: 24px;
}

.approval-step::before {
    content: "";
    position: absolute;
    left: -26px;
    top: 4px;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background-color: #0a6ed1;
    border: 2px solid #ffffff;
    box-shadow: 0 0 0 2px #0a6ed1;
}

.approval-step.completed::before {
    background-color: #107e3e;
    box-shadow: 0 0 0 2px #107e3e;
}

.approval-step.rejected::before {
    background-color: #bb0000;
    box-shadow: 0 0 0 2px #bb0000;
}

/* ========================================================================
   END OF SAP FIORI STYLES
   ======================================================================== */
"""

# ============================================================================
# CHART COLOR SCHEMES (SAP Analytics Cloud Style)
# ============================================================================

CHART_COLOR_SCHEMES = {
    # Sequential (for single metric trends)
    'sequential_blue': [
        '#ebf5fb', '#c6e7f5', '#90cdf4', '#4d9cd6', '#0a6ed1', '#0854a0'
    ],
    
    # Diverging (for variance analysis: negative to positive)
    'variance': [
        '#bb0000', '#e57373', '#f2f2f2', '#81c784', '#107e3e'
    ],
    
    # Categorical (for expense categories)
    'expense_categories': [
        EXPENSE_CATEGORY_COLORS['airfare'],
        EXPENSE_CATEGORY_COLORS['hotel'],
        EXPENSE_CATEGORY_COLORS['meals'],
        EXPENSE_CATEGORY_COLORS['ground_transport'],
        EXPENSE_CATEGORY_COLORS['car_rental'],
        EXPENSE_CATEGORY_COLORS['fuel'],
        EXPENSE_CATEGORY_COLORS['parking'],
        EXPENSE_CATEGORY_COLORS['communication'],
    ],
    
    # Multi-agency
    'agencies': [
        SAP_FIORI_COLORS['agency_rim'],
        SAP_FIORI_COLORS['agency_ckvc'],
        SAP_FIORI_COLORS['agency_bom'],
        SAP_FIORI_COLORS['agency_jpal'],
        SAP_FIORI_COLORS['agency_jli'],
        SAP_FIORI_COLORS['agency_jap'],
        SAP_FIORI_COLORS['agency_las'],
        SAP_FIORI_COLORS['agency_rmqb'],
    ],
    
    # Traffic light (compliance status)
    'traffic_light': [
        SAP_FIORI_COLORS['error'],      # Red - Violation
        SAP_FIORI_COLORS['warning'],    # Orange - Warning
        SAP_FIORI_COLORS['success'],    # Green - Compliant
    ]
}

# ============================================================================
# EXAMPLE: APPLYING THEME TO SUPERSET
# ============================================================================

# Add to your superset_config.py:
"""
# Import theme configuration
from sap_fiori_superset_theme import (
    THEME_OVERRIDES,
    CUSTOM_CSS,
    CHART_COLOR_SCHEMES,
    SAP_FIORI_COLORS,
    EXPENSE_CATEGORY_COLORS
)

# Apply theme
THEME_BY_NAME = {
    'sap_fiori': {
        'name': 'SAP Fiori - InsightPulse AI',
        'colors': THEME_OVERRIDES['colors'],
        'typography': THEME_OVERRIDES['typography'],
        'borderRadius': THEME_OVERRIDES['borderRadius'],
        'gridUnit': THEME_OVERRIDES['gridUnit'],
    }
}

# Set as default theme
APP_NAME = 'InsightPulse AI'
DEFAULT_THEME = 'sap_fiori'

# Add custom CSS
EXTRA_CATEGORICAL_COLOR_SCHEMES = [
    {
        'id': 'expense_categories',
        'label': 'Expense Categories',
        'colors': CHART_COLOR_SCHEMES['expense_categories']
    },
    {
        'id': 'agencies',
        'label': 'Agency Colors',
        'colors': CHART_COLOR_SCHEMES['agencies']
    },
    {
        'id': 'traffic_light',
        'label': 'Compliance Status',
        'colors': CHART_COLOR_SCHEMES['traffic_light']
    },
]

# Custom CSS injection
EXTRA_CATEGORICAL_COLOR_SCHEMES = CUSTOM_CSS
"""

print("SAP Fiori theme configuration generated successfully!")
print("\nNext steps:")
print("1. Copy this file to your Superset instance")
print("2. Import and apply in superset_config.py")
print("3. Restart Superset to see changes")
print("4. Configure dashboard templates with SAP-style layouts")
