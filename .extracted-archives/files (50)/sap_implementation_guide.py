# SAP FIORI DESIGN SYSTEM - SUPERSET IMPLEMENTATION GUIDE
# InsightPulse AI - Finance Shared Service Center
# Travel & Expense Management Platform

"""
Complete guide to implementing SAP Concur + SAP Analytics Cloud design parity
in Apache Superset for Finance SSC operations
"""

# ============================================================================
# TABLE OF CONTENTS
# ============================================================================
"""
1. Prerequisites & Environment Setup
2. Theme Installation & Configuration
3. Custom CSS Deployment
4. Dashboard Template Creation
5. Chart Styling & Color Schemes
6. Component Customization
7. Testing & Validation
8. Production Deployment
9. Maintenance & Updates
"""

# ============================================================================
# 1. PREREQUISITES & ENVIRONMENT SETUP
# ============================================================================

PREREQUISITES = {
    'superset_version': '5.0.0+',  # Theme support requires 5.0+
    'python_version': '3.9+',
    'database': 'PostgreSQL 12+ (recommended)',
    'redis': 'Redis 6+ (for caching)',
    'node': 'Node.js 16+ (for frontend customization)',
}

"""
Step 1.1: Check Your Superset Version
--------------------------------------
Run in your Superset environment:

$ superset version
Apache Superset 5.0.0

If version < 5.0, upgrade first:
$ pip install apache-superset --upgrade
$ superset db upgrade
$ superset init
"""

"""
Step 1.2: Backup Current Configuration
---------------------------------------
CRITICAL: Backup before making changes!

$ cp /path/to/superset_config.py /path/to/superset_config.py.backup
$ superset export-dashboards -f dashboards_backup.zip
"""

# ============================================================================
# 2. THEME INSTALLATION & CONFIGURATION
# ============================================================================

"""
Step 2.1: Copy Theme Files
---------------------------
1. Upload sap_fiori_superset_theme.py to your Superset config directory

   Docker:
   $ docker cp sap_fiori_superset_theme.py superset:/app/pythonpath/
   
   Direct Install:
   $ cp sap_fiori_superset_theme.py /path/to/superset/pythonpath/
"""

"""
Step 2.2: Update superset_config.py
------------------------------------
Add the following to your superset_config.py:
"""

