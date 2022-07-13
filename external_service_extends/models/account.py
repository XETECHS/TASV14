# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    timesheet_invoice_ticket_id = fields.Many2one('project.tasks.service.ticket', string="Service Ticket", readonly=True, copy=False)