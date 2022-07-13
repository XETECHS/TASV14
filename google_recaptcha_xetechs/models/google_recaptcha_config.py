from odoo import api, fields, models, _



class GoogleRecaptchaConfig(models.Model):
    _name = 'google.recaptcha.config'
    
    name = fields.Char(string="Name", default="Google reCAPTCHA Configuration")
    enable_recaptcha = fields.Boolean(string="Enable reCAPTCHA")
    re_site_key = fields.Char(string="Site Key")
    re_secret_key = fields.Char(string="Secret Key")
    enable_on_login = fields.Boolean(string="Enable on Login")
    is_key_verified = fields.Boolean(string="reCAPTCHA Key Verified")
    enable_on_contact_us = fields.Boolean(string="Enable on Contact Us Form")
    
    @api.onchange('enable_recaptcha')
    def onchnage_enable_recaptcha(self):
        if self.enable_recaptcha:
            self.enable_on_login = True
        else:
            self.enable_on_login = False
            
    @api.onchange('re_site_key', 're_secret_key')
    def onchange_google_keys(self):
        self.is_key_verified = False
        
    def verify_google_keys(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return {
                "type": "ir.actions.act_url",
                "url": base_url + '/captcha_validation',
                "target": "self",
            }
    
