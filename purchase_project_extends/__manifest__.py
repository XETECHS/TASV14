# -*- coding: utf-8 -*-
{
    'name': "Purchase Project Extends",
    'summary': """
        Custom options for purchase project extends""",
    'description': """
        Custom options for purchase project extends
    """,
    'author': 'Xetechs, S.A.',
    'support': 'Luis Aquino --> laquino@xetechs.com',
	'maintainer': 'XETECHS, S.A.',
	'website': 'https://www.xetechs.com',
    'category': 'Sale',
    'version': '1.0',
    'depends': ['base', 'purchase', 'requisitions', 'project'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/purchase_view.xml',
        'views/requisition_view.xml',
        'views/account_move_views.xml'
        #'reports/report_quotation.xml'
    ]
}