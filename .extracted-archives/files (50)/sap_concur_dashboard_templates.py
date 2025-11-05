# SAP CONCUR DASHBOARD TEMPLATES FOR SUPERSET
# Travel & Expense Management - Finance Shared Service Center
# Matches SAP Concur + SAP Analytics Cloud dashboard layouts

"""
Dashboard Templates with SQL Queries for:
1. Expense Report Dashboard
2. Travel Request Dashboard
3. Spend Analytics Dashboard
4. Policy Compliance Dashboard
5. Approval Workflow Dashboard
"""

# ============================================================================
# DASHBOARD 1: EXPENSE REPORT OVERVIEW (SAP Concur Style)
# ============================================================================

EXPENSE_REPORT_DASHBOARD = {
    'dashboard_title': 'Expense Reports - Overview',
    'description': 'Real-time expense report tracking and analytics',
    
    'layout': {
        'type': 'sap_shell',  # SAP Fiori shell layout
        'grid_columns': 12,
        'sections': [
            # Header KPIs (4 cards across)
            {
                'row': 0,
                'charts': [
                    {'col': 0, 'width': 3, 'height': 2, 'chart': 'total_pending_amount'},
                    {'col': 3, 'width': 3, 'height': 2, 'chart': 'reports_pending_approval'},
                    {'col': 6, 'width': 3, 'height': 2, 'chart': 'avg_processing_time'},
                    {'col': 9, 'width': 3, 'height': 2, 'chart': 'policy_violations'},
                ]
            },
            # Main charts row
            {
                'row': 2,
                'charts': [
                    {'col': 0, 'width': 8, 'height': 4, 'chart': 'expense_trend'},
                    {'col': 8, 'width': 4, 'height': 4, 'chart': 'category_breakdown'},
                ]
            },
            # Detail tables row
            {
                'row': 6,
                'charts': [
                    {'col': 0, 'width': 12, 'height': 4, 'chart': 'pending_reports_table'},
                ]
            }
        ]
    },
    
    'charts': {
        'total_pending_amount': {
            'type': 'big_number_total',
            'title': 'Pending Reimbursement',
            'sql': """
                SELECT 
                    SUM(total_amount) as value,
                    CONCAT(
                        CASE 
                            WHEN SUM(total_amount) - LAG(SUM(total_amount)) OVER (ORDER BY DATE_TRUNC('month', submission_date)) > 0 
                            THEN '↑ '
                            ELSE '↓ '
                        END,
                        ROUND(
                            (SUM(total_amount) - LAG(SUM(total_amount)) OVER (ORDER BY DATE_TRUNC('month', submission_date))) 
                            / LAG(SUM(total_amount)) OVER (ORDER BY DATE_TRUNC('month', submission_date)) * 100
                        , 1),
                        '%'
                    ) as trend
                FROM expense_reports
                WHERE status IN ('submitted', 'approved')
                AND submission_date >= DATE_TRUNC('month', CURRENT_DATE)
            """,
            'format': '₱#,##0.00',
            'color': 'primary',
            'border_color': 'primary',
        },
        
        'reports_pending_approval': {
            'type': 'big_number_total',
            'title': 'Reports Awaiting Approval',
            'sql': """
                SELECT 
                    COUNT(*) as value,
                    CONCAT('Due: ', COUNT(CASE WHEN due_date < CURRENT_DATE THEN 1 END)) as subtitle
                FROM expense_reports
                WHERE status = 'submitted'
            """,
            'format': '#,##0',
            'color': 'warning',
            'border_color': 'warning',
        },
        
        'avg_processing_time': {
            'type': 'big_number_total',
            'title': 'Avg Processing Time',
            'sql': """
                SELECT 
                    ROUND(AVG(DATE_PART('day', approval_date - submission_date)), 1) as value,
                    'days' as suffix
                FROM expense_reports
                WHERE status = 'approved'
                AND approval_date >= CURRENT_DATE - INTERVAL '30 days'
            """,
            'format': '#,##0.0',
            'color': 'info',
            'border_color': 'info',
        },
        
        'policy_violations': {
            'type': 'big_number_total',
            'title': 'Policy Violations',
            'sql': """
                SELECT 
                    COUNT(*) as value,
                    ROUND(COUNT(*) * 100.0 / NULLIF(COUNT(*) OVER (), 0), 1) as percentage
                FROM expense_line_items
                WHERE policy_violation = true
                AND created_date >= DATE_TRUNC('month', CURRENT_DATE)
            """,
            'format': '#,##0',
            'color': 'error',
            'border_color': 'error',
        },
        
        'expense_trend': {
            'type': 'line',
            'title': 'Monthly Expense Trend by Category',
            'sql': """
                SELECT 
                    DATE_TRUNC('month', submission_date) as month,
                    expense_category,
                    SUM(amount) as total_amount
                FROM expense_line_items eli
                JOIN expense_reports er ON eli.report_id = er.id
                WHERE submission_date >= CURRENT_DATE - INTERVAL '12 months'
                GROUP BY 1, 2
                ORDER BY 1, 2
            """,
            'x_axis': 'month',
            'metrics': ['total_amount'],
            'groupby': ['expense_category'],
            'color_scheme': 'expense_categories',
            'show_legend': true,
            'smooth': true,
        },
        
        'category_breakdown': {
            'type': 'pie',
            'title': 'Spend by Category (This Month)',
            'sql': """
                SELECT 
                    expense_category,
                    SUM(amount) as total_amount
                FROM expense_line_items eli
                JOIN expense_reports er ON eli.report_id = er.id
                WHERE DATE_TRUNC('month', submission_date) = DATE_TRUNC('month', CURRENT_DATE)
                GROUP BY 1
                ORDER BY 2 DESC
            """,
            'groupby': ['expense_category'],
            'metric': 'total_amount',
            'color_scheme': 'expense_categories',
            'show_labels': true,
            'donut': true,
        },
        
        'pending_reports_table': {
            'type': 'table',
            'title': 'Pending Expense Reports',
            'sql': """
                SELECT 
                    er.report_number,
                    er.employee_name,
                    a.agency_code,
                    er.submission_date,
                    er.total_amount,
                    er.status,
                    CASE 
                        WHEN er.policy_compliant THEN 'Compliant'
                        ELSE 'Violations'
                    END as compliance,
                    er.approver_name,
                    CASE 
                        WHEN er.due_date < CURRENT_DATE THEN 'Overdue'
                        WHEN er.due_date <= CURRENT_DATE + INTERVAL '2 days' THEN 'Due Soon'
                        ELSE 'On Track'
                    END as urgency
                FROM expense_reports er
                JOIN agencies a ON er.agency_id = a.id
                WHERE er.status IN ('submitted', 'approved')
                ORDER BY er.submission_date DESC
                LIMIT 50
            """,
            'columns': [
                {'name': 'report_number', 'label': 'Report #', 'align': 'left'},
                {'name': 'employee_name', 'label': 'Employee', 'align': 'left'},
                {'name': 'agency_code', 'label': 'Agency', 'align': 'center'},
                {'name': 'submission_date', 'label': 'Submitted', 'align': 'left', 'format': 'YYYY-MM-DD'},
                {'name': 'total_amount', 'label': 'Amount', 'align': 'right', 'format': '₱#,##0.00'},
                {'name': 'status', 'label': 'Status', 'align': 'center', 'conditional_formatting': {
                    'submitted': 'expense-status submitted',
                    'approved': 'expense-status approved',
                }},
                {'name': 'compliance', 'label': 'Policy', 'align': 'center', 'conditional_formatting': {
                    'Compliant': 'policy-badge compliant',
                    'Violations': 'policy-badge violation',
                }},
                {'name': 'approver_name', 'label': 'Approver', 'align': 'left'},
                {'name': 'urgency', 'label': 'Priority', 'align': 'center'},
            ],
            'page_length': 25,
            'conditional_formatting': true,
        }
    },
    
    'filters': [
        {'column': 'agency_id', 'type': 'select', 'label': 'Agency'},
        {'column': 'submission_date', 'type': 'date_range', 'label': 'Submission Date'},
        {'column': 'status', 'type': 'multi_select', 'label': 'Status'},
        {'column': 'expense_category', 'type': 'multi_select', 'label': 'Category'},
    ]
}

