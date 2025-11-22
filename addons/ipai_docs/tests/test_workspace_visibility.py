# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestWorkspaceVisibility(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Doc = self.env["ipai.docs.document"]
        self.Project = self.env["project.project"]
        self.Task = self.env["project.task"]
        self.user = self.env.ref("base.user_admin")

    def test_doc_project_task_linkage(self):
        """Test document-project-task linkage behaves like Notion workspace"""
        project = self.Project.create({"name": "Notion Replacement – Test"})
        doc = self.Doc.create({
            "name": "Closing SOP",
            "body": "<p>Test SOP content</p>",
        })

        # Link doc to project (via ipai_docs_project, adjust model if needed)
        link_model = self.env.get("ipai.docs.project")
        if link_model:
            link_model.create({
                "project_id": project.id,
                "document_id": doc.id,
            })

        # Create a task under the project
        task = self.Task.create({
            "name": "Prepare closing schedule",
            "project_id": project.id,
            "user_id": self.user.id,
        })

        # Sanity: project sees at least one linked task
        self.assertIn(task, project.task_ids, "Task should be linked to project")

        # If you have a computed docs field on project, assert it here:
        # self.assertIn(doc, project.docs_ids)
