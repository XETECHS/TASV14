# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountPaymentInherit(models.Model):
    _inherit = 'account.payment'

    project_cliente_id = fields.Many2one('project.project', string='Proyecto')
    project_proveedor_id = fields.Many2one('project.project', string='Proyecto')

class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    project_cliente_id = fields.Many2one('project.project', string='Proyecto')
    project_proveedor_id = fields.Many2one('project.project', string='Proyecto')


class ProjectProjectInherit(models.Model):
    _inherit = 'project.project'

    def _payment_cliente_total(self):
        for data in self:
            if data.payment_cliente_ids:
                data.payment_cliente_total = sum(data.payment_cliente_ids.mapped('amount'))
            else:
                data.payment_cliente_total = 0

    def _saldo(self):
        for data in self:
            if data.sale_id:
                data.saldo = data.sale_id.amount_total - data.payment_cliente_total
            else:
                data.saldo = 0



    payment_cliente_ids = fields.One2many('account.payment', 'project_cliente_id', string='Pagos', readonly=True)
    payment_proveedor_ids = fields.One2many('account.payment', 'project_proveedor_id', string='Pagos', readonly=True)

    invoice_cliente_ids = fields.One2many('account.move', 'project_cliente_id', string='Facturas', readonly=True)
    invoice_proveedor_ids = fields.One2many('account.move', 'project_proveedor_id', string='Facturas', readonly=True)

    payment_cliente_total = fields.Float(compute="_payment_cliente_total")
    saldo = fields.Float(compute="_saldo")
