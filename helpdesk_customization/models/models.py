# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartnerInherited(models.Model):
    _inherit = 'res.partner'


class HelpdeskTicketInherited(models.Model):
    _inherit = 'helpdesk.ticket'

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        for rec in self:
            rec.street = rec.partner_id.street
            rec.street2 = rec.partner_id.street2
            rec.zip = rec.partner_id.zip
            rec.city = rec.partner_id.city
            rec.state_id = rec.partner_id.state_id
            rec.country_id = rec.partner_id.country_id
            rec.vat = rec.partner_id.vat
            rec.phone = rec.partner_id.phone
            rec.mobile = rec.partner_id.mobile

            stage_id = self.env['sale.subscription.stage'].search(['|', ('name', '=', 'En progreso'), ('name', '=', 'In Progress')])
            rec.subscriptions = self.env['sale.subscription'].search([('partner_id', '=', rec.partner_id.id), ('stage_id', '=', stage_id.id)])

            project_ids = []
            for subscription in rec.subscriptions:
                project_ids.append(subscription.project_id.id)

            rec.tasks = self.env['project.task'].search([('project_id', 'in', project_ids)])

    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')

    vat = fields.Char(string='VAT')
    phone = fields.Char(string='Phone')
    mobile = fields.Char(string='Mobile')

    subscriptions = fields.Many2many('sale.subscription', string='Subscriptions')
    tasks = fields.Many2many('project.task', string='Tasks')
