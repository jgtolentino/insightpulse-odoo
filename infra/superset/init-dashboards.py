#!/usr/bin/env python3
"""
Initialize Superset with example dashboards for InsightPulse Odoo Finance SSC
"""
import os
import sys
import json
from superset import app, db
from superset.models.dashboard import Dashboard
from superset.models.slice import Slice
from superset.models.core import Database
from sqlalchemy import create_engine

# Database connection (Supabase)
SQLALCHEMY_DATABASE_URI = os.getenv(
    'SQLALCHEMY_DATABASE_URI',
    'postgresql://postgres.spdtwktxdalcfigzeqrz:SHWYXDMFAwXI1drT@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require'
)

def create_database_connection():
    """Create Odoo database connection in Superset"""
    db_connection = Database(
        database_name='InsightPulse Odoo',
        sqlalchemy_uri=SQLALCHEMY_DATABASE_URI,
        expose_in_sqllab=True,
        allow_run_async=True,
        allow_dml=False,
        allow_csv_upload=True,
        extra=json.dumps({
            "metadata_params": {},
            "engine_params": {
                "connect_args": {
                    "sslmode": "require"
                }
            },
            "metadata_cache_timeout": {},
            "schemas_allowed_for_csv_upload": []
        })
    )
    db.session.add(db_connection)
    db.session.commit()
    return db_connection

def create_expense_charts(database_id):
    """Create expense-related charts"""
    charts = []

    # Chart 1: Expense by Agency (Pie)
    chart1 = Slice(
        slice_name='Expense by Agency - Current Month',
        viz_type='pie',
        datasource_id=database_id,
        datasource_type='table',
        params=json.dumps({
            "adhoc_filters": [
                {
                    "clause": "WHERE",
                    "expressionType": "SQL",
                    "sqlExpression": "EXTRACT(MONTH FROM date_submitted) = EXTRACT(MONTH FROM CURRENT_DATE)",
                    "filterOptionName": "current_month"
                }
            ],
            "groupby": ["company_id"],
            "metric": {
                "aggregate": "SUM",
                "column": {
                    "column_name": "total_amount",
                    "type": "DOUBLE PRECISION"
                },
                "expressionType": "SIMPLE",
                "label": "Total Expense"
            },
            "row_limit": 8,
            "color_scheme": "supersetColors",
            "show_legend": True,
            "show_labels": True,
            "label_type": "key_percent"
        })
    )
    charts.append(chart1)

    # Chart 2: BIR Compliance Status (Big Number)
    chart2 = Slice(
        slice_name='BIR Forms Submitted - This Quarter',
        viz_type='big_number_total',
        datasource_id=database_id,
        datasource_type='table',
        params=json.dumps({
            "metric": {
                "aggregate": "COUNT",
                "column": {
                    "column_name": "id",
                    "type": "INTEGER"
                },
                "expressionType": "SIMPLE",
                "label": "Form Count"
            },
            "adhoc_filters": [
                {
                    "clause": "WHERE",
                    "expressionType": "SQL",
                    "sqlExpression": "EXTRACT(QUARTER FROM submission_date) = EXTRACT(QUARTER FROM CURRENT_DATE) AND status = 'submitted'",
                    "filterOptionName": "current_quarter_submitted"
                }
            ],
            "y_axis_format": ",.0f",
            "header_font_size": 0.4,
            "subheader_font_size": 0.15
        })
    )
    charts.append(chart2)

    # Chart 3: Expense Approval Timeline (Line)
    chart3 = Slice(
        slice_name='Expense Approvals - Last 30 Days',
        viz_type='line',
        datasource_id=database_id,
        datasource_type='table',
        params=json.dumps({
            "adhoc_filters": [
                {
                    "clause": "WHERE",
                    "expressionType": "SQL",
                    "sqlExpression": "date_submitted >= CURRENT_DATE - INTERVAL '30 days'",
                    "filterOptionName": "last_30_days"
                }
            ],
            "groupby": [],
            "time_grain_sqla": "P1D",
            "time_range": "Last 30 days",
            "metrics": [
                {
                    "aggregate": "COUNT",
                    "column": {
                        "column_name": "id",
                        "type": "INTEGER"
                    },
                    "expressionType": "SIMPLE",
                    "label": "Expense Count"
                }
            ],
            "x_axis_label": "Date",
            "y_axis_label": "Number of Expenses",
            "show_legend": True,
            "line_interpolation": "linear",
            "rich_tooltip": True,
            "show_markers": True
        })
    )
    charts.append(chart3)

    # Chart 4: Top Expense Categories (Bar)
    chart4 = Slice(
        slice_name='Top 10 Expense Categories',
        viz_type='dist_bar',
        datasource_id=database_id,
        datasource_type='table',
        params=json.dumps({
            "adhoc_filters": [],
            "groupby": ["category"],
            "metrics": [
                {
                    "aggregate": "SUM",
                    "column": {
                        "column_name": "total_amount",
                        "type": "DOUBLE PRECISION"
                    },
                    "expressionType": "SIMPLE",
                    "label": "Total Amount"
                }
            ],
            "row_limit": 10,
            "color_scheme": "supersetColors",
            "show_legend": False,
            "show_bar_value": True,
            "bar_stacked": False,
            "order_desc": True
        })
    )
    charts.append(chart4)

    # Add all charts to database
    for chart in charts:
        db.session.add(chart)

    db.session.commit()
    return charts

