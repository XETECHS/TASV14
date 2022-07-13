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

class CrmLeadNames(models.Model):
    _name = "crm.lead.names"
    _description = "CRM Lead Names"
    _rec_name = 'name'

    name = fields.Char('Descripcion Oportunidad', required=True, translate=True)
    active = fields.Boolean('Activo', default=True)
    notes = fields.Text('Notas', required=False)

CrmLeadNames()
