from odoo import _, api, fields, models

class SaleOrderTasData(models.Model):
    _name = 'sale.order.tas.data'
    _description = 'Sale Order TAS Data'

    name = fields.Char(string='Nombre') 
    description = fields.Html(string='Descripción', copy=False) 
    # order_id = fields.Many2one('sale.order', string='Order id')

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'Sale Order'

    title = fields.Char(string="Titulo", required=True)

    sale_order_tas_data = fields.Many2many('sale.order.tas.data', string='Datos TAS')
    
    tipo_nota = fields.Many2one('sale.note.type', string='')
    notas = fields.Html(string='NOTAS', copy=False, related="tipo_nota.text")


class SaleNoteType(models.Model):
    _name = 'sale.note.type'
    _description = 'Sale Note Type'
    
    name = fields.Char(string='Name', required=True)
    text = fields.Html(string='Text', required=True)