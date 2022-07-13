# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from itertools import groupby
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang
from odoo.tools import html2plaintext
import odoo.addons.decimal_precision as dp

class CrmLead(models.Model):
    _inherit = "crm.lead"

    name_id = fields.Many2one('crm.lead.names', 'Oportunidad', required=True)
    edit_customer_qualification = fields.Boolean('Editar', compute="_get_edit")
    customer_qualification = fields.Selection([('1', '1'),('2', '2'),('3', '3'),('4', '4'),('5', '5'),('6', '6'),('7', '7'),('8', '8'),('9', '9'),('10', '10')], "Calificacion", default='1', required=True)
    partner_shipping_id = fields.Many2one('res.partner', string='Direccion de Entrega', readonly=False, required=False)

    @api.onchange('partner_id')
    def onchange_partner_shipping(self):
        addr = self.partner_id.address_get(['delivery', 'invoice'])
        self.update({
            'partner_shipping_id': addr['delivery'],
        })

    @api.depends('user_id')
    def _get_edit(self):
        user_id = self.env.user
        is_manager = user_id.has_group('crm_names.group_edit_customer_qualification')
        if is_manager:
            self.edit_customer_qualification = True
        else:
            self.edit_customer_qualification = False

    @api.onchange('name_id')
    def onchange_name(self):
        for rec in self:
            if rec.name_id:
                rec.name = rec.name_id.name
CrmLead()
