from odoo import _, api, fields, models

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'
    _description = 'Helpdesk Ticket'

    supervisor_id = fields.Many2one('res.partner', string='Supervisor')

    