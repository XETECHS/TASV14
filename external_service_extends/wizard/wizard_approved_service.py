# -*- coding: utf-8 -*-

from odoo import models, fields, api

class WizardApprovedService(models.TransientModel):
    _name = 'wizard.service.approved'
    _description = "Aprobar servicios en Batch"

    def action_batch_cancel(self):
        active_ids = self.env.context.get('active_ids')
        move_obj = self.env['project.tasks.service.ticket']
        for service in move_obj.browse(active_ids):
            service.approved()
        return True

WizardApprovedService()