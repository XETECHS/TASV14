# -*- coding: utf-8 -*-
{
    'name': 'Stock Move Analytic',
    'author': 'ERP Ukraine',
    'website': 'https://erp.co.ua',
    'support': 'support@erp.co.ua',
    'category': 'Inventory Management',
    'depends': ['stock', 'account', 'stock_account'],
    'version': '4.0',
    'license': 'OPL-1',
    'price': 30.00,
    'currency': 'EUR',
    'description': """
Include analytic account in stock accounting entries
======================================================
This module adds analytic account field for scrap and
production virtual stock locations.

Also it is possible to enter analytic account on Stock Picking form or Stock Picking Type.
""",
    'auto_install': False,
    'demo': [],
    'data': ['views/analytic_stock_view.xml'],
    'installable': True,
    'application': True,
}