SUPERSET_CONFIG_ADDITIONS = '''
# ============================================================================
# SAP FIORI THEME CONFIGURATION
# ============================================================================

# Import SAP Fiori theme
import sys
sys.path.insert(0, '/app/pythonpath')  # Adjust path as needed

from sap_fiori_superset_theme import (
    THEME_OVERRIDES,
    CUSTOM_CSS,
    CHART_COLOR_SCHEMES,
    SAP_FIORI_COLORS,
    EXPENSE_CATEGORY_COLORS
)

# Application Branding
APP_NAME = "InsightPulse AI"
APP_ICON = "/static/assets/images/insightpulse_logo.png"  # Add your logo
APP_ICON_WIDTH = 126

# Apply SAP Fiori Theme
THEME_BY_NAME = {
    "sap_fiori": {
        "name": "SAP Fiori - Finance SSC",
        "colors": THEME_OVERRIDES["colors"],
        "typography": THEME_OVERRIDES["typography"],
        "borderRadius": THEME_OVERRIDES["borderRadius"],
        "gridUnit": THEME_OVERRIDES["gridUnit"],
    }
}

# Set as default theme
SUPERSET_DEFAULT_THEME = "sap_fiori"

# Custom Chart Color Schemes
EXTRA_CATEGORICAL_COLOR_SCHEMES = [
    {
        "id": "expense_categories",
        "label": "Expense Categories (SAP)",
        "colors": CHART_COLOR_SCHEMES["expense_categories"]
    },
    {
        "id": "agencies",
        "label": "Agency Colors",
        "colors": CHART_COLOR_SCHEMES["agencies"]
    },
    {
        "id": "traffic_light",
        "label": "Compliance Status",
        "colors": CHART_COLOR_SCHEMES["traffic_light"]
    },
    {
        "id": "variance",
        "label": "Variance Analysis",
        "colors": CHART_COLOR_SCHEMES["variance"]
    },
]

# Sequential Color Schemes
EXTRA_SEQUENTIAL_COLOR_SCHEMES = [
    {
        "id": "sequential_blue",
        "label": "SAP Blue (Sequential)",
        "colors": CHART_COLOR_SCHEMES["sequential_blue"]
    }
]

# Custom CSS Injection
CUSTOM_CSS = """
""" + CUSTOM_CSS + """
"""

# ============================================================================
# DASHBOARD DEFAULTS
# ============================================================================

# Default dashboard filters
DASHBOARD_FILTER_SCOPES = {
    "agency": {
        "scope": ["ROOT_ID"],
        "immune": []
    }
}

# Dashboard auto-refresh (for real-time monitoring)
DASHBOARD_AUTO_REFRESH_INTERVALS = [
    [0, "Don't refresh"],
    [10, "10 seconds"],
    [30, "30 seconds"],
    [60, "1 minute"],
    [300, "5 minutes"],
]

# ============================================================================
# FEATURE FLAGS (SAP-like features)
# ============================================================================

FEATURE_FLAGS = {
    "DASHBOARD_NATIVE_FILTERS": True,           # Native filter bar
    "DASHBOARD_CROSS_FILTERS": True,            # Cross-filtering
    "DASHBOARD_NATIVE_FILTERS_SET": True,       # Filter sets
    "ENABLE_TEMPLATE_PROCESSING": True,         # Jinja templating
    "DASHBOARD_RBAC": True,                     # Role-based access
    "THUMBNAILS": True,                         # Dashboard thumbnails
    "EMBEDDED_SUPERSET": True,                  # Embedding support
}

# ============================================================================
# ROW LEVEL SECURITY (Multi-Agency Setup)
# ============================================================================

# Users can only see data for their assigned agencies
ROW_LEVEL_SECURITY_FILTER = """
{
    "agency_id": ["RIM", "CKVC", "BOM", "JPAL", "JLI", "JAP", "LAS", "RMQB"]
}
"""
'''

"""
Step 2.3: Restart Superset
---------------------------
After updating config:

Docker:
$ docker-compose restart superset

Direct Install:
$ superset run -p 8088 --with-threads --reload
"""

# ============================================================================
# 3. CUSTOM CSS DEPLOYMENT
# ============================================================================

"""
Step 3.1: CSS File Placement
-----------------------------
Option A: Via superset_config.py (Recommended)
Already done in Step 2.2 above using CUSTOM_CSS variable

Option B: Via Static Files (For complex customization)
1. Create custom.css file
2. Place in: superset-frontend/src/assets/stylesheets/custom.css
3. Rebuild frontend:
   $ cd superset-frontend
   $ npm run build
"""

"""
Step 3.2: Add SAP 72 Font (Optional but Recommended)
------------------------------------------------------
SAP uses proprietary "72" font family. For maximum authenticity:

1. If you have SAP font license:
   - Download SAP 72 font files
   - Add to: superset-frontend/src/assets/fonts/
   - Reference in CSS via @font-face

2. Without SAP fonts (use system fallbacks):
   Already configured: "72", Arial, Helvetica, sans-serif
   
   This will use system fonts that closely match SAP's look
"""

# ============================================================================
# 4. DASHBOARD TEMPLATE CREATION
# ============================================================================

"""
Step 4.1: Import Dashboard Templates
-------------------------------------
Use the sap_concur_dashboard_templates.py file:
"""

