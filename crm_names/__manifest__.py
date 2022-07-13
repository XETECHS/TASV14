# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'CRM Lead Names',
    'version': '12.0.0.2',
    'category': 'Sales',
    'author': "Xetechs, S.A.",
    'website': 'https:/www.xetechs.com',
    'support': 'Luis Aquino --> laquino@xetechs.com',
    'sequence': 1,
    'summary': 'Create a maintenance for save names in CRM Leads',
    'description': "Create a maintenance for save names in CRM Leads",
    'license':'OPL-1',
    'depends': ['crm','sale','sale_management'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/crm_names_view.xml',
        'views/crm_lead_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
