from odoo import api, fields, models, _



class ResCompany(models.Model):
    _inherit = 'res.company'

    enviroment_selection = [
        ('1snn5n9w', 'Test Enviroment'),
        ('k8vif92e', 'Prod Enviroment'),
    ]
    cybersource_merchant_id = fields.Char('Merchant id Cybersource', default="dummy")
    cybersource_org_id = fields.Selection(enviroment_selection, string="Org ID")

