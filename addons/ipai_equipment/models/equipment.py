# -*- coding: utf-8 -*-
from odoo import api, fields, models


class MaintenanceEquipment(models.Model):
    _inherit = "maintenance.equipment"

    equipment_code = fields.Char(string="Asset Tag")
    condition = fields.Selection(
        [
            ("new", "New"),
            ("good", "Good"),
            ("fair", "Fair"),
            ("poor", "Poor"),
            ("broken", "Broken"),
        ],
        string="Condition",
        default="good",
        tracking=True,
    )
    status = fields.Selection(
        [
            ("available", "Available"),
            ("reserved", "Reserved"),
            ("checked_out", "Checked Out"),
            ("maintenance", "In Maintenance"),
            ("retired", "Retired"),
        ],
        string="Status",
        default="available",
        index=True,
        tracking=True,
    )
    current_custodian_id = fields.Many2one("res.partner", string="Current Custodian")
    image_1920 = fields.Image("Image")

    # Smart button fields
    booking_count = fields.Integer(
        string="Bookings",
        compute="_compute_booking_count",
    )
    incident_count = fields.Integer(
        string="Incidents",
        compute="_compute_incident_count",
    )

    def _compute_booking_count(self):
        for asset in self:
            asset.booking_count = self.env['ipai.equipment.booking'].search_count([
                ('equipment_ids', 'in', asset.id)
            ])

    def _compute_incident_count(self):
        for asset in self:
            asset.incident_count = self.env['ipai.equipment.incident'].search_count([
                ('equipment_id', '=', asset.id)
            ])

    def action_view_bookings(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Bookings',
            'res_model': 'ipai.equipment.booking',
            'view_mode': 'tree,form',
            'domain': [('equipment_ids', 'in', self.id)],
            'context': {'default_equipment_ids': [self.id]},
        }

    def action_view_incidents(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Incidents',
            'res_model': 'ipai.equipment.incident',
            'view_mode': 'tree,form',
            'domain': [('equipment_id', '=', self.id)],
            'context': {'default_equipment_id': self.id},
        }


class IpaiEquipmentBooking(models.Model):
    _name = "ipai.equipment.booking"
    _description = "IPAI Equipment Booking"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "start_datetime desc"

    name = fields.Char(
        string="Reference",
        required=True,
        default=lambda self: self.env["ir.sequence"].next_by_code("ipai.equipment.booking"),
    )
    equipment_ids = fields.Many2many("maintenance.equipment", string="Equipment", required=True)
    requester_id = fields.Many2one("res.users", string="Requester", default=lambda self: self.env.user)
    project_id = fields.Many2one("project.project", string="Project / Job")
    start_datetime = fields.Datetime(required=True)
    end_datetime = fields.Datetime(required=True)
    purpose = fields.Char()
    notes = fields.Text()
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("requested", "Requested"),
            ("approved", "Approved"),
            ("checked_out", "Checked Out"),
            ("returned", "Returned"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    is_overdue = fields.Boolean(
        string="Overdue",
        compute="_compute_is_overdue",
        store=True,
    )

    @api.depends('end_datetime', 'state')
    def _compute_is_overdue(self):
        now = fields.Datetime.now()
        for rec in self:
            rec.is_overdue = (
                rec.state == 'checked_out' and
                rec.end_datetime and
                rec.end_datetime < now
            )

    @api.constrains("equipment_ids", "start_datetime", "end_datetime", "state")
    def _check_booking_conflict(self):
        for booking in self:
            if booking.state == "cancelled":
                continue
            domain = [
                ("id", "!=", booking.id),
                ("state", "not in", ["cancelled", "returned"]),
                ("start_datetime", "<", booking.end_datetime),
                ("end_datetime", ">", booking.start_datetime),
                ("equipment_ids", "in", booking.equipment_ids.ids),
            ]
            if self.search_count(domain):
                raise models.ValidationError("Booking conflict: One or more items are already booked for this period.")

    def action_request(self):
        self.write({"state": "requested"})

    def action_approve(self):
        for booking in self:
            booking.state = "approved"
            booking.equipment_ids.write({"status": "reserved"})

    def action_check_out(self):
        for booking in self:
            booking.state = "checked_out"
            booking.equipment_ids.write({
                "status": "checked_out",
                "current_custodian_id": booking.requester_id.partner_id.id,
            })

    def action_return(self):
        for booking in self:
            booking.state = "returned"
            booking.equipment_ids.write({
                "status": "available",
                "current_custodian_id": False,
            })

    def action_cancel(self):
        for booking in self:
            booking.state = "cancelled"
            if booking.equipment_ids:
                booking.equipment_ids.write({"status": "available"})

    def _cron_check_overdue_bookings(self):
        """Create activities for overdue bookings (called by cron)"""
        overdue = self.search([('is_overdue', '=', True)])
        activity_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)

        if not activity_type:
            return

        for booking in overdue:
            # Check if activity already exists for this booking
            existing = self.env['mail.activity'].search([
                ('res_id', '=', booking.id),
                ('res_model', '=', 'ipai.equipment.booking'),
                ('activity_type_id', '=', activity_type.id),
            ], limit=1)

            if not existing:
                # Create activity for the borrower
                booking.activity_schedule(
                    'mail.mail_activity_data_todo',
                    user_id=booking.borrower_id.id,
                    summary=f'Overdue: {booking.asset_id.name}',
                    note=f'Booking {booking.name} is overdue. Expected return: {booking.end_datetime.strftime("%Y-%m-%d %H:%M")}',
                )


class IpaiEquipmentIncident(models.Model):
    _name = "ipai.equipment.incident"
    _description = "IPAI Equipment Incident"
    _order = "create_date desc"

    name = fields.Char(required=True)
    booking_id = fields.Many2one("ipai.equipment.booking", string="Booking")
    equipment_id = fields.Many2one("maintenance.equipment", string="Equipment", required=True)
    reported_by = fields.Many2one("res.users", string="Reported By", required=True)
    severity = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")],
        default="low",
        required=True,
    )
    description = fields.Text()
    status = fields.Selection(
        [
            ("open", "Open"),
            ("in_progress", "In Progress"),
            ("resolved", "Resolved"),
        ],
        default="open",
        required=True,
    )
