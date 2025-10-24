# from odoo import http


# class ProjectBudgetWizard(http.Controller):
#     @http.route('/project_budget_wizard/project_budget_wizard', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/project_budget_wizard/project_budget_wizard/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('project_budget_wizard.listing', {
#             'root': '/project_budget_wizard/project_budget_wizard',
#             'objects': http.request.env['project_budget_wizard.project_budget_wizard'].search([]),
#         })

#     @http.route('/project_budget_wizard/project_budget_wizard/objects/<model("project_budget_wizard.project_budget_wizard"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('project_budget_wizard.object', {
#             'object': obj
#         })

