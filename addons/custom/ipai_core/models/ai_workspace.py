from odoo import api, fields, models, _


class AIWorkspace(models.Model):
    """AI-powered workspace connector for knowledge management."""

    _name = "ipai.ai.workspace"
    _description = "AI Workspace"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(required=True, index=True, tracking=True)
    active = fields.Boolean(default=True)
    description = fields.Text()

    # Polymorphic attachment (can attach to any model)
    res_model = fields.Char(string="Model", index=True)
    res_id = fields.Integer(string="Record ID", index=True)

    # Configuration
    enable_vector_search = fields.Boolean(
        default=True, help="Enable semantic search using pgvector embeddings"
    )
    enable_llm_chat = fields.Boolean(
        default=True, help="Enable AI chat based on workspace context"
    )
    llm_provider = fields.Selection(
        [
            ("openai", "OpenAI"),
            ("anthropic", "Anthropic"),
            ("local", "Local Model"),
        ],
        default="openai",
        help="LLM provider for AI features",
    )

    # Statistics
    page_count = fields.Integer(compute="_compute_page_count", store=False)
    query_count = fields.Integer(compute="_compute_query_count", store=False)
    last_query_date = fields.Datetime(readonly=True)

    @api.depends()
    def _compute_page_count(self):
        """Placeholder for page count - implemented in ipai_knowledge_ai."""
        for workspace in self:
            workspace.page_count = 0

    @api.depends()
    def _compute_query_count(self):
        """Placeholder for query count - implemented in ipai_knowledge_ai."""
        for workspace in self:
            workspace.query_count = 0


class AIWorkspaceContext(models.AbstractModel):
    """Mixin to add AI workspace capability to any model."""

    _name = "ipai.ai.workspace.mixin"
    _description = "AI Workspace Mixin"

    ai_workspace_id = fields.Many2one(
        "ipai.ai.workspace",
        string="AI Workspace",
        help="Associated AI workspace for knowledge management",
    )

    def action_create_workspace(self):
        """Create AI workspace for this record."""
        self.ensure_one()
        if self.ai_workspace_id:
            return self.ai_workspace_id.get_formview_action()

        workspace = self.env["ipai.ai.workspace"].create(
            {
                "name": f"{self._description}: {self.display_name}",
                "res_model": self._name,
                "res_id": self.id,
            }
        )
        self.ai_workspace_id = workspace
        return workspace.get_formview_action()

    def action_open_workspace(self):
        """Open associated AI workspace."""
        self.ensure_one()
        if not self.ai_workspace_id:
            return self.action_create_workspace()
        return self.ai_workspace_id.get_formview_action()
