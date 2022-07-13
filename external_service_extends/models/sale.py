# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    service_task_id = fields.Many2one('project.tasks.service.ticket', 'Service Task', ondelete='cascade')