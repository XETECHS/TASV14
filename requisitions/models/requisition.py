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

    requisition_number = fields.Many2one('po.requisition', sttring='RFQ')

    #@api.onchange('requisition_number')
    #def _rfq_onchange(self):
    #    for rec in self:
    #        rec.order_line = None
    #        for line in rec.requisition_number.order_line:
    #            rec.order_line = [(0, 0, {'product_id': line.product_id, 'name': line.product_id.name,
    #                                      'product_qty': line.product_qty, 'product_uom': line.product_id.uom_id})]
    #        providers = rec.requisition_number.partner_ids.mapped(lambda x: x.id)
    #        if len(providers) == 1:
    #            rec.partner_id = providers[0]
    #        return {'domain': {'partner_id': [('id', 'in', providers)]}}


class Requisition(models.Model):
    _name = "po.requisition"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "Purchase Requisitions"

    name = fields.Char('PO Requisition')
    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Almacen', required=False)
    project_id = fields.Many2one(
        'project.project', string='Proyecto', required=True,
        states={'cancel': [('readonly', True)], 'approve': [('readonly', True)]}, default=False)
    delivery_date = fields.Datetime(
        string='Fecha estimada de Entrega', required=True, index=True)
    po_reference = fields.Many2one('purchase.order', string='Pedido de compra', domain="[('state', '=', 'purchase')]")
    solicited_by = fields.Many2one('hr.employee', 'Solicitado Por', required=False, help="Solicitante de la requisición")
    notes = fields.Text('Observaciones')
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirm', 'Confirmada'),
        ('approve', 'Aprobada'),
        ('cancel', 'Cancelada')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    partner_id = fields.Many2one('res.partner', string='Proveedor', required=False,
                                 help="You can find a vendor by its Name, TIN, Email or Internal Reference.")
    order_line = fields.One2many('requisition.order.line', 'order_id', string='Order Lines', states={
        'cancel': [('readonly', True)], 'approve': [('readonly', True)]}, copy=True)
    purchase_order_ids = fields.Many2many('purchase.order', string='Compras')
    partner_ids = fields.Many2many('res.partner', string="Proveedores", readonly=False)

    @api.onchange('purchase_order_ids')
    def onchange_purchases(self):
        vendors = []
        if self.purchase_order_ids:
            for po in self.purchase_order_ids:
                vendors.append((4, po.partner_id.id, None))
            self.partner_ids = vendors

    @api.onchange('po_reference')
    def on_change_po_reference(self):
        self.order_line = None
        if self.po_reference and len(self.po_reference) > 0:
            self.order_line = [{'product_id': self.po_reference[0].product_id, 'product_qty': 1.00}]

    def action_approve_po_requisition(self):
        for req in self:
            req.activity_schedule('requisitions.mail_act_requisition_upsell',
                        user_id= self.env.user.id,
                        note=_("Aprobacion <a href='#' data-oe-model='%s' data-oe-id='%d'>%s</a> para el proyecto <a href='#' data-oe-model='%s' data-oe-id='%s'>%s</a>") % (
                            req._name, req.id, req.name,
                            req.project_id._name, req.project_id.id, req.project_id.name))
            req.write({'state': 'approve'})
        return {}

    def action_confirm(self):
        return self.write({'state': 'confirm'})


    @api.model
    def create(self, values):

        record = super(Requisition, self).create(values)
        record.name = "REQ0" + str(record.id)

        return record


class RequisitionOrderLine(models.Model):
    _name = 'requisition.order.line'
    _description = 'Requisition Order Line'

    order_id = fields.Many2one(
        'po.requisition', string='Order Reference', index=True, required=True, ondelete='cascade')
    name = fields.Text(string='Description')
    product_id = fields.Many2one('product.product', string='Product', domain=[
        ('purchase_ok', '=', True)], change_default=True, required=True)
    product_qty = fields.Float(string='Quantity', digits=dp.get_precision(
        'Product Unit of Measure'), required=True)

    product_uom = fields.Many2one(
        'uom.uom', string='Product Unit of Measure', required=True)
    price_unit = fields.Float(string='Price', digits=dp.get_precision(
        'Product Price'))


# Odoo 12: Error, a partner cannot follow twice the same object
class Followers(models.Model):
    _inherit = 'mail.followers'

    @api.model
    def create(self, vals):
        if 'res_model' in vals and 'res_id' in vals and 'partner_id' in vals:
            dups = self.env['mail.followers'].search(
                [('res_model', '=', vals.get('res_model')), ('res_id', '=', vals.get('res_id')),
                 ('partner_id', '=', vals.get('partner_id'))])

            if len(dups):
                for p in dups:
                    p.unlink()

        res = super(Followers, self).create(vals)

        return res
