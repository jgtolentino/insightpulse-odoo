# from odoo import http


# class VendorRateRoles(http.Controller):
#     @http.route('/vendor_rate_roles/vendor_rate_roles', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vendor_rate_roles/vendor_rate_roles/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('vendor_rate_roles.listing', {
#             'root': '/vendor_rate_roles/vendor_rate_roles',
#             'objects': http.request.env['vendor_rate_roles.vendor_rate_roles'].search([]),
#         })

#     @http.route('/vendor_rate_roles/vendor_rate_roles/objects/<model("vendor_rate_roles.vendor_rate_roles"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vendor_rate_roles.object', {
#             'object': obj
#         })

