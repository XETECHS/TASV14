# -*- coding: utf-8 -*-
{
    'name': "Atharva Theme General",
    'category': 'Website',
    'sequence': 5,
    'summary': """Atharva Theme General""",
    'version': '2.3',
    'author': 'Atharva System',
    'support': 'support@atharvasystem.com',
    'website' : 'http://www.atharvasystem.com',
    'license' : 'OPL-1',
    'description': """
        Base Module for all themes by Atharva System""",
    'depends': [
        'website_sale_wishlist', 
        'website_sale_stock',
        'website_sale_comparison',
        'website_mass_mailing',
        'website_blog'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/website_menu_views.xml',
        'views/res_config_settings_views.xml',
        'views/category_configure_views.xml',
        'views/category_views.xml',
        'views/multitab_configure_views.xml',
        'views/product_brand_views.xml',
        'views/product_tabs_views.xml',
        'views/product_tags_views.xml',
        'views/custom_shop_views.xml',
        'views/blog_configure_views.xml',
        'views/templates.xml',
        'views/megamenu_templates.xml', 
        'views/dynamic_snippets.xml',
        'views/breadcrumb_templates.xml',
        'views/custom_shop_templates.xml',
        'views/product_brand_page.xml',
        'views/header_footer_template.xml',
        'views/product_quick_view_template.xml'
    ],
    'demo': [
        'data/demo.xml',
    ],
    'price': 14.00,
    'currency': 'EUR',
    'images': ['static/description/atharva-theme-general-banner.png'],
    'installable': True,
    'application': True
}