# ============================================================================
# DASHBOARD 2: TRAVEL REQUEST DASHBOARD (SAP Concur Style)
# ============================================================================

TRAVEL_REQUEST_DASHBOARD = {
    'dashboard_title': 'Travel Requests - Management',
    'description': 'Travel request tracking and approval workflows',
    
    'charts': {
        'travel_requests_overview': {
            'type': 'mixed_timeseries',
            'title': 'Travel Request Volume & Approval Rate',
            'sql': """
                SELECT 
                    DATE_TRUNC('week', request_date) as week,
                    COUNT(*) as total_requests,
                    SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved_requests,
                    ROUND(
                        SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 
                        1
                    ) as approval_rate
                FROM travel_requests
                WHERE request_date >= CURRENT_DATE - INTERVAL '26 weeks'
                GROUP BY 1
                ORDER BY 1
            """,
            'chart_type_1': 'bar',  # total_requests
            'chart_type_2': 'line', # approval_rate
            'y_axis_format': '#,##0',
            'y_axis_2_format': '#,##0.0%',
        },
        
        'destination_analysis': {
            'type': 'table',
            'title': 'Top Destinations - YTD',
            'sql': """
                SELECT 
                    destination_city,
                    destination_country,
                    COUNT(*) as trip_count,
                    SUM(estimated_cost) as total_cost,
                    ROUND(AVG(estimated_cost), 2) as avg_cost,
                    ROUND(AVG(duration_days), 1) as avg_duration
                FROM travel_requests
                WHERE status = 'completed'
                AND request_date >= DATE_TRUNC('year', CURRENT_DATE)
                GROUP BY 1, 2
                ORDER BY 3 DESC
                LIMIT 20
            """,
        },
        
        'approval_workflow': {
            'type': 'sankey',
            'title': 'Travel Request Approval Flow',
            'sql': """
                SELECT 
                    status as source,
                    next_status as target,
                    COUNT(*) as value
                FROM (
                    SELECT 
                        tr.id,
                        tr.status,
                        LEAD(tr.status) OVER (PARTITION BY tr.id ORDER BY ah.action_date) as next_status
                    FROM travel_requests tr
                    JOIN approval_history ah ON tr.id = ah.travel_request_id
                    WHERE tr.request_date >= CURRENT_DATE - INTERVAL '90 days'
                ) flow
                WHERE next_status IS NOT NULL
                GROUP BY 1, 2
            """,
            'color_scheme': 'agencies',
        }
    }
}