DASHBOARD_IMPORT_STEPS = """
1. Access Superset UI → Settings → Import Dashboards

2. Upload JSON file or use programmatic import:

from sap_concur_dashboard_templates import ALL_DASHBOARDS
import json
from superset import db
from superset.models.dashboard import Dashboard

def import_sap_dashboard(dashboard_config):
    dashboard = Dashboard(
        dashboard_title=dashboard_config['dashboard_title'],
        description=dashboard_config['description'],
        slug=dashboard_config['dashboard_title'].lower().replace(' ', '-'),
        position_json=json.dumps(dashboard_config['layout'])
    )
    db.session.add(dashboard)
    db.session.commit()
    return dashboard

# Import all dashboards
for key, config in ALL_DASHBOARDS.items():
    import_sap_dashboard(config)
"""

"""
Step 4.2: Create Dashboard Layouts (Manual Method)
----------------------------------------------------
For each dashboard:

1. Create New Dashboard
   - Click "+" → Dashboard
   - Set title (e.g., "Expense Reports - Overview")
   - Set slug (e.g., "expense-reports-overview")

2. Apply SAP Grid Layout (12-column system)
   - Drag charts into 12-column grid
   - SAP standard widths:
     * Full width: 12 columns
     * Half width: 6 columns  
     * Third width: 4 columns
     * Quarter width: 3 columns
   
3. Add Filter Bar
   - Enable "Native Filters"
   - Position at top (SAP standard)
   - Style: Horizontal layout

4. Save & Publish
"""

# ============================================================================
# 5. CHART STYLING & COLOR SCHEMES
# ============================================================================

"""
Step 5.1: Apply SAP Color Schemes to Charts
--------------------------------------------
For each chart:

1. Edit Chart → Advanced → Color Scheme
2. Select from custom schemes:
   - "Expense Categories (SAP)" - for expense breakdowns
   - "Agency Colors" - for multi-entity views
   - "Compliance Status" - for policy compliance
   - "Variance Analysis" - for budget variance
"""

CHART_STYLING_EXAMPLES = {
    'bar_chart': {
        'color_scheme': 'expense_categories',
        'label_type': 'value',
        'show_legend': True,
        'x_axis_format': ',d',
        'y_axis_format': ',.0f',
        'bar_stacked': False,
        'rich_tooltip': True,
    },
    
    'line_chart': {
        'color_scheme': 'agencies',
        'show_legend': True,
        'line_interpolation': 'smooth',  # SAP style curved lines
        'show_markers': True,
        'marker_size': 6,
        'x_axis_format': 'smart_date',
        'y_axis_format': ',.0f',
    },
    
    'pie_chart': {
        'color_scheme': 'expense_categories',
        'show_labels': True,
        'label_type': 'value_percent',
        'donut': True,  # SAP Analytics Cloud style
        'inner_radius': 50,
    },
    
    'table': {
        'page_length': 25,
        'show_cell_bars': True,
        'cell_bars_color': '#0a6ed1',  # SAP blue
        'align_pn': True,  # Right-align numbers
        'conditional_formatting': True,
    },
    
    'big_number': {
        'header_font_size': 0.3,
        'subheader_font_size': 0.15,
        'time_format': 'smart_date',
        'show_trend_line': True,
    }
}

"""
Step 5.2: Configure Chart-Specific Styling
-------------------------------------------
Example: KPI Card (Big Number with Trend)
"""

KPI_CARD_CONFIG = '''
{
  "viz_type": "big_number_total",
  "metric": "total_pending_amount",
  "adhoc_filters": [],
  "header_font_size": 0.4,
  "subheader_font_size": 0.15,
  "y_axis_format": "₱,.0f",
  "time_range": "Last 30 days",
  "color_picker": {
    "r": 10,
    "g": 110,
    "b": 209,
    "a": 1
  }
}
'''

# ============================================================================
# 6. COMPONENT CUSTOMIZATION
# ============================================================================

"""
Step 6.1: Custom Status Badges (Expense Reports)
-------------------------------------------------
Add to your dataset SQL:
"""

