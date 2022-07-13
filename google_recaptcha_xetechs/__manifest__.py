# Copyright 2018-2019 Alpesh Valaki.
# License OPL-1.

{
    "name": "Google reCAPTCHA",
    "summary": "State of the art spam & abuse protection for your website. in Login and Contact Us form",
    "version": "11.0.1.0.2",
    "category": "web",
    "website": "https://xetechs.odoo.com",
    "author": "Luis Aquino --> laquino@xetechs.com",
    "license": "OPL-1",
    "application": True,
    'installable': True,
    "depends": [
        'web','base_setup', 'website', 'website_crm'
    ], # if "two_factor_authentication" is installed then add "two_factor_authentication" as dependency. 
    "data": [
        'data/google_recaptcha_data.xml',
        'views/google_recaptcha_config_view.xml',
        'views/login_form_inherit.xml',
        'views/website_crm_contactus_form_inherit.xml',
        'security/ir.model.access.csv'
    ],
}
