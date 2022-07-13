# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sale subscription extends',
    'version': '14.0',
    'category': 'Sales',
    'author': "Xetechs, S.A.",
    'website': 'https:/www.xetechs.com',
    'sequence': 1,
    'license':'OPL-1',
    'depends': ['sale_subscription','project', 'external_service_extends'],
    'data': [
        'views/sale_subscription.xml',
        'reports/action.xml',
        'reports/subscription_report.xml',
        'security/groups.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
