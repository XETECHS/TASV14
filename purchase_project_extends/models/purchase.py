# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError, AccessError
from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"


    requisition_id = fields.Many2one('po.requisition', 'Requisicion', required=False)
    project_id = fields.Many2one('project.project', 'Proyecto', related="requisition_id.project_id", required=False)
    customer_id = fields.Many2one('res.partner', 'Cliente', related="project_id.partner_id", required=False)
    is_internal = fields.Boolean('¿Es interna?', default=False)

    def action_view_invoice(self):
        action = super(PurchaseOrder, self).action_view_invoice()
        action['context']['default_is_internal'] = self.is_internal
        return action

    @api.onchange('partner_id', 'requisition_id')
    def _onchange_partner_requisition(self):
        supplier_info_obj = self.env['product.supplierinfo']
        po_lines = []
        for po in self:
            if po.order_line:
                po.order_line.unlink()
            for line in po.requisition_id.order_line:
                count = supplier_info_obj.search([('name', '=', po.partner_id.id), ('product_tmpl_id', '=', line.product_id.product_tmpl_id.id)])
                if len(count.ids) > 0:
                    lines = {
                        'requisition_line_id': line.id,
                        'product_id': line.product_id.id or False,
                        'name': line.product_id.name or "",
                        'date_planned': line.order_id.delivery_date or fields.Datetime.now,
                        'product_qty': line.quantity_available,
                        'product_uom': line.product_uom.id or False,
                        'price_unit': line.price_unit,
                        'taxes_id': line.product_id.supplier_taxes_id.ids,
                        'account_analytic_id': line.order_id.project_id.analytic_account_id.id or False,
                        'analytic_tag_ids': line.analytic_tag_ids.ids,
                    }
                    po_lines.append((0,0,lines))
            po.order_line = po_lines

PurchaseOrder()

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    requisition_line_id = fields.Many2one('requisition.order.line', 'Req. Line', readonly=False, required=False)
    analytic_account_id = fields.Many2one(string="Cuenta analitica", comodel_name="account.analytic.account")
    analytic_tag_ids = fields.Many2many("account.analytic.tag", string="Etiquetas analiticas")


    def _prepare_stock_moves(self, picking):
        res = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        for move in res:
            move.update({
                'analytic_account_id': self.account_analytic_id.id or False,
            })
        return res

PurchaseOrderLine()