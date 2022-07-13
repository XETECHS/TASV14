# -*- coding: utf-8 -*-
from email.policy import default
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo import api, fields, models, _, SUPERUSER_ID
from datetime import datetime
import logging

import base64
import time
_logger = logging.getLogger(__name__)



class ProjectTask(models.Model):
    _inherit = 'project.task'
    _rec_name = 'number'

    tipo_visita = fields.Selection([('a_facturar', 'A Facturar'), ('gratuita', 'Gratuita')], "Tipo de visita", default='a_facturar')
    service_ticket_ids = fields.One2many('project.tasks.service.ticket', 'task_id', string='Service Ticket')
    service_ticket_count = fields.Integer("Service Ticket count", compute='_compute_service_ticket_count')
    partner_id_vat = fields.Char(string='vat', related="partner_id.vat")
    number = fields.Char(string='Number', copy=False, readonly=True, index=True, default=lambda self: _('New'))
    assign_to = fields.Many2many("res.users", 'assign_user_rel', string="Técnico")
    stage_id_name = fields.Char(related="stage_id.name", string='nombre de la etapa')
    resources_list_ids = fields.Many2many('product.product', string='List of Resources', compute="_get_resources_list_ids")
    partner_child = fields.Many2one('res.partner', store=True, string="Persona de Contacto",readonly=False)
    partner_child_email = fields.Char('Correo', related="partner_child.email", readonly=False)
    partner_child_mobile = fields.Char('Teléfono', related="partner_child.mobile", readonly=False)

    # stage_id = fields.Many2one('project.task.type', string='Stage', compute='_compute_stage_id',
    #     store=True, readonly=False, ondelete='restrict', tracking=True, index=True,
    #     default= lambda self: self.env.ref('project.task_type_def1').id, group_expand='_read_group_stage_ids',
    #     domain="[('project_ids', '=', project_id)]", copy=False, task_dependency_tracking=True)

    #New fields
    analytic_group_id = fields.Many2one('account.analytic.group', 'Linea de Negocio', required=False, copy=False, tracking=True)
    analytic_subgroup_id = fields.Many2one('account.analytic.account', 'Sublinea de Negocio', required=False, copy=False, tracking=True)
    service_type_id = fields.Many2one('project.task.service.type', string='Tipo de servicio')
       
    @api.onchange('partner_id','partner_child','partner_child_email','partner_child_mobile')
    def _parent_contact(self):
        for data in self:
            if data.partner_id and data.partner_child:
                if not data.partner_child.parent_id:
                    data.partner_child.parent_id = data.partner_id.id
                if not data.partner_child.email:
                    data.partner_child.email = data.partner_child_email
                if not data.partner_child.mobile:
                    data.partner_child.mobile = data.partner_child_mobile

    @api.depends('resources_ids')
    def _get_resources_list_ids(self):
        for order in self:
            dic = []
            for line in order.resources_ids:
                dic.append(line.product_id.id) 
            order.resources_list_ids = dic

    def action_service_ticket(self):
        action = self.env["ir.actions.actions"]._for_xml_id("external_service_extends.project_tasks_service_ticket_action")

        # display all subtasks of current task
        action['domain'] = [('id', 'in', self.service_ticket_ids.ids)]
        action['context'] = {
            'default_user_id': self.env.context.get('user_id', self.user_id.id),
            'default_date_assign': self.date_assign,
            'default_partner_id': self.env.context.get('partner_id', self.partner_id.id),
            'default_stage_id': self.env.context.get('stage_id', self.stage_id.id),
            'default_tipo_visita': self.env.context.get('tipo_visita', self.tipo_visita),
            'default_task_id': self.id, 
            'default_company_id': self.env.company.id,
            'default_client_note': 'ESTIMADO CLIENTE: Le agradecemos verificar los datos aquí descritos, así como las fechas y horas de salida y llegada antes de firmar esta boleta. Su colaboración permitirá atenderle de una manera mas eficiente'
        }

        return action

    @api.depends('service_ticket_ids')
    def _compute_service_ticket_count(self):
        for task in self:
            task.service_ticket_count = len(task.service_ticket_ids)

    
    @api.model
    def create(self, vals):
        # print("vals",self.env.ref('project.task_type_def1').id,self.env.ref('project.task_type_def1').name)
        if vals.get('number', _('New')) == _('New'):
            vals['number'] = self.env['ir.sequence'].next_by_code('project.tasks.tas') or _('New')
        # self.stage_id=self.env.ref('project.task_type_def1').id
        
        result = super(ProjectTask, self).create(vals)
        return result


