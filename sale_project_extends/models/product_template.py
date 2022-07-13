# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sellers = fields.Char('Suppliers')
    is_kit = fields.Boolean('Is Kit', help="Mark as kit type product")
    is_task = fields.Boolean('Is Task', help="Mark this product as task")
    product_item_ids = fields.One2many('product.item', 'product_tmpl_id', string='Items')
    
    #@api.depends('seller_ids')
    #def _get_sellers(self):
    #    for rec in self:
    #        if rec.seller_ids:
    #            providers = rec.seller_ids.mapped(lambda x: x.name.name)
    #            rec.sellers = ' | '.join(providers)


class ProductItems(models.Model):
    _name = "product.item"
    _description = "Product Item kit"

    name = fields.Text('Descripcion', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_tmpl_id = fields.Many2one('product.template', string='Template')
    quantity = fields.Float('Cantidad', required=True, default=1.00)
    is_task = fields.Boolean('is Task', help="Is a task?")

    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            self.name = self.product_id.name