# ============================================================================
# DASHBOARD 3: SPEND ANALYTICS (SAP Analytics Cloud Style)
# ============================================================================

SPEND_ANALYTICS_DASHBOARD = {
    'dashboard_title': 'Travel & Expense - Spend Analytics',
    'description': 'Comprehensive spend analysis and insights',
    
    'charts': {
        'spend_by_agency': {
            'type': 'horizontal_bar',
            'title': 'YTD Spend by Agency',
            'sql': """
                SELECT 
                    a.agency_code,
                    a.agency_name,
                    SUM(er.total_amount) as total_spend,
                    COUNT(DISTINCT er.employee_id) as employee_count,
                    SUM(er.total_amount) / COUNT(DISTINCT er.employee_id) as spend_per_employee
                FROM expense_reports er
                JOIN agencies a ON er.agency_id = a.id
                WHERE er.status IN ('approved', 'paid')
                AND er.submission_date >= DATE_TRUNC('year', CURRENT_DATE)
                GROUP BY 1, 2
                ORDER BY 3 DESC
            """,
            'x_axis': 'total_spend',
            'y_axis': 'agency_code',
            'color_scheme': 'agencies',
            'show_data_labels': true,
        },
        
        'budget_vs_actual': {
            'type': 'bullet',
            'title': 'Budget vs Actual (Current Quarter)',
            'sql': """
                SELECT 
                    expense_category,
                    SUM(actual_amount) as actual,
                    MAX(budget_amount) as budget,
                    MAX(budget_amount) * 0.9 as target  -- 90% target
                FROM (
                    SELECT 
                        eli.expense_category,
                        SUM(eli.amount) as actual_amount,
                        b.quarterly_budget as budget_amount
                    FROM expense_line_items eli
                    JOIN expense_reports er ON eli.report_id = er.id
                    JOIN budgets b ON eli.expense_category = b.category
                    WHERE DATE_TRUNC('quarter', er.submission_date) = DATE_TRUNC('quarter', CURRENT_DATE)
                    GROUP BY 1, 3
                ) data
                GROUP BY 1
                ORDER BY 2 DESC
            """,
            'color_scheme': 'variance',
        },
        
        'variance_analysis': {
            'type': 'diverging_bar',
            'title': 'Month-over-Month Variance by Category',
            'sql': """
                WITH current_month AS (
                    SELECT expense_category, SUM(amount) as current_amount
                    FROM expense_line_items eli
                    JOIN expense_reports er ON eli.report_id = er.id
                    WHERE DATE_TRUNC('month', submission_date) = DATE_TRUNC('month', CURRENT_DATE)
                    GROUP BY 1
                ),
                prior_month AS (
                    SELECT expense_category, SUM(amount) as prior_amount
                    FROM expense_line_items eli
                    JOIN expense_reports er ON eli.report_id = er.id
                    WHERE DATE_TRUNC('month', submission_date) = DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
                    GROUP BY 1
                )
                SELECT 
                    cm.expense_category,
                    cm.current_amount,
                    pm.prior_amount,
                    (cm.current_amount - pm.prior_amount) as variance,
                    ROUND((cm.current_amount - pm.prior_amount) / NULLIF(pm.prior_amount, 0) * 100, 1) as variance_pct
                FROM current_month cm
                LEFT JOIN prior_month pm ON cm.expense_category = pm.expense_category
                ORDER BY 5 DESC
            """,
            'color_scheme': 'variance',
        }
    }
}

