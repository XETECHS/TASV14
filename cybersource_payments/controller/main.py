import werkzeug
import requests
import json
import logging

from uuid import uuid4
from suds.wsse import Security, UsernameToken
from suds.client import Client
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from requests import get
from suds.sudsobject import asdict
from datetime import datetime, timedelta
from odoo import http, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.web.controllers import main as web
_logger = logging.getLogger(__name__)

reason_code = {
    100: 'Successful transaction',
    101: 'The request is missing one or more required fields',
    102: 'One or more fields in the request contains invalid data',
    104: 'The merchantReferenceCode sent with this authorization request matches the merchantReferenceCode of another authorization request that you sent in the last 15 minutes.',
    150: 'Error: General system failure',
    151: 'Error: The request was received but there was a server timeout. This error does not include timeouts between the client and the server.',
    152: 'Error: The request was received, but a service did not finish running in time',
    201: 'The issuing bank has questions about the request. You do not receive an authorization code in the reply message, but you might receive one verbally by calling the processor',
    202: 'Expired card. You might also receive this if the expiration date you provided does not match the date the issuing bank has on file',
    203: 'General decline of the card. No other information provided by the issuing bank',
    204: 'Insufficient funds in the account',
    205: 'Stolen or lost card',
    207: 'Issuing bank unavailable',
    208: 'Inactive card or card not authorized for card-not-present transactions',
    210: 'The card has reached the credit limit',
    211: 'Invalid card verification number',
    221: 'The customer matched an entry on the processor\'s negative file',
    231: 'Invalid account number',
    232: 'The card type is not accepted by the payment processor',
    233: 'General decline by the processor',
    234: 'There is a problem with your CyberSource merchant configuration',
    235: 'The requested amount exceeds the originally authorized amount. Occurs, for example, if you try to capture an amount larger than the original authorization amount. This reason code only applies if you are processing a capture through the API',
    236: 'Processor Failure',
    238: 'The authorization has already been captured. This reason code only applies if you are processing a capture through the API',
    239: 'The requested transaction amount must match the previous transaction amount. This reason code only applies if you are processing a capture or credit through the API',
    240: 'The card type sent is invalid or does not correlate with the credit card number',
    241: 'The request ID is invalid. This reason code only applies when you are processing a capture or credit through the API',
    242: 'You requested a capture through the API, but there is no corresponding, unused authorization record. Occurs if there was not a previously successful authorization request or if the previously successful authorization has already been used by another capture request. This reason code only applies when you are processing a capture through the API',
    243: 'The transaction has already been settled or reversed',
    246: 'The capture or credit is not voidable because the capture or credit information has already been submitted to your processor. Or, you requested a void for type a of transaction that cannot be voided. This reason code applies only if you are processing a void through the API',
    247: 'You requested a credit for a capture that was previously voided. This reason code applies only if you are processing a void through the API',
    250: 'Error: The request was received, but there was a timeout at the payment processor',
    520: 'The authorization request was approved by the issuing bank but declined by CyberSource based on your Smart Authorization settings',
    400: 'Soft Decline - Fraud score exceeds threshold.'
}

class WebsiteSale(WebsiteSale):
    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        response = super(WebsiteSale, self).shop(page=page, category=category, search=search, ppg=ppg, **post)
        payment_acquirer = request.env['payment.acquirer'].sudo().search([('provider', '=', 'cybersource')])
        payment_token = request.env['payment.token'].sudo().search([('acquirer_id', '=', payment_acquirer.id)])
        if payment_acquirer.save_token == 'none':
            for token_id in payment_token:
                token_id.unlink()
        if post.get('error'):
            return request.render('cybersource_payments.PaymentFailed',{'reason' : request.session.get('reason')})
            request.session['reason'] = False
        return response

