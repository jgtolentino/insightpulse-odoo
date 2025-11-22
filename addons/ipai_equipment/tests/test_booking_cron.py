# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo import fields


class TestIpaiEquipmentBooking(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Asset = self.env["ipai.equipment.asset"]
        self.Booking = self.env["ipai.equipment.booking"]

        self.asset = self.Asset.create({
            "name": "Test Camera #1",
            "status": "available",
        })

        self.user = self.env.ref("base.user_admin")

    def test_booking_lifecycle_and_overdue(self):
        """Test booking lifecycle and overdue notification system"""
        booking = self.Booking.create({
            "asset_id": self.asset.id,
            "borrower_id": self.user.id,
            "start_datetime": fields.Datetime.now(),
            "end_datetime": fields.Datetime.now(),
        })

        # Verify booking sequence generation (EQB prefix)
        self.assertTrue(booking.name.startswith("EQB"))

        # Test state transitions
        booking.action_reserve()
        booking.action_check_out()
        self.assertEqual(booking.asset_id.status, "checked_out")

        # Force overdue condition
        booking.end_datetime = fields.Datetime.subtract(
            fields.Datetime.now(), days=1
        )
        booking.is_overdue = True

        # Run cron job
        self.Booking._cron_check_overdue_bookings()

        # Verify activity created
        activities = booking.activity_ids.filtered(
            lambda a: a.activity_type_id.xml_id == "mail.mail_activity_data_todo"
        )
        self.assertTrue(activities)
