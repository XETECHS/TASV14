# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'External service extends',
    'version': '14.0',
    'author': "Xetechs, S.A.",
    'website': 'https:/www.xetechs.com',
    'support': 'Justo Rivera --> justo.rivera@xetechs.com',
    'sequence': 1,
    'license':'OPL-1',
    'depends': [
        'industry_fsm',
        'task_resources',
        'hr_timesheet',
        'base',
        'mail', 
        'product',
        'sale',
        'sale_timesheet_enterprise'
    ],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'wizard/service_ticket_timer_views.xml',
        'wizard/wizard_approved_service.xml',
        'views/project_task_form.xml',
        'views/project_task_view_inherit.xml',
        'reports/reports.xml',
        'reports/report_service_ticket_tmpl.xml',
        'data/template_email.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
