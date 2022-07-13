# -*- coding: utf-8 -*-
{
    'name': "CRM Extend Task",

    'author': "Xetechs GT",
    'website': "http://www.xetechs.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list

    # any module necessary for this one to work correctly
    'depends': ['sale', 'crm'],

    # always loaded
    'data': [
        'security/security_views.xml',
        'security/ir.model.access.csv',
        'views/partner_views.xml',
        'views/crm_views.xml',
        'views/sale_views.xml'
    ],
}
