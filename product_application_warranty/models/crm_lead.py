from odoo import api, fields, models, _

import datetime
days = ['Monday', 'Tuesday', 'Wednesday','Thursday','Friday', 'Saturday', 'Sunday']
months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

days_dict = {
    'Monday': 'Lunes',
    'Tuesday': 'Martes',
    'Wednesday': 'Miercoles',
    'Thursday': 'Jueves',
    'Friday': 'Viernes',
    'Saturday': 'Sabado',
    'Sunday': 'Domingo',
}

months_dict = {
    'January'  : 'Enero',
    'February' : 'Febrero',
    'March'    : 'Marzo',
    'April'    : 'Abril',
    'May'      : 'Mayo',
    'June'     : 'Junio',
    'July'     : 'Julio',
    'August'   : 'Agosto',
    'September': 'Septiembre',
    'October'  : 'Octubre',
    'November' : 'Noviembre',
    'December' : 'Diciembre'
}

class GarantiaProducto(models.Model):
    _name = 'garantia.producto'
    _description = 'Garantia de aplicacion de producto'

    name = fields.Text('Nombre')
    descripcion = fields.Text('Descripcion')


class Lead(models.Model):
    _inherit = 'crm.lead'
    garantia_producto_id = fields.Many2one('garantia.producto', string='Descripcion de garantia')
    cobertura_inicio = fields.Date('Inicio de cobertura')
    cobertura_fin = fields.Date('Fin de cobertura')
    translate_date = fields.Text(compute="_translate_date")


    def _translate_date(self):
        for data in self:
            data.translate_date = _(datetime.datetime.now().strftime('%A, %d de %B del %Y'))
            data.check()

    def check(self):

        for day in days:
            if day in self.translate_date:
                self.translate_date = self.translate_date.replace(day, days_dict[day])

        for month in months:
            if month in self.translate_date:
                self.translate_date = self.translate_date.replace(month, months_dict[month])