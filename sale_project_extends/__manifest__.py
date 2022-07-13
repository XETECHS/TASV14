# -*- coding: utf-8 -*-
{
    'name': "Sale Project Extends",
    'summary': """
        Custom options for sale project extends""",
    'description': """
        Custom options for sale project extends
    """,
    'author': 'Luis Aquino --> laquino@xetechs.com ',
    'maintainer': 'XETECHS, S.A.',
    'website': 'https://www.xetechs.com',
    'category': 'Sale',
    'version': '1.0.2',
    'depends': [
        'product',
        'sale_management',
        'project',
        'purchase',
        'requisitions',
        'hr_timesheet',
        'hr_payroll'
    ],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/product_views.xml',
        'views/sale_views.xml',
        'views/project_views.xml',
        'views/stock_view.xml',
        'views/requisition_views.xml',
        'wizard/wizard_requisition_view.xml',
        'reports/report_quotation.xml'
    ]
}