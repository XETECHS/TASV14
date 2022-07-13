# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'Sale Order'

    supervisor_id = fields.Many2one('res.users', string='Supervisor', related="team_id.user_id", readonly=True)
