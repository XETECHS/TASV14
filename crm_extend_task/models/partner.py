# -*- coding: utf-8 -*-
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger( __name__ )

class ResPartner(models.Model):
    _inherit = 'res.partner'
    _description = 'Res Partner'

    reference = fields.Many2one('res.partner.reference', string = 'Referencia')
    '''
    @api.constrains('vat')
    def _check_unique_vat(self):
        for record in self:
            if self.search_count([('vat', '=', record.vat), ('parent_id', '=', False)]) > 1:
                raise ValidationError("Error. There is already a partner with that vat.")
    '''

class ResPartnerReference(models.Model):
    _name = 'res.partner.reference'
    _description = 'Res Partner Reference'

    name = fields.Char(string='Nombre', required=True)


