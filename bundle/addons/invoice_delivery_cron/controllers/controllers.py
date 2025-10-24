# from odoo import http


# class InvoiceDeliveryCron(http.Controller):
#     @http.route('/invoice_delivery_cron/invoice_delivery_cron', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/invoice_delivery_cron/invoice_delivery_cron/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('invoice_delivery_cron.listing', {
#             'root': '/invoice_delivery_cron/invoice_delivery_cron',
#             'objects': http.request.env['invoice_delivery_cron.invoice_delivery_cron'].search([]),
#         })

#     @http.route('/invoice_delivery_cron/invoice_delivery_cron/objects/<model("invoice_delivery_cron.invoice_delivery_cron"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('invoice_delivery_cron.object', {
#             'object': obj
#         })