def create_finance_dashboard(charts):
    """Create Finance SSC Executive Dashboard"""
    dashboard = Dashboard(
        dashboard_title='Finance SSC - Executive Dashboard',
        slug='finance-ssc-executive',
        slices=charts,
        position_json=json.dumps({
            "DASHBOARD_VERSION_KEY": "v2",
            "GRID_ID": {
                "type": "GRID",
                "id": "GRID_ID",
                "children": [
                    "ROW-1",
                    "ROW-2"
                ],
                "parents": ["ROOT_ID"]
            },
            "ROW-1": {
                "type": "ROW",
                "id": "ROW-1",
                "children": [
                    "CHART-1",
                    "CHART-2"
                ],
                "meta": {
                    "background": "BACKGROUND_TRANSPARENT"
                }
            },
            "ROW-2": {
                "type": "ROW",
                "id": "ROW-2",
                "children": [
                    "CHART-3",
                    "CHART-4"
                ],
                "meta": {
                    "background": "BACKGROUND_TRANSPARENT"
                }
            },
            "CHART-1": {
                "type": "CHART",
                "id": "CHART-1",
                "children": [],
                "meta": {
                    "width": 6,
                    "height": 50,
                    "chartId": charts[0].id
                }
            },
            "CHART-2": {
                "type": "CHART",
                "id": "CHART-2",
                "children": [],
                "meta": {
                    "width": 6,
                    "height": 50,
                    "chartId": charts[1].id
                }
            },
            "CHART-3": {
                "type": "CHART",
                "id": "CHART-3",
                "children": [],
                "meta": {
                    "width": 6,
                    "height": 50,
                    "chartId": charts[2].id
                }
            },
            "CHART-4": {
                "type": "CHART",
                "id": "CHART-4",
                "children": [],
                "meta": {
                    "width": 6,
                    "height": 50,
                    "chartId": charts[3].id
                }
            }
        }),
        description='Multi-agency Finance Shared Service Center overview with BIR compliance metrics',
        css='',
        json_metadata=json.dumps({
            "color_scheme": "supersetColors",
            "refresh_frequency": 300,
            "timed_refresh_immune_slices": [],
            "expanded_slices": {},
            "label_colors": {},
            "shared_label_colors": {},
            "color_scheme_domain": [],
            "cross_filters_enabled": False
        })
    )

    db.session.add(dashboard)
    db.session.commit()
    return dashboard

def main():
    """Main initialization function"""
    with app.app_context():
        print("🚀 Initializing Superset with InsightPulse Odoo dashboards...")

        # Step 1: Create database connection
        print("📊 Creating Odoo database connection...")
        database = create_database_connection()
        print(f"✅ Database connection created: {database.database_name}")

        # Step 2: Create charts
        print("📈 Creating example charts...")
        charts = create_expense_charts(database.id)
        print(f"✅ Created {len(charts)} charts")

        # Step 3: Create dashboard
        print("🎨 Creating Finance SSC dashboard...")
        dashboard = create_finance_dashboard(charts)
        print(f"✅ Dashboard created: {dashboard.dashboard_title}")
        print(f"   URL: /superset/dashboard/{dashboard.slug}/")

        print("\n🎉 Initialization complete!")
        print(f"\nAccess your dashboard at: http://localhost:8088/superset/dashboard/{dashboard.slug}/")

if __name__ == '__main__':
    main()
