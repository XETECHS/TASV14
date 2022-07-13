from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    per_diem_ids = fields.One2many('project.task.per.diem', 'task_id', 'Viaticos')
