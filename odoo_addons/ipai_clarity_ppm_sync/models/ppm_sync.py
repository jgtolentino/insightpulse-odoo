from odoo import models, api

class IpaiPpmSync(models.TransientModel):
    _name = "ipai.ppm.sync"
    _description = "Pull PPM projects/tasks/timesheets"

    @api.model
    def action_pull(self):
        # TODO: upsert project.project, project.task, account.analytic.line
        return {"status":"ok"}
