import os, requests
from odoo import http
from odoo.http import request

RAG_API = os.getenv("RAG_API_URL","http://127.0.0.1:8085")

class RagPanel(http.Controller):
    @http.route('/rag/ask', type='json', auth='user')
    def rag_ask(self, question, top_k=5):
        org_key = request.env.user.company_id and str(request.env.user.company_id.id) or "default"
        r = requests.post(f"{RAG_API}/v1/ask", json={"question":question,"org_key":org_key,"top_k":top_k}, timeout=30)
        r.raise_for_status()
        return r.json()

    @http.route('/odoo/insights', type='http', auth='user', website=True)
    def insights(self, dashboard_id=None):
        return request.render('rag_panel.page', {"dashboard_id": dashboard_id})
