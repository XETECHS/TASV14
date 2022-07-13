from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import datetime



class SaleSubscriptionPeriod(models.Model):
    _name = 'sale.subscription.period'

    template_id = fields.Many2one('sale.subscription.template', String='template')
    name = fields.Char('Nombre')
    date_from = fields.Date('Fecha Inicial')
    date_to = fields.Date('Fecha Final')
    number_dates = fields.Integer('Ctd. de Citas')


class SaleSubscriptionExtends(models.Model):
    _inherit = "sale.subscription"

    number_periods = fields.Integer('Ctd. de Periodos', related="template_id.number_periods")
    number_dates = fields.Integer('Ctd. de Citas por Periodo', related="template_id.number_dates")
    days_in_periods = fields.Integer('Ctd. de Dias por Periodo', related="template_id.days_in_periods")
    dates_ids = fields.One2many('sale.subscription.dates', 'subscription_id', 'Periodo')
    vencidas = fields.Boolean(compute="set_vencidas")
    vencidas2 = fields.Boolean()
    pendientes = fields.Boolean(compute="set_vencidas")
    pendientes2 = fields.Boolean()


    @api.depends('dates_ids')
    def set_vencidas(self):
        for data in self:
            data.vencidas = False
            data.vencidas2 = False
            data.pendientes = False
            data.pendientes2 = False
            if True in data.dates_ids.mapped('vencidas'):
                data.vencidas = True
                data.vencidas2 = True
            if True in data.dates_ids.mapped('pendientes'):
                data.pendientes = True
                data.pendientes2 = True


    @api.onchange('date_start', 'number_periods', 'number_dates', 'days_in_periods')
    def _create_subscription_dates(self):
        for rec in self:
            rec.dates_ids = [(5, 0, 0)]


            if rec.date_start and rec.number_periods and rec.number_dates and rec.days_in_periods:
                total_dates = rec.number_periods*rec.number_dates
                date_from = rec.date_start
                cont_date = 1
                for period in range(rec.number_periods):
                    date_to = date_from + datetime.timedelta(days=rec.days_in_periods)
                    for date in range(rec.number_dates):
                        Sale_Subscription_Dates = rec.env['sale.subscription.dates']
                        new_date = Sale_Subscription_Dates.create({
                            'subscription_id': rec.id,
                            'name': str(cont_date) + ' / ' + str(total_dates),
                            'date_from': date_from,
                            'date_to': date_to
                        })
                        new_date.create_plannning()

                        cont_date += 1
                    date_from = date_from + datetime.timedelta(days=rec.days_in_periods+1)


class SaleSubscriptionDates(models.Model):
    _name = "sale.subscription.dates"

    subscription_id = fields.Many2one('sale.subscription', String='template')
    name = fields.Char('Nombre')
    date_from = fields.Date('Fecha Inicial del Periodo')
    date_to = fields.Date('Fecha Final del Periodo')
    date = fields.Datetime('Fecha de la cita')
    planning_id = fields.Many2one('sale.subscription.dates.planning', string="Planificacion", readonly=True)
    vencidas = fields.Boolean(related="planning_id.vencidas")
    pendientes = fields.Boolean(related="planning_id.pendientes")

    @api.onchange('date')
    def _validation_date(self):
        for rec in self:
            if rec.date:
                if rec.date.date() < rec.date_from or rec.date.date() > rec.date_to:
                    raise UserError(_(
                        'La fecha de la cita ' + rec.name + ' no esta dentro del intervalo de su periodo'))

    def create_plannning(self):
        for data in self:
            planning = data.env['sale.subscription.dates.planning'].create({
            })
            data.planning_id = planning.id


SaleSubscriptionDates()
