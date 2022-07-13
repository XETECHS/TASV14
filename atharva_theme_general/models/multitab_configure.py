# -*- coding: utf-8 -*-

from odoo import fields, models


class MultitabConfigure(models.Model):
    _name = 'multitab.configure'
    _description = 'Multitab configuration for product snippets'
    
    name = fields.Char('Group Name', translate=True, required=True)
    product_ids = fields.One2many('multitab.products','tab_id',string='Products')
    active = fields.Boolean(string='Active', default=True)
    image = fields.Binary(string='Image', store=True)
    image_filename = fields.Char(string='Image Filename')


class MultitabProducts(models.Model):
    _name = 'multitab.products'
    _order = 'sequence,id'
    _description = 'Products Collection for Multitabs'
    
    product_id = fields.Many2one('product.template',string='Products',
                                 domain=[('website_published','=',True)])
    sequence = fields.Integer(string='Sequence')
    tab_id = fields.Many2one('multitab.configure',string ='Multi Tab')


class CollectionConfigure(models.Model):
    _name = 'collection.configure'
    _description = 'Multitab Collections'
    
    name = fields.Char(string='Title', required=True, translate=True)
    tab_collection_ids = fields.Many2many('multitab.configure',string='Select Collection')
    active = fields.Boolean(string='Active', default=True)


class Multitab_configure_brand(models.Model):
    _name = 'multitab.configure.brand'
    _description = 'Tab configuration for brand snippets'

    name = fields.Char("Group Name", translate=True, required=True)
    brand_ids = fields.One2many(
        "tab.brands", "tab_id", string="Brands", translate=True)
    active = fields.Boolean("Active", translate=True)
    label_active = fields.Boolean("Show Label", translate=True)
    brand_name_active = fields.Boolean("Show Brand Name", translate=True)
    brand_link_active = fields.Boolean("Set Brand link", translate=True)
    item_count = fields.Integer("Total count", default=4, translate=True)
    auto_slider = fields.Boolean("Auto Slider", translate=True)
    slider_time = fields.Integer("Slider Time (Seconds)", default=5, translate=True)

class Tab_collection_brand(models.Model):
    _name = "tab.brands"
    _order = "sequence,id"
    _description = 'Brand collection'

    brand_id = fields.Many2one("product.brand", string="Brands",
                               domain=[('visible_slider', '=', True)])
    sequence = fields.Integer(string="Sequence")
    tab_id = fields.Many2one("multitab.configure.brand", string="Tab Id")
