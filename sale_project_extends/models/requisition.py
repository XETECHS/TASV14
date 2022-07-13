# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Requisition(models.Model):
    _inherit = "po.requisition"

    sale_id = fields.Many2one('sale.order', string='Sale Order', required=False)
    sale_ids = fields.Many2many('sale.order', string="Ordenes de ventas", required=False)
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
    state  = fields.Selection(selection_add=[('confirm', 'Confirmado')])
    is_blocked = fields.Boolean('Bloquear', compute="_compute_blocked")

    @api.depends('project_id', 'sale_ids')
    def _compute_blocked(self):
        for rec in self:
            if self.env.user.has_group('sale_project_extends.group_edit_requisition_lines'):
                rec.is_blocked = True
            else:
                rec.is_blocked = False

    @api.onchange('project_id')
    def onchange_project_id(self):
        sale_obj = self.env['sale.order']
        tags_ids = []
        analytic_ids = []
        if self.project_id:
            sale_ids = sale_obj.search([('project_id', '=', self.project_id.id)])
            if sale_ids:
                self.sale_ids = sale_ids.ids
    
    @api.onchange('sale_ids')
    def onchange_sales(self):
        lines = []
        if self.sale_ids:
            for sale in self.sale_ids:
                for line in sale.order_line:
                    if line.service_cost_id and line.service_cost_id.cost_line_ids:
                        for l in line.service_cost_id.cost_line_ids:
                            if l.product_tmpl_id.type != 'service':
                                res = {
                                    'product_id': l.product_tmpl_id.id or False,
                                    'product_qty': l.product_qty or 0.00,
                                    'product_uom': l.product_tmpl_id.uom_id.id or False, 
                                    'available': l.product_qty,
                                    #'total': line.price, 
                                    'analytic_tag_ids': line.analytic_tag_ids.ids,
                                }
                                lines.append((0,0, res))
                    else:
                        if line.product_id.type == 'product':
                            res = {
                                'product_id': line.product_id,
                                'product_qty': line.product_uom_qty,
                                'product_uom': line.product_id.uom_id, 
                                'available': line.product_uom_qty,
                                'total': line.price_subtotal, 
                                'analytic_tag_ids': line.analytic_tag_ids.ids,
                            }
                            lines.append((0,0, res))
                self.update({
                    'is_blocked': True,
                    'order_line': lines,
                })

Requisition()

class RequisitionOrderLine(models.Model):
    _inherit = 'requisition.order.line'

    total = fields.Float('Total',)
    available = fields.Float('Disponible')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')

    @api.onchange('product_id')
    def _compute_total(self):
        self.total = self._get_total()

    def _get_total(self):
        total = 0
        for line in self.order_id.sale_id.order_line:
            if line.product_id.id == self.product_id.id:
                total = line.product_uom_qty
        return total

    @api.onchange('product_id', 'total', 'product_uom', 'product_qty')
    def _compute_available(self):
        self.available = self._get_total()
        requisitions = self.env['po.requisition'].search([('state', '=', 'approve')])
        for requisition in requisitions:
            for line in requisition.order_line:
                if line.product_id.id == self.product_id.id:
                    self.available -= line.product_qty
        self.available = max(0, self.available)

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.product_uom = self.product_id.product_tmpl_id.uom_id

    @api.model
    def create(self, values):
        rfq = self.env['po.requisition'].search([('id', '=', values['order_id'])])
        values['total'] = 0
        for line in rfq.sale_id.order_line:
            if line.product_id.id == values['product_id']:
                values['total'] = line.product_uom_qty

        requisitions = self.env['po.requisition'].search([('state', '=', 'approve')])
        values['available'] = values['total']
        for requisition in requisitions:
            for line in requisition.order_line:
                if line.product_id.id == values['product_id']:
                    values['available'] -= line.product_qty
        values['available'] = max(0, values['available'])

        return super(RequisitionOrderLine, self).create(values)

RequisitionOrderLine()

class ProjectRequisitionLines(models.Model):
    _name = "project.requisition.lines"
    _description = "Requisition Lines in Project"

    project_id = fields.Many2one('project.project', 'Proyecto', ondelete="cascade")
    product_id = fields.Many2one('product.product', 'Producto', required=True)
    name = fields.Text('Descripcion', required=True)
    quantity = fields.Float('Cantidad', required=True)
    product_uom = fields.Many2one('uom.uom', 'Unidad de medida', required=True)
    quantity_purchase = fields.Float('Requerido', compute="_compute_purchase")
    quantity_transfer = fields.Float('Transferido', compute="_compute_purchase")
    quantity_available = fields.Float('Disponible', compute="_compute_purchase")
    
    @api.depends('product_id', 'quantity')
    def _compute_purchase(self):
        quantity_purchase = 0.00
        quantity_available = 0.00
        quantity_transfer = 0.00
        for line in self:
            quantity_available = line.quantity
            quantity_purchase = 0.00
            quantity_transfer = 0.00
            for req in line.project_id.requisition_ids:
                for req_line in req.order_line:
                    if line.product_id.id == req_line.product_id.id:
                        quantity_purchase += req_line.product_qty 
            for picking in line.project_id.picking_ids:
                for move in picking.move_ids_without_package:
                    if line.product_id.id == move.product_id.id:
                        quantity_transfer += move.quantity_done

            line.update({
                'quantity_purchase': quantity_purchase or 0.00,
                'quantity_transfer': quantity_transfer or 0.00,
                'quantity_available': (quantity_available - (quantity_purchase + quantity_transfer)) or 0.00,
            })
ProjectRequisitionLines()