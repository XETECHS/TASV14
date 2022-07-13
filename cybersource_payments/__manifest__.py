{
    'name': 'Odoo CyberSource Payment Gateway',
    'summary': 'Cybersource Payment Gateway',
    'version': '1.0',
    'description': """Cybersource Payment Gateway""",
    'author': 'XETECHS',
    'category': 'Website',
    'website': "xetechs.com",
    'depends': ['base','website_sale', 'payment', 'sale', 'account','website', 'google_recaptcha'],
    'data': [
        'views/company.xml',
        'views/payment_view.xml',
        'views/payment_cybersource_template.xml',
        'data/payment_acquirer_data.xml',
    ],
    'images': ['static/description/cyber_source_logo.jpg'],
    'installable': True,
    'auto_install': False,
}
