# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    @api.model
    def update_task_type(self):
        sec_1 = self.env['project.task.type'].search([('name', '=', 'Equipo Completo Bodega')])
        if sec_1:
            sec_1[0].write({'sequence': 50})
        sec_2 = self.env['project.task.type'].search([('name', '=', 'Creado Esperando Inicio')])
        if sec_2:
            sec_2[0].write({'sequence': 1})
