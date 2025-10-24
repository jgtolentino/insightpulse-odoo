# from odoo import http


# class PartnerBillingPrefs(http.Controller):
#     @http.route('/partner_billing_prefs/partner_billing_prefs', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/partner_billing_prefs/partner_billing_prefs/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('partner_billing_prefs.listing', {
#             'root': '/partner_billing_prefs/partner_billing_prefs',
#             'objects': http.request.env['partner_billing_prefs.partner_billing_prefs'].search([]),
#         })

#     @http.route('/partner_billing_prefs/partner_billing_prefs/objects/<model("partner_billing_prefs.partner_billing_prefs"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('partner_billing_prefs.object', {
#             'object': obj
#         })

