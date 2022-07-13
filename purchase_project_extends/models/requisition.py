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


class PurchaseRequisition(models.Model):
    _inherit = "po.requisition"

    purchase_complete = fields.Boolean('Completa', readonly=True)
    purchase_ids = fields.One2many('purchase.order', 'requisition_id', 'Compras')
    purchase_count = fields.Integer(compute='_compute_purchase', string='Compras', default=0, store=True)

    @api.depends('purchase_ids')
    def _compute_purchase(self):
        for order in self:
            order.purchase_count = len(order.purchase_ids.ids)

    def action_purchase(self):
        purchase_obj = self.env['purchase.order']
        res_line_obj = self.env['requisition.order.line']
        po_line = []
        for req in self:
            lines = self.group_by_suppliers(req.order_line)
            for key, items in lines.items():
                po_line = []
                for line in res_line_obj.browse(items):
                    if line.quantity_available > 0.00:
                        lines = {
                            'product_id': line.product_id.id or False,
                            'product_qty': line.quantity_available or 0.00,
                            'product_uom': line.product_uom.id or False,
                            'price_unit': line.product_id.standard_price or 1.00,
                            'date_planned': req.delivery_date or fields.Datetime.now,
                            'requisition_line_id': line.id,
                            'name': line.product_id.name,
                            'taxes_id': line.product_id.supplier_taxes_id.ids,
                            'account_analytic_id': line.order_id.project_id.analytic_account_id.id or False,
                            'analytic_tag_ids': line.analytic_tag_ids.ids,
                        }
                        po_line.append((0,0,lines))
                if po_line:
                    po = {
                        'partner_id': key or False,
                        'state': 'draft',
                        'requisition_id': req.id or False,
                        'order_line': po_line,
                        'partner_ref': req.name,
                        'origin': req.name,
                    }
                    purchase_obj.create(po)
                elif not po_line:
                    req.write({'purchase_complete': True})
                    raise UserError(('Ya no hay lineas para comprar en la requisicion %s') %(req.name))
        return self.action_view_purchases()

    def group_by_suppliers(self, order_lines):
        lines_dict = {}
        for line in order_lines:
            if not line.supplier_id:
                raise UserError(('El producto %s no tiene proveedor asignado') %(line.product_id.name))
            if line.supplier_id.id not in lines_dict:
                lines_dict[line.supplier_id.id] = []
            lines_dict[line.supplier_id.id].append(line.id)
        return lines_dict
    
    def action_view_purchases(self):
        action = self.env.ref('purchase.purchase_rfq')
        result = action.read()[0]
        # override the context to get rid of the default filtering on operation type
        #result['context'] = {'default_partner_id': self.partner_id.id, 'default_origin': self.name,}
        purchase_ids = self.mapped('purchase_ids')
        # choose the view_mode accordingly
        if not purchase_ids or len(purchase_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % (purchase_ids.ids)
        elif len(purchase_ids) == 1:
            res = self.env.ref('purchase.purchase_order_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = purchase_ids.id
        return result

PurchaseRequisition()

class RequisitionOrderLine(models.Model):
    _inherit = 'requisition.order.line'

    @api.depends('product_id', 'product_qty')
    def _compute_purchase(self):
        purchase_line_obj = self.env['purchase.order.line']
        quantity_purchase = 0.00
        quantity_available = 0.00
        for line in self:
            quantity_available = line.product_qty
            quantity_purchase = 0.0
            lines_ids = purchase_line_obj.search([('requisition_line_id', '=', line.id), ('product_id', '=', line.product_id.id), ('state', '!=', ('cancel'))])
            for po_line in lines_ids:
                quantity_purchase += po_line.product_qty 
            line.update({
                'quantity_purchase': quantity_purchase or 0.00,
                'quantity_available': (quantity_available - quantity_purchase) or 0.00,
            })

    quantity_purchase = fields.Float('Comprado', compute="_compute_purchase")
    quantity_available = fields.Float('Disponible', compute="_compute_purchase")
    supplier_id = fields.Many2one('res.partner', 'Proveedor')

    @api.depends('product_id')
    def _get_supplier(self):
        supplier_id = False
        for rec in self:
            supplier_id = False
            if rec.product_id and rec.product_id.seller_ids:
                for seller in rec.product_id.seller_ids:
                    #if seller.sequence == 1:
                    supplier_id = seller.name.id
            rec.update({
                'supplier_id': supplier_id or False,
            })
RequisitionOrderLine()