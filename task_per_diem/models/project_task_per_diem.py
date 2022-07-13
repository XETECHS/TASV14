from odoo import api, fields, models


class ProjectTaskPerDiem(models.Model):
    _name = 'project.task.per.diem'

    def _subtotal(self):
        for data in self:
            data.subtotal = data.cantidad * data.cost

    product_id = fields.Many2one('product.product', 'Producto', domain=[('type', 'in', ['consu', 'product'])])
    uom = fields.Many2one('uom.uom', related="product_id.uom_id", string="Unidad de medida")
    cost = fields.Float(string='Costo', related="product_id.standard_price")
    subtotal = fields.Float('Subtotal', compute="_subtotal")
    referencia = fields.Char(related="product_id.default_code", string='Referencia interna')
    cantidad = fields.Float('Cantidad', default=0)
    task_id = fields.Many2one('project.task', string='Tarea')
