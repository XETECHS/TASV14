from odoo import api, fields, models
from odoo.exceptions import AccessError, ValidationError, MissingError, UserError


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.model
    def create(self, vals_list):
        if vals_list.get('tipo_visita') == 'gratuita' and vals_list.get('project_id'):
            project = self.env['project.project'].search([('id', '=', vals_list['project_id'])], limit=1)
            if project:
                external_service = self.env['sale.subscription'].search([('project_id', '=', project.id)], limit=1)
                if external_service and external_service.visitas_gratuitas_restantes <= 0 and not self.env.user.has_group('sale_subscription_extends.group_visitas_gratuitas_approve'):
                    raise UserError(
                        "No hay visitas gratuitas restantes," +
                        " por favor comunicate con un encargado para agregar mas visitas al proyecto."
                    )
        res = super(ProjectTask, self).create(vals_list)
        return res
    
    def write(self, values):
        if self._origin.tipo_visita != 'gratuita' and values.get('tipo_visita') == 'gratuita':
            project = self.env['project.project'].search([('id', '=', self.project_id.id)], limit=1)
            if project:
                external_service = self.env['sale.subscription'].search([('project_id', '=', project.id)], limit=1)
                if external_service and external_service.visitas_gratuitas_restantes <= 0 and not self.env.user.has_group('sale_subscription_extends.group_visitas_gratuitas_approve'):
                    raise UserError(
                        "No hay visitas gratuitas restantes," +
                        " por favor comunicate con un encargado para agregar mas visitas al proyecto."
                    )
        res = super(ProjectTask, self).write(values)

    sale_subscription_visitas_id = fields.Many2one('sale.subscription')
