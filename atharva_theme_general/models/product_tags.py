# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTags(models.Model):
    _description = 'Product Tags'
    _name = 'product.tag'
    _order = 'sequence'

    name = fields.Char(string='Name', required=True, translate=True)
    sequence = fields.Integer(help="Gives the sequence order when displaying a list of rules.")
    active = fields.Boolean(default=True, help="The active field allows you to hide the tag without removing it.")
    product_ids = fields.Many2many('product.template', string='Product')

    _sql_constraints = [('name_uniqe', 'unique (name)',
                         "Tag name already exists.!")]




class ProductTemplate(models.Model):
    _inherit = "product.template"

    tag_ids = fields.Many2many('product.tag', string='Product Tags')
