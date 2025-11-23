from odoo import http
from odoo.http import request
from datetime import date
import json


class FinancePPMDashboard(http.Controller):
    """HTTP controller for Finance PPM ECharts dashboard"""

    @http.route("/ipai/finance/ppm", type="http", auth="user", website=True)
    def ppm_dashboard(self, **kwargs):
        """
        Main PPM dashboard route with ECharts visualizations

        Charts:
        1. BIR Timeline (Gantt-style showing deadlines)
        2. Completion vs Deadline (Bar chart)
        3. Status Distribution (Pie chart)
        """
        # Fetch BIR schedules
        bir_schedules = request.env["ipai.finance.bir_schedule"].sudo().search([])

        # Prepare chart data
        chart_data = []
        for bir in bir_schedules:
            chart_data.append({
                "form": bir.name,
                "period": bir.period_covered,
                "filing_deadline": bir.filing_deadline.isoformat() if bir.filing_deadline else None,
                "prep_deadline": bir.prep_deadline.isoformat() if bir.prep_deadline else None,
                "review_deadline": bir.review_deadline.isoformat() if bir.review_deadline else None,
                "approval_deadline": bir.approval_deadline.isoformat() if bir.approval_deadline else None,
                "completion": bir.completion_pct or 0,
                "status": bir.status,
                "supervisor": bir.supervisor_id.name if bir.supervisor_id else "Unassigned",
                "reviewer": bir.reviewer_id.name if bir.reviewer_id else "Unassigned",
                "approver": bir.approver_id.name if bir.approver_id else "Unassigned",
            })

        # Calculate status distribution
        status_counts = {}
        for bir in bir_schedules:
            status = bir.status
            status_counts[status] = status_counts.get(status, 0) + 1

        status_data = [
            {"name": status.replace("_", " ").title(), "value": count}
            for status, count in status_counts.items()
        ]

        return request.render("ipai_finance_ppm.ppm_dashboard_template", {
            "chart_data": json.dumps(chart_data),
            "status_data": json.dumps(status_data),
            "today": date.today().isoformat(),
            "schedule_count": len(bir_schedules),
        })
