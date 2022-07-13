# -*- coding: utf-8 -*-
{
    'name': "Sale Subscription Dates",
    'description': """
        Modulo para la gestion de los periodos y el numero citas en cada periodo.
    """,
    'author': 'Josué --> Jcpoz777@gmail.com ',
    'maintainer': 'XETECHS, S.A.',
    'website': 'https://www.xetechs.com',
    'category': 'Sale',
    'version': '1.0.0',
    'depends': [
        "sale_subscription",
        "planning"
    ],
    'data': [
        "security/ir.model.access.csv",
        "views/sale_subscription_views_extends.xml",
        "views/sale_subscription_template_form.xml",
        "views/sale_subscription_dates_planning.xml",
        "views/sale_subscription_kanban.xml",
        "filters/sale_subscriptions.xml",

    ]
}