# ============================================================================
# DASHBOARD 4: POLICY COMPLIANCE (SAP Concur Style)
# ============================================================================

POLICY_COMPLIANCE_DASHBOARD = {
    'dashboard_title': 'Policy Compliance & Audit Trail',
    'description': 'Travel & expense policy compliance monitoring',
    
    'charts': {
        'compliance_score': {
            'type': 'gauge',
            'title': 'Overall Compliance Score',
            'sql': """
                SELECT 
                    ROUND(
                        SUM(CASE WHEN policy_compliant THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
                        1
                    ) as compliance_score
                FROM expense_reports
                WHERE submission_date >= DATE_TRUNC('month', CURRENT_DATE)
            """,
            'min': 0,
            'max': 100,
            'ranges': [
                {'from': 0, 'to': 70, 'color': 'error'},
                {'from': 70, 'to': 90, 'color': 'warning'},
                {'from': 90, 'to': 100, 'color': 'success'},
            ]
        },
        
        'violation_breakdown': {
            'type': 'treemap',
            'title': 'Policy Violations by Type',
            'sql': """
                SELECT 
                    violation_type,
                    violation_category,
                    COUNT(*) as violation_count,
                    SUM(amount) as total_amount
                FROM expense_line_items
                WHERE policy_violation = true
                AND created_date >= DATE_TRUNC('month', CURRENT_DATE)
                GROUP BY 1, 2
                ORDER BY 3 DESC
            """,
            'color_scheme': 'traffic_light',
        },
        
        'audit_trail': {
            'type': 'table',
            'title': 'Recent Policy Violations - Detailed',
            'sql': """
                SELECT 
                    er.report_number,
                    er.employee_name,
                    a.agency_code,
                    eli.expense_date,
                    eli.expense_category,
                    eli.merchant_name,
                    eli.amount,
                    eli.violation_type,
                    eli.violation_reason,
                    er.status,
                    CASE 
                        WHEN er.manager_override THEN 'Approved (Override)'
                        ELSE 'Pending Review'
                    END as resolution
                FROM expense_line_items eli
                JOIN expense_reports er ON eli.report_id = er.id
                JOIN agencies a ON er.agency_id = a.id
                WHERE eli.policy_violation = true
                AND eli.created_date >= CURRENT_DATE - INTERVAL '30 days'
                ORDER BY eli.created_date DESC
                LIMIT 100
            """,
            'conditional_formatting': {
                'violation_type': {
                    'Over Limit': 'policy-badge violation',
                    'Missing Receipt': 'policy-badge warning',
                    'Unapproved Merchant': 'policy-badge warning',
                }
            }
        }
    }
}

