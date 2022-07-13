# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductBrand(models.Model):
    _name = 'product.brand'
    _inherit = ['website.multi.mixin']
    _description = 'Product Brands'

    name = fields.Char(string='Brand Name', required=True, translate=True)
    logo = fields.Binary(string='Logo')
    visible_slider = fields.Boolean(string='Visible in Website',default=True)
    active = fields.Boolean(string='Active',default=True)
    product_ids = fields.One2many(
        'product.template',
        'product_brand_id',
        string='Brand Products',
    )
    products_count = fields.Integer(
        string='Number of products',
        compute='_get_products_count',
    )

    @api.depends('product_ids')
    def _get_products_count(self):
        self.products_count = len(self.product_ids)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_brand_id = fields.Many2one(
        'product.brand',
        string='Brand',
        help='Select a brand for this product'
    )
