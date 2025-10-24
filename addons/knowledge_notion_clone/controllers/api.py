from odoo import http
from odoo.http import request

class KnowledgeAPI(http.Controller):

    @http.route('/knowledge/api/pages', type='json', auth='user')
    def pages(self, search=None, parent_id=None):
        domain = []
        if search: domain += [('name','ilike',search)]
        if parent_id: domain += [('parent_id','=',int(parent_id))]
        pages = request.env['knowledge.page'].search_read(domain, ['id','name','parent_id','is_favorite','icon'])
        return {"pages": pages}

    @http.route('/knowledge/api/page/<int:pid>', type='json', auth='user')
    def page(self, pid):
        page = request.env['knowledge.page'].browse(pid)
        page.ensure_one()
        blocks = request.env['knowledge.block'].search_read([('page_id','=',pid)],
                    ['id','sequence','type','text','checked','db_id'])
        return {"page": {"id": page.id, "name": page.name, "icon": page.icon}, "blocks": blocks}

    @http.route('/knowledge/api/block/save', type='json', auth='user', methods=['POST'])
    def save_block(self, **payload):
        vals = payload.get('vals', {})
        bid = payload.get('id')
        if bid:
            request.env['knowledge.block'].browse(int(bid)).sudo().write(vals)
            return {"ok": True, "id": bid}
        rec = request.env['knowledge.block'].sudo().create(vals)
        return {"ok": True, "id": rec.id}
