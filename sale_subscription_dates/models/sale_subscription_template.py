from odoo import api, fields, models


class SaleSubscriptionTemplateExtends(models.Model):
    _inherit = "sale.subscription.template"

    period_dates = fields.One2many('sale.subscription.period', 'template_id', 'Periodo')
    number_periods = fields.Integer('Ctd. de Periodos', default=12)
    number_dates = fields.Integer('Frecuencia', default=1)
    days_in_periods = fields.Integer('Ctd. de Dias por Periodo', default=30)
