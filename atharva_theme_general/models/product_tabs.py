# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductTabHeads(models.Model):
    _name = 'product.tab_heads'
    _description = 'Product Tab Heading'

    name = fields.Char(string='Tab Name', translate=True)
    active = fields.Boolean(string='Active', default=True)


class ProductTabs(models.Model):
    _name = 'product.tabs'
    _order = 'tab_order, name'
    _description = 'Product Tab Collection'

    name = fields.Many2one('product.tab_heads', string='Tab Name')
    active = fields.Boolean(string='Active', default=True)
    tab_content = fields.Html(string='Tab Content', sanitize=True, translate=True)
    tab_order = fields.Integer(string='Tab Order')
    product_tmpl_id = fields.Many2one('product.template', string='Product')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    tab_ids = fields.One2many('product.tabs', 'product_tmpl_id', string='Product Tabs')
