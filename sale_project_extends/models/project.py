# -*- coding: utf-8 -*-


from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError


class ProjectStage(models.Model):
    _name = "project.project.stage"

    name = fields.Char(string="name", required=True)

class Project(models.Model):
    _inherit = "project.project"

    stage_id = fields.Many2one('project.project.stage', string="Stage")
    

    @api.depends('requisition_ids', 'picking_ids')
    def _get_requisition_count(self):
        requisition_count = 0
        picking_count = 0
        for rec in self:
            if rec.requisition_ids:
                requisition_count = len(rec.requisition_ids.ids)
            if rec.picking_ids:
                picking_count = len(rec.picking_ids.ids)
            rec.update({
                'requisition_count': requisition_count or 0,
                'picking_count': picking_count or 0,
            })

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
    requisition_ids = fields.One2many('po.requisition', 'project_id', string="Requisiciones")
    requisition_count = fields.Integer('Requisition Count', compute="_get_requisition_count")
    project_requisition_lines_ids = fields.One2many('project.requisition.lines', 'project_id', string="Productos requeridos")
    sale_id = fields.Many2one('sale.order', 'Pedido de Venta', readonly=True)
    stock_location_id = fields.Many2one('stock.location', 'Ubicacion', required=False)
    picking_ids = fields.One2many('stock.picking', 'project_id', string="Transferencias")
    picking_count = fields.Integer('Picking Count', compute="_get_requisition_count")

    def action_requisition_view(self):
        context = dict(self.env.context or {})
        action = self.env.ref('requisitions.po_requisition_action')
        result = action.read()[0]
        requisition_ids = self.mapped('requisition_ids')
        if not requisition_ids or len(requisition_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % (requisition_ids.ids)
        elif len(requisition_ids) == 1:
            res = self.env.ref('requisitions.po_requisition_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = requisition_ids.id
        #if len(self) == 1:
        context.update({
            'default_project_id': self.ids[0],
        })
        action['context'] = context
        return result

    def action_view_picking(self):
        action = self.env.ref('stock.action_picking_tree_all')
        result = action.read()[0]
        result['context'] = {'default_partner_id': self.partner_id.id, 'default_origin': self.name}
        pick_ids = self.mapped('picking_ids')
        if not pick_ids or len(pick_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % (pick_ids.ids)
        elif len(pick_ids) == 1:
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pick_ids.id
        return result

    def action_create_requisition(self):
        lines = []
        view = self.env.ref('sale_project_extends.wizard_requisitions_form')
        new_id = self.env['wizard.requisitions']
        for line in self.project_requisition_lines_ids:
            if line.quantity_available > 0.00:
                item = {
                    'product_id': line.product_id.id or False,
                    'name': line.name,
                    'product_uom': line.product_uom.id or False,
                    'quantity': line.quantity_available,
                    'quantity_request': 0.00,
                }
                lines.append((0, 0, item))
        if lines:
            vals = {
                'project_id': self.ids[0] or False,
                'lines_ids': lines,
                }
            #raise UserError(('%s') %(vals))
            view_id = new_id.create(vals)
        else:
            raise UserError(('No hay cantidades disponibles para realizar requesiciones'))
        return {
            'name': _("Crear Requisicion de compra"),
            'view_mode': 'form',
            'view_id': view.id,
            'res_id': view_id.id,
            'view_type': 'form',
            'res_model': 'wizard.requisitions',
            'type': 'ir.actions.act_window',
            'target': 'new',
           
        }

class Task(models.Model):
    _inherit = "project.task"

    product_tmpl_id = fields.Many2one('product.template', string='Product', domain=[('is_task', '=', True)])

    @api.onchange('product_tmpl_id')
    def _onchange_product_tmpl(self):
        if not self.product_tmpl_id:
            return
        self.name = self.product_tmpl_id.name.upper()
Task()

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    cost_unit = fields.Float('Costo Unitario',)
    subtotal_cost = fields.Float('Subtotal', compute="_compute_service_cost_subtotal")
    is_pay = fields.Boolean('Pagada', default=False)

    @api.depends( 'cost_unit', 'unit_amount')
    def _compute_service_cost_subtotal(self):
        subtotal_amount = 0.00
        for line in self:
            subtotal_amount = (line.unit_amount * line.cost_unit)
            line.update({
                'subtotal_cost': subtotal_amount or 0.00,
            })
AccountAnalyticLine()

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def action_calculate_labour_cost(self):
        view = self.env.ref('sale_project_extends.wizard_calculate_labour_cost')
        new_id = self.env['wizard.labour.cost']
        for rec in self:
            lines_ids = self.get_tasks(rec)
            vals = {
                'payslip_id': rec.id,
                'task_ids': lines_ids.ids or False,
            }
            view_id = new_id.create(vals)
            return {
                'name': _("Mano de Obra"),
                'view_mode': 'form',
                'view_id': view.id,
                'res_id': view_id.id,
                'view_type': 'form',
                'res_model': 'wizard.labour.cost',
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
    
    def get_tasks(self, payslip):
        tasks_obj = self.env['account.analytic.line']
        lines_ids = []
        if payslip:
            #if not payslip.employee_id and not payslip.employee_id.user_id:
            #    raise UserError(('El empleado no tiene usuario de sistema asignado'))
            lines_ids = tasks_obj.search([
                ('date', '>=', payslip.date_from),
                ('date', '<=', payslip.date_to),
                ('employee_id', '=', payslip.employee_id.id)
            ], order="date")
        return lines_ids


HrPayslip()