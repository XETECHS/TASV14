import hmac
import time
import hashlib
import base64
import uuid
import json
import logging, base64, requests, json

from werkzeug import urls
from datetime import datetime
from suds.sudsobject import asdict
from odoo import api, fields, models, _
from odoo.http import request
from odoo.tools.float_utils import float_compare

_logger = logging.getLogger(__name__)


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('cybersource', 'CyberSouce')], ondelete = {'cybersource': 'set default',})
    cybersource_merchant_id = fields.Char(required_if_provider='cybersource', string="Merchant id")
    cybersource_key = fields.Char(required_if_provider='cybersource', string="Key")
    
    def _get_feature_support(self):
        res = super(PaymentAcquirer, self)._get_feature_support()
        res['tokenize'].append('cybersource')
        return res
    
    cybersouce_values = {}

    def cybersource_form_generate_values(self, values):
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        cybersouce_values = dict(values)
        cybersouce_values.update({
            'c_login': self.cybersource_merchant_id,
            'c_trans_key': self.cybersource_key,
            'c_amount': str(values['amount']),
            'c_show_form': 'PAYMENT_FORM',
            'c_type': 'AUTH_CAPTURE' if not self.capture_manually else 'AUTH_ONLY',
            'c_method': 'CC',
            'c_fp_sequence': '%s%s' % (self.id, int(time.time())),
            'c_version': '3.1',
            'c_relay_response': 'TRUE',
            'c_fp_timestamp': str(int(time.time())),
            'c_relay_url': 'shop/confirmation',
            'c_currency_code': values['currency'] and values['currency'].name or '',
            'address': values.get('partner_address'),
            'city': values.get('partner_city'),
            'country': values.get('partner_country') and values.get('partner_country').name or '',
            'email': values.get('partner_email'),
            'zip_code': values.get('partner_zip'),
            'first_name': values.get('partner_first_name'),
            'last_name': values.get('partner_last_name'),
            'phone': values.get('partner_phone'),
            'state': values.get('partner_state') and values['partner_state'].code or '',
            'billing_address': values.get('billing_partner_address'),
            'billing_city': values.get('billing_partner_city'),
            'billing_country': values.get('billing_partner_country') and values.get('billing_partner_country').name or '',
            'billing_email': values.get('billing_partner_email'),
            'billing_zip_code': values.get('billing_partner_zip'),
            'billing_first_name': values.get('billing_partner_first_name'),
            'billing_last_name': values.get('billing_partner_last_name'),
            'billing_phone': values.get('billing_partner_phone'),
            'billing_state': values.get('billing_partner_state') and values['billing_partner_state'].code or '',
        })
        return cybersouce_values
    
class TxCybersource(models.Model):
    _inherit = 'payment.transaction'
    


    @api.model
    def _cybersource_form_get_tx_from_data(self, data):
        reference = data.get('id')
        transaction = self.search([('reference', '=', reference)])
        if not transaction:
            _logger.warning(_('Cybersource: received data for reference %s; no order found') % (reference))
        elif len(transaction) > 1:
            _logger.warning(_('Cybersource: received data for reference %s; multiple orders found') % (reference))
        return transaction
    
    def s2s_do_transaction(self, **kwargs):
        custom_method_name = '%s_s2s_do_transaction' % self.acquirer_id.provider
        for trans in self:
            transaction_status = {}
            transaction_status.update({
                'state': 'done',
                'date': fields.Datetime.now(),
                'state_message': request.session.get('reason'),
                'acquirer_reference': request.session.get('requestID') or '',
            })
            trans.write(transaction_status)
            trans._log_payment_transaction_sent()
            if hasattr(trans, custom_method_name):
                return getattr(trans, custom_method_name)(**kwargs)
