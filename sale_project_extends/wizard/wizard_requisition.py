# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError
from datetime import datetime, timedelta

import math
from collections import defaultdict


class WizardRequisition(models.TransientModel):
    _name = "wizard.requisitions"

    @api.model
    def _default_warehouse_id(self):
        company = self.env.company.id
        warehouse_ids = self.env['stock.warehouse'].search([('company_id', '=', company)], limit=1)
        return warehouse_ids

    project_id = fields.Many2one('project.project', 'Proyecto', readonly=True)
    lines_ids = fields.One2many('wizard.requisitions.lines', 'wizard_id', 'Lineas')
    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Almacen',
        required=False, readonly=False,
        default=_default_warehouse_id)

    def action_create(self):
        picking_obj = self.env['stock.picking']
        req_obj = self.env['po.requisition']
        lines = []
        picking_moves = []
        for rec in self:
            if not rec.project_id:
                raise UserError(('No hay proyecto asignado'))
            for l in rec.lines_ids:
                if not l.product_id:
                    raise UserError(('No se pueden procesar lineas sin producto'))
                if l.quantity_request == 0.00:
                    raise UserError(('No se pueden procesar lineas con cantidades a 0.00'))
                if l.qty_available_today > 0.00 and l.qty_available_today >= l.quantity_request:
                    picking_type = self.env['stock.picking.type'].search([('code', '=', 'internal'), ('warehouse_id', '=', rec.warehouse_id.id)])
                    move = {
                        'name': l.name,
                        'product_id': l.product_id.id,
                        'product_uom': l.product_id.uom_id.id,
                        'product_uom_qty': l.quantity_request,
                        'date': fields.Date.today(),
                        'date_expected': fields.Date.today(),
                        'picking_type_id': picking_type.id,
                        'location_id': picking_type.default_location_src_id.id,
                        'location_dest_id': rec.project_id.stock_location_id.id,
                        'partner_id': rec.project_id.partner_id.id,
                        'state': 'draft',
                    }
                    picking_moves.append((0,0,move))
                elif l.qty_available_today > 0.00 and l.qty_available_today < l.quantity_request:
                    picking_type = self.env['stock.picking.type'].search([('code', '=', 'internal'), ('warehouse_id', '=', rec.warehouse_id.id)])
                    move = {
                        'name': l.name,
                        'product_id': l.product_id.id,
                        'product_uom': l.product_id.uom_id.id,
                        'product_uom_qty': l.qty_available_today,
                        'date': fields.Date.today(),
                        'date_expected': fields.Date.today(),
                        'picking_type_id': picking_type.id,
                        'location_id': picking_type.default_location_src_id.id,
                        'location_dest_id': rec.project_id.stock_location_id.id,
                        'partner_id': rec.project_id.partner_id.id,
                        'state': 'draft',
                    }
                    picking_moves.append((0,0,move))
                    res = {
                        'product_id': l.product_id.id or False,
                        'product_qty': (l.quantity_request - l.qty_available_today) or 0.00,
                        'product_uom': l.product_id.uom_id.id or False, 
                        'analytic_tag_ids': [(6, 0, rec.project_id.analytic_tag_ids.ids)],
                    }
                    lines.append((0,0, res))
                elif l.qty_available_today <= 0.00:
                    res = {
                        'product_id': l.product_id.id or False,
                        'product_qty': (l.quantity_request - l.qty_available_today) or 0.00,
                        'product_uom': l.product_id.uom_id.id or False, 
                        'analytic_tag_ids': [(6, 0, rec.project_id.analytic_tag_ids.ids)],
                    }
                    lines.append((0,0, res))
            if lines:
                vals = {
                    'delivery_date': fields.datetime.now(),
                    'project_id': rec.project_id.id or False,
                    'sale_ids': [(6, 0 , [rec.project_id.sale_id.id])],
                    'analytic_tag_ids': [(6, 0, rec.project_id.analytic_tag_ids.ids)],
                    'order_line': lines,
                }
                req_obj.create(vals)
            if picking_moves:
                picking = self._prepare_picking()
                picking.update({
                    'move_ids_without_package': picking_moves,
                })
                picking_id = picking_obj.create(picking)
                picking_id.action_confirm()
                #picking_id.action_assign()
        return True

    def action_view_requisitions(self):
        action = self.env.ref('requisitions.po_requisition_action')
        result = action.read()[0]
        purchase_ids = self.project_id.requisition_ids
        if not purchase_ids or len(purchase_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % (purchase_ids.ids)
        elif len(purchase_ids) == 1:
            res = self.env.ref('requisitions.po_requisition_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = purchase_ids.id
        return result

    def _prepare_picking(self):
        picking_type = self.env['stock.picking.type'].search([('code', '=', 'internal'), ('warehouse_id', '=', self.warehouse_id.id)])
        if not self.project_id.partner_id.property_stock_supplier.id:
            raise UserError(_("You must set a Vendor Location for this partner %s") % self.project_id.partner_id.name)
        return {
            'picking_type_id': picking_type and picking_type.id,
            'partner_id': self.project_id.partner_id.id,
            'project_id': self.project_id.id,
            'user_id': self.env.user.id or False,
            'date': fields.Date.today(),
            'origin': self.project_id.name,
            'location_id': picking_type.default_location_src_id.id,
            'location_dest_id': self.project_id.stock_location_id.id,
            'company_id': self.env.user.company_id.id or False,
        }

WizardRequisition()

class WizardRequisitionLines(models.TransientModel):
    _name = "wizard.requisitions.lines"
    _description = "Wizard Requisitions Lines"

    wizard_id = fields.Many2one('wizard.requisitions', ondelete="cascade")
    product_id = fields.Many2one('product.product', 'Producto', required=False)
    name = fields.Text('Descripcion', required=False)
    quantity = fields.Float('Cant. Requerida', required=False, readonly=False, default=1.00)
    quantity_rounded = fields.Float('Redondeo', compute="_compute_qty_rounded")
    quantity_request = fields.Float('Cant. a Solicitar', required=False, default=1.00)
    product_uom = fields.Many2one('uom.uom', 'Unidad de medida', required=False)
    virtual_available_at_date = fields.Float(compute='_compute_qty_at_date')
    scheduled_date = fields.Datetime(compute='_compute_qty_at_date')
    free_qty_today = fields.Float(compute='_compute_qty_at_date')
    #quantity_rounded = fields.Float('Redondeo', compute="_compute_qty_at_date")
    qty_available_today = fields.Float(compute='_compute_qty_at_date')
    warehouse_id = fields.Many2one('stock.warehouse', compute='_compute_qty_at_date')

    @api.onchange('quantity', 'quantity_request', 'quantity_rounded')
    def onchange_quantity(self):
        for rec in self:
            if rec.quantity_request > rec.quantity_rounded:
                raise UserError(('No se puede solicitar mas cantidades de lo requerido'))

    @api.depends('quantity')
    def _compute_qty_rounded(self):
        amount_int = 0
        amount_decimal = 0
        amount_res = 0.00
        for line in self:
            amount_decimal, amount_int = math.modf(line.quantity)
            if amount_decimal > 0:
                amount_res = round(math.ceil(line.quantity), 2)
            else:
                amount_res = round(line.quantity, 2)
            line.update({
                'quantity_rounded': amount_res or 0.00,
            })



    @api.depends('product_id', 'quantity', 'wizard_id.warehouse_id')
    def _compute_qty_at_date(self):
        """ Compute the quantity forecasted of product at delivery date. There are
        two cases:
         1. The quotation has a commitment_date, we take it as delivery date
         2. The quotation hasn't commitment_date, we compute the estimated delivery
            date based on lead time"""
        qty_processed_per_product = defaultdict(lambda: 0)
        grouped_lines = defaultdict(lambda: self.env['wizard.requisitions.lines'])
        # We first loop over the SO lines to group them by warehouse and schedule
        # date in order to batch the read of the quantities computed field.
        for line in self:
            #if not line.display_qty_widget:
            #    continue
            line.warehouse_id = line.wizard_id.warehouse_id
            #if line.order_id.commitment_date:
            #    date = line.order_id.commitment_date
            #else:
            #    confirm_date = line.order_id.date_order if line.order_id.state in ['sale', 'done'] else datetime.now()
            date = datetime.now()
            grouped_lines[(line.warehouse_id.id, date)] |= line

        treated = self.browse()
        for (warehouse, scheduled_date), lines in grouped_lines.items():
            product_qties = lines.mapped('product_id').with_context(to_date=scheduled_date, warehouse=warehouse).read([
                'qty_available',
                'free_qty',
                'virtual_available',
            ])
            qties_per_product = {
                product['id']: (product['qty_available'], product['free_qty'], product['virtual_available'])
                for product in product_qties
            }
            for line in lines:
                line.scheduled_date = scheduled_date
                qty_available_today, free_qty_today, virtual_available_at_date = qties_per_product[line.product_id.id]
                line.qty_available_today = qty_available_today - qty_processed_per_product[line.product_id.id]
                line.free_qty_today = free_qty_today - qty_processed_per_product[line.product_id.id]
                line.virtual_available_at_date = virtual_available_at_date - qty_processed_per_product[line.product_id.id]
                qty_processed_per_product[line.product_id.id] += line.quantity
            treated |= lines
        remaining = (self - treated)
        remaining.virtual_available_at_date = False
        remaining.scheduled_date = False
        remaining.free_qty_today = False
        remaining.qty_available_today = False
        remaining.warehouse_id = False

WizardRequisitionLines()

class WizardLabourCost(models.TransientModel):
    _name = 'wizard.labour.cost'
    _description = 'Wizard to calculate labour cost'
    
    payslip_id = fields.Many2one('hr.payslip', 'Nomina', required=False)
    task_ids = fields.Many2many('account.analytic.line', 'rel_wizard_commissions', 'wizard_id', 'task_line_id', string="Mano de Obra")
    subtotal_m2 = fields.Float('Mts. Cuadrados', compute="_compute_subtotal")
    subtotal_m_lineal = fields.Float('Mts. Lineales', compute="_compute_subtotal")
    subtotal_time = fields.Float('Cant. Tiempo', compute="_compute_subtotal")
    total_lines = fields.Float('Total', compute="_compute_subtotal")


    @api.depends('task_ids', 'task_ids.unit_amount')
    def _compute_subtotal(self):
        subtotal_m2 = 0.00
        subtotal_mts = 0.00
        #subtotal_lineal = 0.00
        subtotal_hours = 0.00
        for rec in self:
            for task in rec.task_ids:
                if task.task_type == 'meters':
                    if task.mt_type == 'm':
                        subtotal_mts += task.subtotal_cost
                    elif task.mt_type == 'm2':
                        subtotal_m2 += task.subtotal_cost
                elif task.task_type == 'time':
                    subtotal_hours += task.subtotal_cost
            rec.update({
                'subtotal_m2': subtotal_m2 or 0.00,
                'subtotal_m_lineal': subtotal_mts or 0.00,
                'subtotal_time': subtotal_hours or 0.00,
                'total_lines': (subtotal_m2 + subtotal_mts + subtotal_hours) or 0.00,
            })


    def action_calculate(self):
        #amount_commission = 0.00
        for rec in self:
            if rec.task_ids:
                input_id = self.env.ref('sale_project_extends.input_labour_cost').id
                #for l in rec.task_ids:
                #amount_commission += l.subtotal_cost
                #if amount_commission:
                if rec.subtotal_m2:
                    self.env['hr.payslip.input'].create({
                        'payslip_id': rec.payslip_id.id,
                        'name': ("Subtotal Metros Cuadrados %s" %(rec.payslip_id.employee_id.name)),
                        'input_type_id': input_id,
                        'amount': rec.subtotal_m2 or 0.00,
                    })
                if rec.subtotal_m_lineal:
                    self.env['hr.payslip.input'].create({
                        'payslip_id': rec.payslip_id.id,
                        'name': ("Subtotal Metros Lineales %s" %(rec.payslip_id.employee_id.name)),
                        'input_type_id': input_id,
                        'amount': rec.subtotal_m_lineal or 0.00,
                    })
                if rec.subtotal_time:
                    self.env['hr.payslip.input'].create({
                        'payslip_id': rec.payslip_id.id,
                        'name': ("Subtotal Tiempo %s" %(rec.payslip_id.employee_id.name)),
                        'input_type_id': input_id,
                        'amount': rec.subtotal_time or 0.00,
                    })
            rec.payslip_id.compute_sheet()
        return True

WizardLabourCost()