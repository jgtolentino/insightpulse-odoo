# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo import fields


class TestIpaiExpenseOCR(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Expense = self.env["ipai.expense"]
        self.user = self.env.ref("base.user_admin")

    def test_expense_ocr_fields_exist_and_flow(self):
        """Test expense OCR field schema and workflow"""
        expense = self.Expense.create({
            "employee_id": self.user.employee_id.id if self.user.employee_id else False,
            "description": "Test OCR meal",
            "date": fields.Date.today(),
            "amount": 0.0,
        })

        # Make sure OCR-related fields exist (schema sanity check)
        for field in ["ocr_status", "ocr_vendor_detected", "ocr_amount_detected"]:
            self.assertIn(field, self.Expense._fields, f"Field {field} should exist in ipai.expense model")

        # Simulate OCR completion (you can later replace this with real HTTP stub)
        expense.write({
            "ocr_status": "processed",
            "ocr_vendor_detected": "Test Vendor",
            "ocr_amount_detected": 123.45,
        })

        self.assertEqual(expense.ocr_status, "processed")
        self.assertEqual(expense.ocr_vendor_detected, "Test Vendor")
        self.assertEqual(expense.ocr_amount_detected, 123.45)