class CyberSourceController(http.Controller):
    
    def recursive_dict(self,d):
        out = {}
        for k, v in asdict(d).items():
            if hasattr(v, '__keylist__'):
                out[k] = self.recursive_dict(v)
            elif isinstance(v, list):
                out[k] = []
                for item in v:
                    if hasattr(item, '__keylist__'):
                        out[k].append(self.recursive_dict(item))
                    else:
                        out[k].append(item)
            else:
                out[k] = v
        return out
    
    @http.route(['/payment/cybersource/s2s/create_json_3ds'], type='json', auth='public', csrf=False)
    def cybersource_s2s_create_json_3ds(self, verify_validity=False, **kwargs):
        order_id = request.session.get('sale_order_id')
        order = request.env['sale.order'].sudo().search([('id', '=', order_id)])
        payment_acquirer = request.env['payment.acquirer'].sudo().search([('id', '=', kwargs.get('acquirer_id'))])
        responseData = self.request_payment_status(kwargs)
        data = json.loads(json.dumps(self.recursive_dict(responseData)))
        reason = reason_code.get(data.get('reasonCode'), 'Invalid Data')
        return_url = '/'
        data.update({'amount' : order.amount_total,'id' : order.name, 'reason' : reason})
        request.session['reason'] = reason
        if responseData:
            if data.get('reasonCode') == 100 or data.get('reasonCode') == 480:
                token_id = request.env['payment.token'].sudo().create({'partner_id':order.partner_id.id,'acquirer_id':payment_acquirer.id,
                            'acquirer_ref':order.name,'active':True,'name': 'XXXXXXXXXXXX%s - %s' % (kwargs.get('cc_number')[-4:], kwargs.get('cc_holder_name'))})
                return_url = '/shop/confirmation'
                request.session['requestID'] = data.get('requestID')
            else:
                return_url = '/shop/payment'
            transaction = request.env['payment.transaction'].sudo().form_feedback(data, 'cybersource')
        if data.get('reasonCode') == 100 or data.get('reasonCode') == 480 :
            return {
                'result': True,
                '3d_secure': False,
                'id': token_id.id,
                'short_name': token_id.acquirer_ref,
                'verified': True,
                }
        else:
            return {
                'result': False,
                '3d_secure': False,
                'verified': True,
                }
            
    @http.route(['/shop/confirmation'], type='http', auth="public", website=True)
    def payment_confirmation(self, **post):
        print('test')
        payment_acquirer = request.env['payment.acquirer'].sudo().search([('provider', '=', 'cybersource')])
        payment_token = request.env['payment.token'].sudo().search([('acquirer_id', '=', payment_acquirer.id)])
        if payment_acquirer.save_token == 'none':
            for token_id in payment_token:
                token_id.unlink()
        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            if not order or order.state != 'draft':
                request.website.sale_reset()
            return request.render("website_sale.confirmation", {'order': order})
        else:
            return request.redirect('/shop/payment')
        
    def request_payment_status(self,post):
        order_id = request.session.get('sale_order_id')
        order = request.env['sale.order'].sudo().search([('id', '=', order_id)])
        kwargs = {}
        payment_acquire = request.env['payment.acquirer'].sudo().search([('id', '=', post.get('acquirer_id'))])
        if payment_acquire.state == 'enabled':
            wsdl = 'https://ics2wsa.ic3.com/commerce/1.x/transactionProcessor/CyberSourceTransaction_1.141.wsdl'
        else:
            wsdl = 'https://ics2wstesta.ic3.com/commerce/1.x/transactionProcessor/CyberSourceTransaction_1.141.wsdl'
        transaction_security_key = payment_acquire.cybersource_key
        merchant_id = payment_acquire.cybersource_merchant_id
        self.merchant_id = merchant_id
        self.client = Client(wsdl)
        security = Security()
        token = UsernameToken(self.merchant_id, transaction_security_key)
        security.tokens.append(token)
        self.client.set_options(wsse=security)
        data = {}
        data['merchantID'] = self.merchant_id
        data['merchantReferenceCode'] = self.merchant_id
        data['purchaseTotals'] = self.client.factory.create('ns0:PurchaseTotals')
        data['purchaseTotals'].currency = order.pricelist_id.currency_id.name or 'USD'
        data['purchaseTotals'].grandTotalAmount = order.amount_total
        data['pos'] = self.client.factory.create('ns0:pos')
        data['billTo'] = self.client.factory.create('ns0:BillTo')
        data['billTo'].email = order.partner_id.email
        data['billTo'].firstName = order.partner_id.name
        data['billTo'].lastName = order.partner_id.name
        data['billTo'].street1 = order.partner_id.street
        data['billTo'].street2 = order.partner_id.street2 or None
        data['billTo'].city = order.partner_id.city
        data['billTo'].state = order.partner_id.state_id.code
        data['billTo'].postalCode = order.partner_id.zip
        data['billTo'].country = order.partner_id.country_id.code
        data['billTo'].ipAddress = get('https://api.ipify.org').text
        data['shipTo'] = self.client.factory.create('ns0:shipTo')
        data['shipTo'].firstName = order.partner_id.name
        data['shipTo'].lastName = order.partner_id.name
        data['shipTo'].street1 = order.partner_id.street
        data['shipTo'].street2 = order.partner_id.street2 or None
        data['shipTo'].city = order.partner_id.city
        data['shipTo'].state = order.partner_id.state_id.code
        data['shipTo'].country = order.partner_id.country_id.code
        data['shipTo'].postalCode = order.partner_id.zip
        data['apPaymentType'] = 'EPS'
        data['card'] = self.client.factory.create('ns0:Card')
        data['card'].accountNumber = int(post.get('cc_number').replace(" ", ""))
        data['card'].expirationMonth = int(post.get('cc_expiry')[:2])
        data['card'].expirationYear = int('20' + post.get('cc_expiry')[5:])
        data['card'].cvNumber = post.get('cc_cvc')
        data['ccAuthService'] = self.client.factory.create('ns0:ccAuthService')
        data['ccAuthService']._run = 'true'
        data['ccCaptureService'] = self.client.factory.create('ns0:ccCaptureService')
        data['ccCaptureService']._run = 'true'
        data['deviceFingerprintID'] = order.id
        try:
            resp = self.client.service.runTransaction(**data)
        except Exception as e:
            resp = None
        return resp
