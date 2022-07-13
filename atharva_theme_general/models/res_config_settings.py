# -*- coding: utf-8 -*-

from odoo import fields, models


class WebsiteConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    bread_cum_image = fields.Binary(
        related='website_id.bread_cum_image',
        string='Breadcrumb Image',readonly=False
    )
    is_breadcum = fields.Boolean(string="Do you want to disable Breadcrumb?", related='website_id.is_breadcum',readonly=False)
    breadcrumb_height = fields.Char('Padding',related='website_id.breadcrumb_height',help="For ex. 50px;",readonly=False)
    breadcum_background_image = fields.Boolean(string="Remove Breadcrumb background image?" ,related='website_id.breadcum_background_image',readonly=False)
    breadcrumb_color = fields.Char('Backgroud Color #', related='website_id.breadcrumb_color',readonly=False)
    breadcrumb_text_color = fields.Char('Text Color #', related='website_id.breadcrumb_text_color',readonly=False)
    shop_product_loader = fields.Selection(selection=[('infinite_loader','Infinite Loader'),('pagination','Pagination')], related='website_id.shop_product_loader', default='infinite_loader', translate=True,readonly=False)