STATUS_BADGE_SQL = """
SELECT 
    report_number,
    employee_name,
    total_amount,
    CASE status
        WHEN 'draft' THEN '<span class="expense-status draft">Draft</span>'
        WHEN 'submitted' THEN '<span class="expense-status submitted">Submitted</span>'
        WHEN 'approved' THEN '<span class="expense-status approved">Approved</span>'
        WHEN 'rejected' THEN '<span class="expense-status rejected">Rejected</span>'
        WHEN 'paid' THEN '<span class="expense-status paid">Paid</span>'
    END as status_badge
FROM expense_reports
"""

"""
Step 6.2: Agency Indicators (Multi-Entity)
-------------------------------------------
"""

AGENCY_INDICATOR_SQL = """
SELECT 
    report_number,
    CASE agency_code
        WHEN 'RIM' THEN '<span class="agency-indicator rim">RIM</span>'
        WHEN 'CKVC' THEN '<span class="agency-indicator ckvc">CKVC</span>'
        WHEN 'BOM' THEN '<span class="agency-indicator bom">BOM</span>'
        -- Add other agencies
    END as agency_badge,
    total_amount
FROM expense_reports er
JOIN agencies a ON er.agency_id = a.id
"""

"""
Step 6.3: BIR Compliance Indicators
------------------------------------
"""

BIR_COMPLIANCE_SQL = """
SELECT 
    form_type,
    filing_period,
    due_date,
    filing_date,
    CASE 
        WHEN filing_date IS NULL AND due_date < CURRENT_DATE 
            THEN '<span class="bir-compliance overdue">Overdue</span>'
        WHEN filing_date IS NULL 
            THEN '<span class="bir-compliance pending">Pending</span>'
        WHEN filing_date <= due_date 
            THEN '<span class="bir-compliance compliant">Compliant</span>'
        ELSE '<span class="bir-compliance overdue">Late Filed</span>'
    END as compliance_status
FROM bir_tax_filings
"""

# ============================================================================
# 7. TESTING & VALIDATION
# ============================================================================

"""
Step 7.1: Visual Regression Testing
------------------------------------
Compare your dashboards against SAP reference screenshots:

1. Expense Report Dashboard
   ✓ Header uses SAP blue gradient
   ✓ KPI cards have colored left border
   ✓ Status badges use SAP semantic colors
   ✓ Tables have hover states
   ✓ Charts use SAP color palette

2. Travel Request Dashboard
   ✓ Approval workflow shows clear progression
   ✓ Destination analysis table is clean
   ✓ All monetary values right-aligned

3. Spend Analytics Dashboard
   ✓ Budget variance uses red/green colors
   ✓ Agency comparison uses distinct colors
   ✓ Charts have SAP-style borders and shadows
"""

"""
Step 7.2: Cross-Browser Testing
--------------------------------
Test in:
- Chrome (primary)
- Firefox
- Safari
- Edge

Verify:
- Font rendering
- Color accuracy
- Layout responsiveness
- Filter functionality
"""

"""
Step 7.3: Performance Testing
------------------------------
SAP Analytics Cloud is fast. Your dashboards should be too:

1. Query Performance
   - All queries < 2 seconds
   - Use indexed columns in WHERE clauses
   - Materialize complex aggregations

2. Dashboard Load Time
   - Initial load < 3 seconds
   - Chart rendering < 1 second each
   - Filter application < 500ms

3. Caching Strategy
   - Enable Redis caching
   - Cache expiry: 5 minutes for real-time, 1 hour for historical
"""

# ============================================================================
# 8. PRODUCTION DEPLOYMENT
# ============================================================================

"""
Step 8.1: Production Checklist
-------------------------------
□ Theme files deployed and tested
□ Custom CSS applied correctly
□ All dashboards functional
□ Filters working across dashboards
□ Row-level security configured (agency access)
□ Performance benchmarks met
□ Browser compatibility verified
□ Mobile responsiveness checked
□ User acceptance testing complete
□ Documentation updated
"""

