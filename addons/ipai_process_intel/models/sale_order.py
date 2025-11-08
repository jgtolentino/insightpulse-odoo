# -*- coding: utf-8 -*-
from odoo import models


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'process.intel.mixin']

    def _get_pi_process_id(self):
        """Use SO name as process ID"""
        return self.name

    def _get_pi_process_type(self):
        """Order-to-Cash process type"""
        return 'ORDER_TO_CASH'
