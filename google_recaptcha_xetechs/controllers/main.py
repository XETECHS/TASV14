import odoo.addons.web.controllers.main as main
from odoo import api, http, SUPERUSER_ID, _
import json
import urllib
import requests
from odoo.http import request, WebRequest
from odoo import http
import odoo
import collections
from odoo.addons.website_crm.controllers.main import WebsiteForm
from odoo.addons.website_sale.controllers.main import WebsiteSale

class Home(main.Home):
    
    @http.route('/web/login', type='http', auth="public")
    def web_login(self, redirect=None, **kw):
        copy_kw = kw.copy()
        GRCSudo = request.env.ref('google_recaptcha_xetechs.google_recaptcha_config').sudo()
        if GRCSudo.enable_recaptcha and GRCSudo.is_key_verified:
            if GRCSudo.enable_on_login:
                request.params['google_site_key'] = GRCSudo.re_site_key or ''
                if 'db' and 'login' and 'password' in kw:
                    "Start reCAPTCHA validation"
                    response = copy_kw.get('g-recaptcha-response')
                    g_url = 'https://www.google.com/recaptcha/api/siteverify'
                    secret = GRCSudo.re_secret_key or ''
                    captcha_values = {
                        'secret': secret,
                        'response': response
                    }
                    data = urllib.parse.urlencode(captcha_values).encode()
                    req =  urllib.request.Request(g_url, data=data)
                    response = urllib.request.urlopen(req)
                    result = json.loads(response.read().decode())
                    ''' End reCAPTCHA validation '''
                    if not result['success']:
                        request.params['login_success'] = False
                        if request.httprequest.method == 'GET' and redirect and request.session.uid:
                            return http.redirect_with_hash(redirect)
                        if not request.uid:
                            request.uid = odoo.SUPERUSER_ID
                        values = request.params.copy()
                        try:
                            values['databases'] = request.session.db
                        except odoo.exceptions.AccessDenied:
                            values['databases'] = None
                        if 'invalid-input-secret' in result.get('error-codes'):
                            values['error'] = _("Invalid reCAPTCHA secret key. \n Please contact admin!") 
                        else:
                            values['error'] = _("Invalid reCAPTCHA. Please try again!")  
                        return request.render('web.login', values)
#                         return http.redirect_with_hash('/web/login')

        login_response = super(Home, self).web_login(redirect=None, kw=copy_kw)
        return login_response

class CaptchaValidation(http.Controller):  
    
    @http.route('/captcha_validation', type='http', auth="user", csrf=False, website=True)
    def google_captcha_validation(self, redirect=None, **kw):
        values = {}
        recaptcha_data = request.env.ref('google_recaptcha_xetechs.google_recaptcha_config')
        site_key = recaptcha_data.re_site_key or ''
        secret_key = recaptcha_data.re_secret_key or ''
        values.update({'site_key': site_key})
        
        if not kw.get('g-recaptcha-response') == None:
            response = kw.get('g-recaptcha-response')
            g_url = 'https://www.google.com/recaptcha/api/siteverify'
            captcha_values = {
                'secret': secret_key,
                'response': response
            }
            data = urllib.parse.urlencode(captcha_values).encode()
            req =  urllib.request.Request(g_url, data=data)
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())
            ''' End reCAPTCHA validation '''
            if result['success'] == True:
                recaptcha_data = request.env.ref('google_recaptcha_xetechs.google_recaptcha_config')
                quote_url =""
                action =  request.env.ref('google_recaptcha_xetechs.action_google_recaptcha_config')
                menu_id = request.env.ref('google_recaptcha_xetechs.menu_google_recaptcha_config')
                quote_url =  '/web#id=%s&view_type=form&model=sale.order&action=%s&menu_id=%s'%(recaptcha_data.id,action.id,menu_id.id)
                recaptcha_data.is_key_verified = True
                return request.redirect(quote_url)
            else:
                values['error'] = _("Invalid reCAPTCHA. Validation Faild! \n Please try again! make sure your keys are valid.")
        
        return request.render('google_recaptcha_xetechs.google_captcha_validation', values)
        
        
        
class ContactusFormRecaptcha(http.Controller):

    # Check and insert values from the form on the model <model>
    @http.route('/contactus', type='http', auth="public", website=True)
    def contactus_recapthca(self, **kwargs):
        GRCSudo = request.env.ref('google_recaptcha_xetechs.google_recaptcha_config').sudo()
        if GRCSudo.enable_recaptcha and GRCSudo.is_key_verified:
            if GRCSudo.enable_on_contact_us:
                request.params['google_site_key'] = GRCSudo.re_site_key or ''
        return request.render("website.contactus", **kwargs)

class WebsiteForm(WebsiteForm):

    # Check and insert values from the form on the model <model>
    @http.route('/website_form/<string:model_name>', type='http', auth="public", methods=['POST'], website=True)
    def website_form(self, model_name, **kwargs):
        copy_kw = kwargs.copy()
        if model_name == 'crm.lead' and not request.params.get('state_id'):
            GRCSudo = request.env.ref('google_recaptcha_xetechs.google_recaptcha_config').sudo()
            if GRCSudo.enable_recaptcha and GRCSudo.is_key_verified:
                if GRCSudo.enable_on_contact_us:
                    request.params['google_site_key'] = GRCSudo.re_site_key or ''
                    "Start reCAPTCHA validation"
                    response = copy_kw.get('g-recaptcha-response')
                    g_url = 'https://www.google.com/recaptcha/api/siteverify'
                    secret = GRCSudo.re_secret_key or ''
                    captcha_values = {
                        'secret': secret,
                        'response': response
                    }
                    data = urllib.parse.urlencode(captcha_values).encode()
                    req =  urllib.request.Request(g_url, data=data)
                    response = urllib.request.urlopen(req)
                    result = json.loads(response.read().decode())
                    if not result['success']:
                        request.params['login_success'] = False
                        values = request.params.copy()
                        if 'invalid-input-secret' in result.get('error-codes'):
                            values['error'] = _("Invalid reCAPTCHA secret key. \n Please contact admin!") 
                        else:
                            values['error'] = _("Invalid reCAPTCHA. Please try again!") 
                        return request.render('website.contactus',  values)
                    ''' End reCAPTCHA validation '''
        if kwargs.get('g-recaptcha-response'):
            kwargs.pop('g-recaptcha-response')
        return super(WebsiteForm, self).website_form(model_name, **kwargs)


class WebsiteSaleProductComparison(WebsiteSale):
    @http.route(['/shop/payment'], type='http', auth="public", website=True, sitemap=False)
    def payment(self, **post):
        GRCSudo = request.env.ref('google_recaptcha_xetechs.google_recaptcha_config').sudo()
        if GRCSudo.enable_recaptcha and GRCSudo.is_key_verified:
            if GRCSudo.enable_on_contact_us:
                request.params['google_site_key'] = GRCSudo.re_site_key or ''

        order = request.website.sale_get_order()
        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        render_values = self._get_shop_payment_values(order, **post)
        render_values['only_services'] = order and order.only_services or False

        if render_values['errors']:
            render_values.pop('acquirers', '')
            render_values.pop('tokens', '')

        return request.render("website_sale.payment", render_values)
