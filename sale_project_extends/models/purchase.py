# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    is_blocked = fields.Boolean('Bloquear', compute="_compute_blocked")

    @api.depends('product_id')
    def _compute_blocked(self):
        for rec in self:
            if self.env.user.has_group('sale_project_extends.group_edit_purchase_order_lines'):
                rec.is_blocked = True
            else:
                rec.is_blocked = False

    #@api.onchange('product_id', 'product_uom')
    #def onchange_product_id(self):
    #    self.price_unit = self.product_id.product_tmpl_id.standard_price
    #    self.product_uom = self.product_id.product_tmpl_id.uom_id
    #    self.name = self.product_id.product_tmpl_id.name