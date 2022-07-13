# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Dynamic Product Bundle (choice on Sales Order) Odoo/OpenERP',
    'category': 'Sales',
    "version" : "14.0.0.0",
    'summary': 'Combine two or more product pack product kit product bundle product pack item on product combo product on sale bundle product delivery bundle product pack kit combine product combine product variant bundle item pack sales bundle Dynamic product bundle pack',
    'description': """
    BrowseInfo developed a new odoo/OpenERP module apps.

    odoo create Product Bundle Product Pack Bundle Pack of Product Combined Product pack odoo
    odoo Product Pack Custom Combo Product Bundle Product Customized product Group product odoo
    odoo Custom product bundle Custom Product Pack odoo combo product pack combo product combo bundle pack combo bundle product pack 
    odoo combo product pack multiple product pack group product pack choice odoo
    odoo product Pack Price Product Bundle pack price product Bundle Discount product Bundle Offer bundle price



    odoo create Product kit Product Pack kit Pack of Product Combined Product kit odoo
    odoo Product kit Custom Combo Product kit Product Customized product kit product odoo
    odoo Custom product kit Custom Product kit pack product bundle kit product kit bundle odoo 
    odoo combo product pack kit combo product combo kit bundle pack combo kit product pack kit 
    odoo combo product kit multiple product kit group product kit choice odoo
    odoo product kit Price Product kit pack price product kit Discount product kit Bundle Offer bundle price
    -Product Pack, Custom Combo Product, Bundle Product. Customized product, Group product.Custom product bundle. Custom Product Pack.
    -Pack Price, Bundle price, Bundle Discount, Bundle Offer. Customize product bundle, customize product pack, customize bundle pack.
""",
    'author': 'BrowseInfo',
    "price": 49.00,
    "currency": 'EUR',
    'website': 'https://www.browseinfo.in',
    'images': [],
    'depends': ['sale','product','stock','sale_stock','sale_management'],

    'data': [
        'wizard/product_bundle_wizard_view.xml',
        'views/product_bundle_view.xml',
        'security/ir.model.access.csv'
        
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    "live_test_url":'https://youtu.be/LcQQyQ-xm3A',
    "images":['static/description/banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
