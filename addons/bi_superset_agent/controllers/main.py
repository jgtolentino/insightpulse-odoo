from odoo import http
from odoo.http import request

class BiAgentController(http.Controller):
    """Controller for BI Agent operations"""

    @http.route("/bi/agent", type="http", auth="user", website=True)
    def index(self, **kw):
        """BI Agent landing page"""
        return request.render("bi_superset_agent.page_root", {})

    @http.route("/bi/chart/<int:chart_id>", type="http", auth="user")
    def view_chart(self, chart_id, **kw):
        """View individual chart"""
        analytics = request.env["bi.superset.analytics"].browse(chart_id)
        if not analytics.exists():
            return request.not_found()

        return request.render("bi_superset_agent.chart_view", {
            "analytics": analytics,
        })
