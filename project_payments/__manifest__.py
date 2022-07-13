# -*- coding: utf-8 -*-
{
    'name': "Project Payments",

    'summary': """
        This module is developed to add the functionality of payments
        on the project and project on the payments.""",

    'description': """
        This module is developed to add the functionality of payments
        on the project and project on the payments.
    """,

    'author': "Fazal Ur Rahman",
    'category': 'Extra Tools',
    'version': '13.0.0.1',

    'depends': [
                'base', 
                'account',
                'purchase_project_extends'
            ],

    'data': [
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