"""
Step 8.2: Deployment Steps (Docker)
------------------------------------
"""

DOCKER_DEPLOYMENT = '''
# 1. Build custom Superset image with theme
FROM apache/superset:5.0.0

# Copy theme files
COPY sap_fiori_superset_theme.py /app/pythonpath/
COPY superset_config.py /app/pythonpath/

# Install additional dependencies (if needed)
COPY requirements-local.txt /app/
RUN pip install -r /app/requirements-local.txt

# Build frontend with custom styles
USER root
COPY custom.css /app/superset-frontend/src/assets/stylesheets/
RUN cd /app/superset-frontend && npm run build

USER superset

# 2. Update docker-compose.yml
services:
  superset:
    build: .
    environment:
      - SUPERSET_CONFIG_PATH=/app/pythonpath/superset_config.py
      - THEME_BY_NAME=sap_fiori
    volumes:
      - ./superset_config.py:/app/pythonpath/superset_config.py
      - ./sap_fiori_superset_theme.py:/app/pythonpath/sap_fiori_superset_theme.py

# 3. Deploy
docker-compose down
docker-compose build
docker-compose up -d
docker-compose exec superset superset db upgrade
docker-compose exec superset superset init
'''

"""
Step 8.3: Rollback Plan
------------------------
If issues occur:

1. Revert to backup config:
   $ cp superset_config.py.backup superset_config.py
   $ docker-compose restart superset

2. Disable custom theme:
   # In superset_config.py
   SUPERSET_DEFAULT_THEME = "default"

3. Restore dashboards:
   $ superset import-dashboards -f dashboards_backup.zip
"""

# ============================================================================
# 9. MAINTENANCE & UPDATES
# ============================================================================

"""
Step 9.1: Monthly Maintenance Tasks
------------------------------------
□ Update expense category colors (if new categories added)
□ Verify agency color assignments
□ Check BIR compliance indicator logic
□ Review dashboard performance metrics
□ Update chart templates based on user feedback
"""

"""
Step 9.2: Superset Version Upgrades
------------------------------------
When upgrading Superset:

1. Test theme compatibility in staging
2. Check for breaking changes in:
   - Theme API
   - Chart plugins
   - Color scheme format
3. Update theme files if needed
4. Retest all dashboards
5. Deploy to production
"""

"""
Step 9.3: Adding New Components
--------------------------------
To add new SAP-style components:

1. Define color in sap_fiori_superset_theme.py
2. Add CSS class in CUSTOM_CSS
3. Update documentation
4. Test in dev environment
5. Deploy to production
"""

# ============================================================================
# COST SAVINGS SUMMARY
# ============================================================================

COST_COMPARISON = {
    'SAP Concur': {
        'annual_cost': '$15,000',
        'per_user_cost': '$200/year',
        'features': 'Travel, Expense, Approvals',
    },
    'SAP Analytics Cloud': {
        'annual_cost': '$8,400',
        'per_user_cost': '$35/month/user',
        'features': 'BI, Analytics, Reporting',
    },
    'InsightPulse AI (Self-Hosted)': {
        'annual_cost': '$0 (infrastructure only)',
        'per_user_cost': '$0',
        'features': 'All SAP features + customization',
        'infrastructure_cost': '~$200-500/month (DigitalOcean)',
        'annual_savings': '$23,400 - $29,400',
    }
}

print("=" * 80)
print("SAP FIORI DESIGN SYSTEM - IMPLEMENTATION GUIDE COMPLETE")
print("=" * 80)
print("\nAnnual Cost Savings: ₱1.2M - ₱1.5M ($23,400 - $29,400)")
print("\nYour Finance SSC now has enterprise-grade T&E management")
print("with SAP-level design parity at $0 licensing cost!")
print("\nNext Steps:")
print("1. Follow implementation steps above")
print("2. Import dashboard templates")
print("3. Train users on new interface")
print("4. Monitor adoption and gather feedback")
print("\n" + "=" * 80)
