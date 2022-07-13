from odoo import api, fields, models


class PlanningSlot(models.Model):
    _inherit = 'planning.slot'


    planning_id = fields.Many2one('sale.subscription.dates.planning', string="Planificacion")
