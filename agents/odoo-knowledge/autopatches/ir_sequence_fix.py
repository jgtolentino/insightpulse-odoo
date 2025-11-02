"""
Auto-Patch: Invoice Numbering Sequence Fix
Category: accounting
Guardrail: GR-ACCT-002

Replaces hardcoded invoice numbering with proper ir.sequence usage.
"""

from odoo import models, api

class AccountMoveSequenceFix(models.Model):
    _inherit = 'account.move'

    @api.model
    def _get_sequence_prefix(self, code, company_id=None):
        """Get proper sequence for invoice numbering"""
        if not company_id:
            company_id = self.env.company.id

        return self.env['ir.sequence'].next_by_code(
            code,
            company_id=company_id
        ) or '/'

    def _compute_display_name(self):
        """Override to use ir.sequence instead of hardcoded logic"""
        for move in self:
            if move.state == 'draft':
                move.display_name = '/'
            else:
                # Use proper sequence
                if not move.name or move.name == '/':
                    if move.move_type == 'out_invoice':
                        move.name = self._get_sequence_prefix('account.move.out_invoice')
                    elif move.move_type == 'in_invoice':
                        move.name = self._get_sequence_prefix('account.move.in_invoice')
                    else:
                        move.name = self._get_sequence_prefix('account.move')

                move.display_name = move.name

# Data file to create sequence if missing:
# <data noupdate="1">
#     <record id="sequence_invoice_custom" model="ir.sequence">
#         <field name="name">Custom Invoice Sequence</field>
#         <field name="code">account.move.out_invoice</field>
#         <field name="prefix">INV/%(year)s/</field>
#         <field name="padding">5</field>
#         <field name="company_id" ref="base.main_company"/>
#     </record>
# </data>
