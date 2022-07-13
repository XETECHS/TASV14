# -*- coding: utf-8 -*-
{
    'name': "Helpdesk Customization",

    'summary': """
        This module is developed to handle the customized requirements of
        adding new features on the helpdesk module.""",

    'description': """
        This module is developed to handle the customized requirements of
        adding new features on the helpdesk module.
    """,

    'author': "Fazal Ur Rahman",
    'category': 'Extra Tools',
    'version': '14.0.0.1',

    'depends': ['base', 'helpdesk', 'sale_subscription', 'sale_subscription_extends'],

    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
