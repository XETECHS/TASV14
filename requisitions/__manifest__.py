{
    'name': 'Requisition',
    'summary': """PO Requisition""",
    'description': """
        Here user can place a requisition for purchase. Modified by Xetechs S.A.
    """,
    'author': "Xetechs, S.A. and Shahjalal Hossain",
    'website': "https://github.com/shahjalalh",
    'category': 'Purchase',
    'version': '1.0',
    'depends': ['base', 'account', 'purchase', 'stock', 'project'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data_view.xml',
        'views/requisition_view.xml',
        'report/requisition_report_templates.xml',
        'report/requisition_reports.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
