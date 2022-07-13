# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo import SUPERUSER_ID


class BIProductPack(models.Model):
    _name = 'bi.product.pack'

    product_id = fields.Many2one('product.product', string='Product', required=True)
    qty_uom = fields.Float(string='Quantity', required=True, defaults=1.0)
    bi_product_template = fields.Many2one('product.template', string='Product pack')
    bi_image = fields.Binary(related='product_id.image_1920', string='Image', store=True)
    price = fields.Float(related='product_id.lst_price', string='Product Price')
    uom_id = fields.Many2one(related='product_id.uom_id' , string="Unit of Measure")
    name = fields.Char(related='product_id.name', readonly="1")

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_pack = fields.Boolean(string='Is Product Pack')
    cal_pack_price = fields.Boolean(string='Calculate Pack Price')
    bi_pack_ids = fields.One2many('bi.product.pack','bi_product_template', string='Product pack')

    @api.model
    def create(self, vals):
        total = 0
        res = super(ProductTemplate, self).create(vals)
        if res.cal_pack_price:
            if 'pack_ids' in vals or 'cal_pack_price' in vals:
                for pack_product in res.pack_ids:
                    qty = pack_product.qty_uom
                    price = pack_product.product_id.list_price
                    total += qty * price
        if total > 0:
            res.list_price = total
        return res

    def write(self, vals):
        total = 0
        res = super(ProductTemplate, self).write(vals)
        for pk in self:
            if pk.cal_pack_price:
                if 'pack_ids' in vals or 'cal_pack_price' in vals:
                    for pack_product in pk.pack_ids:
                        qty = pack_product.qty_uom
                        price = pack_product.product_id.list_price
                        total += qty * price
        if total > 0:
            self.list_price = total
        return res
