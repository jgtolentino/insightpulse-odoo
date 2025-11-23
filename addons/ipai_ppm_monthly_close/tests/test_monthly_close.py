# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase
from datetime import date
from odoo.exceptions import UserError


class TestMonthlyClose(TransactionCase):
    """Test PPM Monthly Close module for November 2025."""

    def setUp(self):
        super(TestMonthlyClose, self).setUp()
        self.MonthlyClose = self.env['ppm.monthly.close']
        self.CloseTask = self.env['ppm.close.task']
        self.CloseTemplate = self.env['ppm.close.template']

    def test_01_november_2025_date_calculations(self):
        """
        Test that November 2025 dates are calculated correctly.

        Expected:
        - close_month: 2025-11-01
        - month_end_date: 2025-11-28 (Friday - last business day)
        - prep_start_date: 2025-11-24 (Monday - C minus 3 business days)
        - review_due_date: 2025-11-25 (Tuesday)
        - approval_due_date: 2025-11-25 (Tuesday)
        """
        # Create November 2025 close
        close = self.MonthlyClose.create({
            'close_month': date(2025, 11, 1),
        })

        # Verify computed dates
        self.assertEqual(close.close_month, date(2025, 11, 1),
                        "Close month should be 2025-11-01")

        self.assertEqual(close.month_end_date, date(2025, 11, 28),
                        "Month end should be Friday, 28 Nov 2025 (last business day)")

        self.assertEqual(close.prep_start_date, date(2025, 11, 24),
                        "Prep start should be Monday, 24 Nov 2025 (C - 3 business days)")

        self.assertEqual(close.review_due_date, date(2025, 11, 25),
                        "Review due should be Tuesday, 25 Nov 2025 (S + 1 business day)")

        self.assertEqual(close.approval_due_date, date(2025, 11, 25),
                        "Approval due should be Tuesday, 25 Nov 2025 (S + 1 business day)")

        # Verify name
        self.assertEqual(close.name, "FIN CLOSE – November 2025",
                        "Display name should be formatted correctly")

        # Verify state
        self.assertEqual(close.state, 'draft',
                        "Initial state should be draft")

    def test_02_task_generation_from_templates(self):
        """Test that tasks are generated correctly from templates."""
        # Create November 2025 close
        close = self.MonthlyClose.create({
            'close_month': date(2025, 11, 1),
        })

        # Get count of active templates
        template_count = self.CloseTemplate.search_count([('active', '=', True)])

        # Generate tasks
        close.action_generate_tasks()

        # Verify task count
        self.assertEqual(len(close.task_ids), template_count,
                        f"Should create {template_count} tasks from templates")

        # Verify at least the expected templates exist
        self.assertGreaterEqual(template_count, 10,
                               "Should have at least 10 pre-configured templates")

        # Verify task dates are inherited
        for task in close.task_ids:
            self.assertEqual(task.prep_start, date(2025, 11, 24),
                           f"Task {task.name} prep_start should be 24 Nov")
            self.assertEqual(task.review_due, date(2025, 11, 25),
                           f"Task {task.name} review_due should be 25 Nov")
            self.assertEqual(task.approval_due, date(2025, 11, 25),
                           f"Task {task.name} approval_due should be 25 Nov")

        # Verify state changed to scheduled
        self.assertEqual(close.state, 'scheduled',
                        "State should be 'scheduled' after generating tasks")

    def test_03_task_workflow_states(self):
        """Test task state transitions through the workflow."""
        # Create close and generate tasks
        close = self.MonthlyClose.create({
            'close_month': date(2025, 11, 1),
        })
        close.action_generate_tasks()

        # Get first task
        task = close.task_ids[0]

        # Verify initial state
        self.assertEqual(task.state, 'todo', "Initial state should be 'todo'")

        # Start preparation
        task.action_start_prep()
        self.assertEqual(task.state, 'in_progress',
                        "State should be 'in_progress' after starting prep")

        # Submit for review
        task.action_submit_for_review()
        self.assertEqual(task.state, 'for_review',
                        "State should be 'for_review' after submitting")
        self.assertIsNotNone(task.prep_completed_date,
                           "Prep completed date should be set")

        # Submit for approval
        task.action_submit_for_approval()
        self.assertEqual(task.state, 'for_approval',
                        "State should be 'for_approval' after reviewer approves")
        self.assertIsNotNone(task.review_completed_date,
                           "Review completed date should be set")

        # Final approval
        task.action_approve()
        self.assertEqual(task.state, 'done',
                        "State should be 'done' after final approval")
        self.assertIsNotNone(task.approval_completed_date,
                           "Approval completed date should be set")

    def test_04_task_rejection_workflow(self):
        """Test that tasks can be rejected and returned to owner."""
        # Create close and generate tasks
        close = self.MonthlyClose.create({
            'close_month': date(2025, 11, 1),
        })
        close.action_generate_tasks()

        task = close.task_ids[0]

        # Progress to review
        task.action_start_prep()
        task.action_submit_for_review()

        # Reviewer rejects
        task.action_reject()
        self.assertEqual(task.state, 'in_progress',
                        "State should return to 'in_progress' after rejection")

        # Fix and resubmit
        task.action_submit_for_review()
        task.action_submit_for_approval()

        # Approver rejects
        task.action_reject()
        self.assertEqual(task.state, 'in_progress',
                        "State should return to 'in_progress' after approver rejection")

    def test_05_progress_tracking(self):
        """Test progress percentage calculation."""
        # Create close and generate tasks
        close = self.MonthlyClose.create({
            'close_month': date(2025, 11, 1),
        })
        close.action_generate_tasks()

        total_tasks = len(close.task_ids)
        self.assertGreater(total_tasks, 0, "Should have tasks")

        # Initially 0% complete
        self.assertEqual(close.progress_percentage, 0.0,
                        "Progress should be 0% with no completed tasks")

        # Complete half the tasks
        tasks_to_complete = close.task_ids[:total_tasks // 2]
        for task in tasks_to_complete:
            task.action_start_prep()
            task.action_submit_for_review()
            task.action_submit_for_approval()
            task.action_approve()

        # Refresh computed fields
        close._compute_task_stats()

        # Verify progress is approximately 50%
        expected_progress = (len(tasks_to_complete) / total_tasks) * 100
        self.assertAlmostEqual(close.progress_percentage, expected_progress, delta=1.0,
                              msg=f"Progress should be ~{expected_progress:.0f}% with {len(tasks_to_complete)} of {total_tasks} tasks done")

    def test_06_complete_close_validation(self):
        """Test that close cannot be completed with pending tasks."""
        # Create close and generate tasks
        close = self.MonthlyClose.create({
            'close_month': date(2025, 11, 1),
        })
        close.action_generate_tasks()

        # Try to complete with pending tasks
        with self.assertRaises(UserError):
            close.action_complete_close()

        # Complete all tasks
        for task in close.task_ids:
            task.action_start_prep()
            task.action_submit_for_review()
            task.action_submit_for_approval()
            task.action_approve()

        # Now should complete successfully
        close.action_complete_close()
        self.assertEqual(close.state, 'done',
                        "Close should be marked as 'done' when all tasks complete")

    def test_07_business_day_calculations(self):
        """Test business day calculation methods."""
        close = self.MonthlyClose.create({
            'close_month': date(2025, 11, 1),
        })

        # Test is_business_day
        monday = date(2025, 11, 24)
        saturday = date(2025, 11, 29)
        sunday = date(2025, 11, 30)

        self.assertTrue(close._is_business_day(monday),
                       "Monday should be a business day")
        self.assertFalse(close._is_business_day(saturday),
                        "Saturday should not be a business day")
        self.assertFalse(close._is_business_day(sunday),
                        "Sunday should not be a business day")

        # Test subtract_business_days
        # From Friday 28 Nov, subtract 3 business days = Monday 24 Nov
        friday = date(2025, 11, 28)
        result = close._subtract_business_days(friday, 3)
        self.assertEqual(result, date(2025, 11, 24),
                        "Subtracting 3 business days from Fri 28 should give Mon 24")

        # Test add_business_days
        # From Monday 24 Nov, add 1 business day = Tuesday 25 Nov
        result = close._add_business_days(monday, 1)
        self.assertEqual(result, date(2025, 11, 25),
                        "Adding 1 business day from Mon 24 should give Tue 25")

    def test_08_multi_agency_support(self):
        """Test that all 8 agencies are represented in templates."""
        # Get templates by agency
        agencies = ['RIM', 'CKVC', 'BOM', 'JPAL', 'JLI', 'JAP', 'LAS', 'RMQB']

        for agency in agencies:
            template_count = self.CloseTemplate.search_count([
                ('agency_code', '=', agency),
                ('active', '=', True)
            ])
            self.assertGreater(template_count, 0,
                             f"Should have at least one template for agency {agency}")

    def test_09_template_fields(self):
        """Test that templates have all required fields."""
        templates = self.CloseTemplate.search([('active', '=', True)], limit=1)

        if templates:
            template = templates[0]
            self.assertTrue(template.task_category,
                          "Template should have task_category")
            self.assertTrue(template.detailed_task,
                          "Template should have detailed_task")
            self.assertTrue(template.agency_code,
                          "Template should have agency_code")
            self.assertTrue(template.owner_code,
                          "Template should have owner_code")
            self.assertGreater(template.prep_days, 0,
                             "Template should have prep_days > 0")

    def test_10_cron_create_monthly_close(self):
        """Test that cron can create monthly close schedules."""
        # This would normally create for next month
        # For testing, we just verify the method exists and is callable
        result = self.MonthlyClose.cron_create_monthly_close()

        # Should return a monthly.close record
        self.assertTrue(result,
                       "Cron should create or return a monthly close record")
        self.assertEqual(result._name, 'ppm.monthly.close',
                        "Cron should return a ppm.monthly.close record")
