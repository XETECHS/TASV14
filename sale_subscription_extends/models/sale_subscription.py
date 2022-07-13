from odoo import api, fields, models

class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    def _set_visitas_gratuitas_restantes(self):
        for data in self:
            data.visitas_gratuitas_restantes = data.visitas_gratuitas - data.visitas_gratuitas_utilizadas

    def _total_visitas(self):
        for data in self:
            data.total_visitas = 0
            data.visitas_gratuitas_utilizadas = 0
            data.visitas_realizadas = False
            if data.project_id:
                final_stages = self.env['project.task.type'].search([('is_closed', '=', True)])
                if final_stages:
                    done_tasks = self.env['project.task'].search(
                        [
                            ('project_id', '=', data.project_id.id),
                            ('stage_id', 'in', final_stages.mapped('id')),
                            ('tipo_visita', 'in', ['a_facturar','gratuita'])
                        ]
                    )

                    done_free_tasks = self.env['project.task'].search(
                        [
                            ('project_id', '=', data.project_id.id),
                            ('stage_id', 'in', final_stages.mapped('id')),
                            ('tipo_visita', '=', 'gratuita')
                        ]
                    )
                    data.total_visitas = len(done_tasks)
                    data.visitas_realizadas = done_tasks
                    data.visitas_gratuitas_utilizadas = len(done_free_tasks)

    project_id = fields.Many2one('project.project')
    fecha_final = fields.Date('Fecha Final')
    visitas_gratuitas = fields.Integer('Visitas Gratuitas', help="Cantidad de visitas permitidas por suscripcion")
    total_visitas = fields.Integer('Cantidad de visitas realizadas', readonly=True, compute="_total_visitas")
    visitas_gratuitas_utilizadas = fields.Integer('Visitas gratuitas realizadas', readonly=True, compute="_total_visitas")
    visitas_realizadas = fields.One2many('project.task', 'sale_subscription_visitas_id', string="Visitas Realizadas", compute="_total_visitas")
    visitas_gratuitas_restantes = fields.Integer('Visitas gratuitas restantes', compute="_set_visitas_gratuitas_restantes")
    beneficios = fields.Text('Beneficios')
    definiciones = fields.Text('Definiciones')
    especificaciones = fields.Text('Especificaciones del Servicio')