class ProjectTasksServiceTicket(models.Model):
    _name = 'project.tasks.service.ticket'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    #_inherit = 'timer.mixin'
    _description = 'Project Tasks Service Ticket'
    
    name = fields.Char(string='No. Boleta', required=True, 
        copy=False, readonly=True, index=True, 
        default=lambda s: s.env['ir.sequence'].next_by_code('project.tasks.service.ticket') )
    text = fields.Html(string='Text')

    hours_planned_in = fields.Datetime(string='Hora de Inicio')
    hours_planned_out = fields.Datetime(string='Hora Salida')
    status_timer = fields.Selection([
        ('draft', 'Draft'),
        ('started', 'Started'),
        ('finished', 'Finished')
    ], string='Status Timer', default="draft")
    timer_finished = fields.Char('Horas Totales')

    date_assign = fields.Datetime(string='Fecha', index=True, copy=False, default=datetime.now())
    task_id = fields.Many2one('project.task', string='No. de OT', index=True, required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    company_logo = fields.Binary(related="company_id.logo")
    tipo_visita = fields.Selection([('a_facturar', 'A Facturar'), ('gratuita', 'Gratuita')], default=('a_facturar'), string="A Cobrar")
    service_type_id = fields.Many2one('project.task.service.type', string='Tipo de servicio')
    stage_id = fields.Many2one('project.task.type', string='Etapa')
    # default=lambda self:self.env.ref('cambio_presentacion.stock_warehouse_desglose').id
    stage_id_name = fields.Char(related="stage_id.name", string='nombre de la etapa')

    user_id = fields.Many2one('res.users', string='Colaborador', index=True, tracking=True, readonly=True, default=lambda self: self.env.user.id)
    resources_ids = fields.One2many('project.task.resource', 'task_ticket_id', 'Recursos')
    work_done_xt = fields.Html(string='Trabajo Realizado', copy=False)

    partner_id = fields.Many2one(related="task_id.partner_id", string='Cliente', store=True, readonly=True)
    partner_id_phone = fields.Char(string='Phone', related="partner_id.phone")
    partner_id_vat = fields.Char(string='vat', related="partner_id.vat")
    partner_id_street = fields.Char(string='street', related="partner_id.street")
    partner_id_city = fields.Char(string='city', related="partner_id.city")
    partner_id_state_id = fields.Char(string='state_id', related="partner_id.state_id.name")
    partner_id_zip = fields.Char(string='zip', related="partner_id.zip")
    partner_id_country_id = fields.Char(string='country_id', related="partner_id.country_id.name")
    
    client_note = fields.Text(string='Nota de Cliente')
    partner_sign = fields.Binary(string='Firma del Cliente')
    technical_sign = fields.Binary(string='Firma del Técnico')
    active_sign = fields.Boolean(string='Active', default=False, compute="_get_active_sign")

    order_ids = fields.One2many('sale.order', 'service_task_id', string='Sale Order')
    timesheet_ids = fields.One2many('account.analytic.line', 'timesheet_invoice_ticket_id', string='Timesheets', readonly=True, copy=False)
    state = fields.Selection([('new', 'Nuevo'),('process','En Proceso'),('closed','Concluido'),('to approved','Para aprobar'),('approved','Aprobado'),('finished','Cerrado')],default='new', string='Estado',tracking=True)
    variable = fields.Float('Variable',tracking=True)
    user_admin = fields.Integer('Es Super administrador', compute="_is_user_admin")
    # resources_list_ids = fields.Many2many(related="parent_id.resources_list_ids", string='List of Resources')

    @api.onchange('task_id')
    def onchange_task(self):
        if self.task_id:
            if self.task_id.service_type_id:
                self.service_type_id = self.task_id.service_type_id
            if self.task_id.stage_id:
                self.stage_id = self.task_id.stage_id


    def to_approved(self):
        # Function for Change the state when the user clicked the button "para aprobar" and the mount variable is max a zero.
        for data in self:
            data.state = 'to approved'
            data.action_send_email_state()
            data.send_email_state()
            

    def approved(self):
        # Function for change the state "approved"
        for data in self:
            if data.state != 'approved' and data.state == 'to approved':
                data.state = 'approved'
            else:
                raise UserError(_("Esta Boleta aun no esta para aprobar."))

    @api.onchange('partner_sign', 'technical_sign')
    def _onchange_sign_xt(self):
        for order in self:
            if order.partner_sign and order.technical_sign:
                task = self.env['project.task.type'].search([('name', '=', 'Hecho')])
                if task:
                    order.stage_id = task

    @api.depends('work_done_xt', 'hours_planned_out')
    def _get_active_sign(self):
        for order in self:
            _logger.info(order.work_done_xt)
            if order.work_done_xt == '<p>&nbsp;</p>' or order.work_done_xt == '<p><br></p>' or order.work_done_xt == '<p class="oe-hint oe-command-temporary-hint"><br></p>' or order.work_done_xt == '<p class="oe-hint oe-command-temporary-hint" placeholder="Type &quot;/&quot; for commands"><br></p>':
                order.active_sign = False
            else:
                if order.hours_planned_out != 0.0:
                    order.active_sign = True
                else:
                    order.active_sign = False

    @api.onchange('user_id')
    def _onchange_user_id(self):
        if self.user_id:
            try:
                PREFIX = "".join(
                    [name[0].upper() for name in self.user_id.name.split(" ")]
                )
                self.name = PREFIX + self.name[2:]
            except:
                pass

    @api.depends('state')
    def _is_user_admin(self):
        for data in self:
            if data.state == 'closed':
                user = self.env['res.users'].browse(self._uid)
                is_admin = user.has_group('__export__.res_groups_184_5bfdf510')
                if is_admin:
                    data.user_admin =  1
                else:
                    data.user_admin = 0
            else:
                data.user_admin = 0

    def action_compute_timer(self):
        for record in self:
            hours = record.hours_planned_out - record.hours_planned_in
            if '.' in str(hours):
                hours = str(hours).split('.')
                record.write({
                    "timer_finished": hours[0]
                })
            else:
                record.write({
                    "timer_finished": str(hours)
                })


    def action_fsm_create_quotation(self):
        view_form_id = self.env.ref('sale.view_order_form').id
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations")
        action.update({
            'views': [(view_form_id, 'form')],
            'view_mode': 'form',
            'name': self.name,
            'context': {
                'fsm_mode': True,
                'form_view_initial_mode': 'edit',
                'default_partner_id': self.partner_id.id,
                'default_task_id': self.id,
                'default_company_id': self.company_id.id,
            },
        })
        return action
        
    def action_send_email_state(self):
        self = self.with_user(SUPERUSER_ID)
        template_id = self.env['ir.model.data'].xmlid_to_res_id('external_service_extends.external_service_email_template', raise_if_not_found=False)
        if template_id:
            for order in self:
                order.with_context(force_send=True).message_post_with_template(template_id, composition_mode='comment', email_layout_xmlid="mail.mail_notification_light")


    def send_email_state(self):
        for record in self:
            template_id = self.env['ir.model.data'].get_object_reference('external_service_extends', 'external_service_email_template_external')[1]
            email_template_obj = self.env['mail.template'].browse(template_id)
            if template_id:
                report_template_id = self.env.ref('external_service_extends.action_service_ticket_report').with_context(landscape=True)._render_qweb_pdf(record.id, data=None)
                data_record = base64.b64encode(report_template_id[0])
                ir_values = {
                    'name': "Reporte de Servicios",
                    'type': 'binary',
                    'datas': data_record,
                    'store_fname': data_record,
                    'mimetype': 'application/x-pdf',
                }
                
                values = email_template_obj.generate_email(record.id, ['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'email_cc', 'reply_to', 'scheduled_date'])
                values['email_from'] = record.company_id.email
                values['email_to'] = record.task_id.partner_child_email
                #values['email_cc'] = record.user_cc_id.partner_id.email or ''
                data_id = self.env['ir.attachment'].create(ir_values)
                values['attachment_ids'] = [(6, 0, [data_id.id])]
                mail_mail_obj = self.env['mail.mail']
                msg_id = mail_mail_obj.sudo().create(values)
                if msg_id:
                    msg_id.sudo().send()
        return True


class ProjectTaskResource(models.Model):
    _inherit = 'project.task.resource'
    _rec_name = 'product_id'

    task_ticket_id = fields.Many2one('project.tasks.service.ticket', 'Task Ticket', ondelete='restrict', readonly=True,)
    resources_list_ids = fields.Many2many(related="task_ticket_id.task_id.resources_list_ids", string='List of Resources')

class ProjectTaskServiceTask(models.Model):
    _name = 'project.task.service.type'
    _description = 'Tipo de servicio'

    name = fields.Char(string='Nombre')
