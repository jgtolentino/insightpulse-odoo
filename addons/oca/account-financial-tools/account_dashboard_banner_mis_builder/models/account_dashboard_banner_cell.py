# Copyright 2025 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.misc import format_date


class AccountDashboardBannerCell(models.Model):
    _inherit = "account.dashboard.banner.cell"

    cell_type = fields.Selection(
        selection_add=[("mis_builder", "MIS Builder KPI")],
        ondelete={"mis_builder": "cascade"},
    )
    mis_report_instance_id = fields.Many2one("mis.report.instance", string="MIS Report")
    mis_report_id = fields.Many2one(
        related="mis_report_instance_id.report_id",
        store=True,
        string="MIS Report Template",
    )
    mis_report_kpi_id = fields.Many2one(
        "mis.report.kpi",
        string="MIS Report KPI",
        domain="[('report_id', '=', mis_report_id)]",
    )
    mis_report_kpi_type = fields.Selection(related="mis_report_kpi_id.type")
    # In mis_builder, the "type" field of a KPI can be "num" (numeric), but there is
    # nothing that will tell you if it's a monetary KPI or just a number. So we
    # add the field below.
    mis_report_kpi_num_display_currency = fields.Boolean(
        string="Display Currency", default=True
    )
    mis_report_instance_period_id = fields.Many2one(
        "mis.report.instance.period",
        string="MIS Report Period",
        domain="[('report_instance_id', '=', mis_report_instance_id), "
        "('source', 'in', ('actuals', 'actuals_alt'))]",
    )

    @api.constrains(
        "mis_report_instance_id", "mis_report_instance_id", "mis_report_kpi_id"
    )
    def _check_mis_builder(self):
        for cell in self:
            if cell.cell_type == "mis_builder":
                if (
                    not cell.mis_report_instance_id
                    or not cell.mis_report_kpi_id
                    or not cell.mis_report_instance_period_id
                ):
                    raise ValidationError(
                        _(
                            "On MIS Builder cells, you must configure a MIS Report, "
                            "a related KPI and a related Period."
                        )
                    )
                mis_report = cell.mis_report_instance_id.report_id
                if cell.mis_report_kpi_id.report_id != mis_report:
                    raise ValidationError(
                        _(
                            "The MIS Report KPI '%(kpi)s' is attached to "
                            "MIS Report Template '%(kpi_report)s' whereas "
                            "the MIS Report '%(instance)s' is attached to "
                            "MIS Report Template '%(instance_report)s'.",
                            kpi=cell.mis_report_kpi_id.display_name,
                            kpi_report=cell.mis_report_kpi_id.report_id.display_name,
                            instance=cell.mis_report_instance_id.display_name,
                            instance_report=cell.mis_report_instance_id.report_id.display_name,
                        )
                    )
                if (
                    cell.mis_report_instance_period_id.report_instance_id
                    != cell.mis_report_instance_id
                ):
                    raise ValidationError(
                        _(
                            "The MIS Report Period '%(period)s' is attached to "
                            "MIS Report '%(period_report)s' and not to "
                            "the selected MIS Report '%(report)s'.",
                            period=cell.mis_report_instance_period_id.display_name,
                            period_report=cell.mis_report_instance_period_id.report_instance_id.display_name,
                            report=cell.mis_report_instance_id.display_name,
                        )
                    )

    def _prepare_speedy(self, company):
        # We compute the MIS reports in _prepare_speedy() to mutualize MIS report
        # evaluation to speed-up computation in case we display several KPIs
        # from the same report and period
        speedy = super()._prepare_speedy(company)
        speedy["mis_style_obj"] = self.env["mis.report.style"]
        speedy["mis_lang"] = self.env["res.lang"]._lang_get(self.env.user.lang)
        speedy["mis_report"] = {}
        # key = (report, period)
        # value = {'kpis': locals_dict, 'date_from': .., 'date_to': ;;}
        mis_cells = self.filtered(lambda x: x.cell_type == "mis_builder")
        for mis_cell in mis_cells:
            mis_report = mis_cell.mis_report_id
            key = (mis_report.id, mis_cell.mis_report_instance_period_id.id)
            if key not in speedy["mis_report"]:
                date_from = mis_cell.mis_report_instance_period_id.date_from
                date_to = mis_cell.mis_report_instance_period_id.date_to
                currency = mis_cell.mis_report_instance_id.currency_id
                aep = mis_report._prepare_aep(company, currency)
                locals_dict = mis_report.evaluate(aep, date_from, date_to)
                speedy["mis_report"][key] = {
                    "kpiname2value": locals_dict,
                    "date_from": date_from,
                    "date_to": date_to,
                    "date_from_formatted": format_date(self.env, date_from),
                    "date_to_formatted": format_date(self.env, date_to),
                    "currency": currency,
                    "report_style": mis_report.style_id,
                }
        return speedy

    def _prepare_cell_data(self, company, speedy):
        res = super()._prepare_cell_data(company, speedy)
        if (
            res["cell_type"] == "mis_builder"
            and self.mis_report_instance_id
            and self.mis_report_kpi_id
            and self.mis_report_instance_period_id
        ):
            kpi = self.mis_report_kpi_id
            if not self.custom_label:
                res["label"] = kpi.description
            compute_res = speedy["mis_report"][
                (self.mis_report_id.id, self.mis_report_instance_period_id.id)
            ]
            raw_value = compute_res["kpiname2value"][kpi.name]
            style_props = speedy["mis_style_obj"].merge(
                [compute_res["report_style"], kpi.style_id]
            )
            value = speedy["mis_style_obj"].render(
                speedy["mis_lang"], style_props, kpi.type, raw_value
            )
            if kpi.type == "num" and self.mis_report_kpi_num_display_currency:
                currency = compute_res["currency"] or company.currency_id
                cur_str = currency.symbol or currency.name
                if currency.position == "before":
                    value = f"{cur_str} {value}"
                elif currency.position == "after":
                    value = f"{value} {cur_str}"
            res.update(
                {
                    "value": value,
                    "raw_value": raw_value,
                }
            )
            if not self.custom_tooltip:
                res["tooltip"] = _(
                    "MIS Builder KPI: %(kpi)s. " "From %(date_from)s to %(date_to)s.",
                    kpi=kpi.display_name,
                    date_from=compute_res["date_from_formatted"],
                    date_to=compute_res["date_to_formatted"],
                )
                if not kpi.multi:
                    expr = _(
                        "Expression: %(kpi_expression)s.", kpi_expression=kpi.expression
                    )
                    res["tooltip"] = " ".join([res["tooltip"], expr])
        return res
