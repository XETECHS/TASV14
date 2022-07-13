# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models
class CrmLead(models.Model):
    _inherit = "crm.lead"
    _description = 'crm lead'

    budgets = fields.Many2one('sale.order', string="Presupuestos")
    @api.onchange('budgets')
    def _onchange_budgets(self):
        self.expected_revenue = self.budgets.amount_total