# ============================================================================
# DASHBOARD 5: EXECUTIVE SUMMARY (SAP Analytics Cloud Style)
# ============================================================================

EXECUTIVE_SUMMARY_DASHBOARD = {
    'dashboard_title': 'T&E Executive Dashboard',
    'description': 'High-level travel & expense metrics for leadership',
    
    'layout': {
        'type': 'executive',
        'sections': [
            # Top KPI row (full width cards with trends)
            {
                'type': 'kpi_row',
                'cards': [
                    'total_spend_ytd',
                    'avg_expense_per_employee',
                    'compliance_rate',
                    'cost_savings',
                ]
            },
            # Main analytics section (2 columns)
            {
                'type': 'main_content',
                'left_column': ['spend_trend', 'category_mix'],
                'right_column': ['top_spenders', 'agency_comparison'],
            },
            # Bottom insights
            {
                'type': 'insights',
                'chart': 'executive_insights',
            }
        ]
    },
    
    'charts': {
        'total_spend_ytd': {
            'type': 'kpi_card',
            'title': 'Total T&E Spend YTD',
            'sql': """
                SELECT 
                    SUM(total_amount) as value,
                    ROUND(
                        (SUM(total_amount) - SUM(total_amount) FILTER (WHERE submission_date < DATE_TRUNC('year', CURRENT_DATE))) 
                        / NULLIF(SUM(total_amount) FILTER (WHERE submission_date < DATE_TRUNC('year', CURRENT_DATE)), 0) * 100,
                        1
                    ) as yoy_change
                FROM expense_reports
                WHERE status IN ('approved', 'paid')
                AND submission_date >= DATE_TRUNC('year', CURRENT_DATE)
            """,
            'format': '₱#,##0.00',
            'show_trend': true,
            'trend_format': '#,##0.0%',
        }
    }
}

# ============================================================================
# SQL HELPER FUNCTIONS
# ============================================================================

def generate_dashboard_sql(dashboard_config, date_range=None, agency_filter=None):
    """
    Generate parameterized SQL queries for dashboards
    
    Args:
        dashboard_config: Dashboard configuration dict
        date_range: Tuple of (start_date, end_date)
        agency_filter: List of agency IDs to filter by
        
    Returns:
        Dict of chart_id -> SQL query with applied filters
    """
    queries = {}
    
    for chart_id, chart_config in dashboard_config['charts'].items():
        sql = chart_config['sql']
        
        # Add date range filter
        if date_range:
            sql = sql.replace(
                'WHERE', 
                f"WHERE submission_date BETWEEN '{date_range[0]}' AND '{date_range[1]}' AND"
            )
        
        # Add agency filter
        if agency_filter:
            agency_list = ','.join([f"'{a}'" for a in agency_filter])
            sql = sql.replace(
                'WHERE',
                f"WHERE agency_id IN ({agency_list}) AND"
            )
        
        queries[chart_id] = sql
    
    return queries

# ============================================================================
# EXPORT DASHBOARD CONFIGS
# ============================================================================

ALL_DASHBOARDS = {
    'expense_reports': EXPENSE_REPORT_DASHBOARD,
    'travel_requests': TRAVEL_REQUEST_DASHBOARD,
    'spend_analytics': SPEND_ANALYTICS_DASHBOARD,
    'policy_compliance': POLICY_COMPLIANCE_DASHBOARD,
    'executive_summary': EXECUTIVE_SUMMARY_DASHBOARD,
}

if __name__ == '__main__':
    import json
    
    # Export to JSON for Superset import
    with open('sap_concur_dashboards.json', 'w') as f:
        json.dump(ALL_DASHBOARDS, f, indent=2)
    
    print("Dashboard templates generated successfully!")
    print("\nAvailable dashboards:")
    for key, dashboard in ALL_DASHBOARDS.items():
        print(f"  - {key}: {dashboard['dashboard_title']}")
