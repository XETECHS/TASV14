from odoo import api, fields, models
from datetime import date, datetime

class SaleSubscriptionDatesPlanning(models.Model):
    _name = "sale.subscription.dates.planning"

    name = fields.Char('Nombre', compute="set_name")
    planning_ids = fields.One2many('planning.slot', 'planning_id', string="Tareas planificadas")
    vencidas = fields.Boolean(compute="set_name")
    pendientes = fields.Boolean(compute="set_name")

    def set_name(self):
        for data in self:
            count = 0
            count_vencidas = 0
            for slot in data.planning_ids:
                if slot.start_datetime.date() == date.today():
                    count += 1
                if slot.start_datetime.date() < date.today() and state != 'terminado':
                    count_vencidas += 1
            data.pendientes = True if count else False
            data.vencidas = True if count_vencidas else False
            data.name = "Hoy: " + str(count) + "  vencidas: " + str(count_vencidas)
