from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    resources_ids = fields.One2many('project.task.resource', 'task_id', 'Recursos')
