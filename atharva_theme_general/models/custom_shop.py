# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools.translate import _


class ProductsPerPage(models.Model):
    _name = 'product.qty_per_page'
    _description = 'Quantity per page'

    name = fields.Integer(string='Quantity', required=True, default=10)
    sequence = fields.Integer(string='Sequence', default=10)

    _sql_constraints = [
        ('const_unique_name','unique(name)', 'The duplicates of Quantity values are not allowed!'),
        ('check_name', 'CHECK(name > 0)', 'The Quantity should be greater than 0.'),
    ]
