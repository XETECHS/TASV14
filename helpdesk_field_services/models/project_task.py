from odoo import _, api, fields, models

class ProjectTask(models.Model):
    _inherit = 'project.task'
    _description = 'Project Task'

    supervisor_id = fields.Many2one('res.partner', string='Supervisor', related="helpdesk_ticket_id.supervisor_id")
