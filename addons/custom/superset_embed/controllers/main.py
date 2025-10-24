import os, time, requests
from odoo import http
from odoo.http import request

SUPERSET = os.getenv("SUPERSET_URL","")
API_LOGIN = f"{SUPERSET}/api/v1/security/login"
API_CSRF  = f"{SUPERSET}/api/v1/security/csrf_token/"
API_GUEST = f"{SUPERSET}/api/v1/security/guest_token/"
API_DASH  = f"{SUPERSET}/api/v1/dashboard"

_tok = {"val": None, "exp": 0}
def _access_token():
    if _tok["val"] and _tok["exp"] > time.time()+30:
        return _tok["val"]
    r = requests.post(API_LOGIN, json={
        "provider":"db","username":os.getenv("SS_USER"),"password":os.getenv("SS_PASS"),"refresh":False
    }, timeout=10)
    r.raise_for_status()
    _tok.update(val=r.json()["access_token"], exp=time.time()+600)
    return _tok["val"]

def _csrf(tok):
    r = requests.get(API_CSRF, headers={"Authorization":f"Bearer {tok}"}, timeout=10)
    r.raise_for_status()
    return r.json()["result"]

def _uuid(tok, id_or_uuid):
    if len(id_or_uuid)==36 and id_or_uuid.count("-")==4:
        return id_or_uuid
    r = requests.get(f"{API_DASH}/{id_or_uuid}", headers={"Authorization":f"Bearer {tok}"}, timeout=10)
    r.raise_for_status()
    return r.json()["result"]["uuid"]

class SupersetEmbed(http.Controller):
    @http.route('/odoo/dashboards', type='http', auth='user', website=True, csrf=False)
    def dashboards(self, **kw):
        dash = kw.get("dashboard_id")
        if not dash:
            return http.Response("dashboard_id is required", status=400)
        try:
            tok  = _access_token()
            csrf = _csrf(tok)
            uuid = _uuid(tok, dash)
            user = request.env.user.sudo()
            payload = {
                "resources":[{"type":"dashboard","id":uuid}],
                "user":{"username": user.login or f"user_{user.id}"},
                "rls": []  # add dataset clauses if needed
            }
            g = requests.post(API_GUEST, json=payload,
                              headers={"Authorization":f"Bearer {tok}","X-CSRFToken":csrf},
                              timeout=10)
            g.raise_for_status()
            guest = g.json()["token"]
        except Exception as e:
            return http.Response(f"Embed error: {str(e)}", status=502)
        return request.render('superset_embed.page',
                              {"guest_token": guest, "superset_url": SUPERSET, "dash_uuid": uuid})

    @http.route('/odoo/insights', type='http', auth='user', website=True)
    def insights(self, dashboard_id=None):
        return request.render('superset_embed.page',
                              {"guest_token": "", "superset_url": SUPERSET, "dash_uuid": dashboard_id})

    @http.route('/odoo/superset/dashboards', type='json', auth='user')
    def list_dashboards(self):
        """Return list of available Superset dashboards"""
        try:
            tok = _access_token()
            r = requests.get(f"{API_DASH}/?q=(page:0,page_size:50)",
                            headers={"Authorization":f"Bearer {tok}"}, timeout=10)
            r.raise_for_status()
            dashboards = r.json().get("result", [])
            return [{
                "id": dash.get("id"),
                "uuid": dash.get("uuid"),
                "title": dash.get("dashboard_title"),
                "description": dash.get("description", "")
            } for dash in dashboards]
        except Exception as e:
            return {"error": str(e)}
