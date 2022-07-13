# -*- encoding: utf-8 -*-

from odoo import fields, models

class ProductPublicCategory(models.Model):
	_name = 'category.lines'
	_order = 'sequence'

	sequence = fields.Integer(string='Sequence')
	image = fields.Binary(string='Image', attachment=True)
	category_id = fields.Many2one('product.public.category', string="category", ondelete='restrict')


class CategoryCollection(models.Model):
	_name="category.collection"
	_description="Category Collection Configuration"

	name = fields.Char("Collection Name",required=True, translate=True)
	active = fields.Boolean("Active", translate=True, default=True)
	categ_ids = fields.Many2many('category.lines', string="Categories")
	item_count = fields.Selection([('1', '1'),('2', '2'),('3', '3'),('4', '4'),('5', '5')],string="Total count", default="4", translate=True)
	label_active = fields.Boolean("Show Label", default=True)
	category_name_active = fields.Boolean("Show Category Name", default=True)
	category_link_active = fields.Boolean("Show Category Link", default=True)