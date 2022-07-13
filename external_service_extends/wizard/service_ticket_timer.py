# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo import api, fields, models, _

_logger = logging.getLogger( __name__ )

class ServiceTicketTimer(models.TransientModel):
    _name = 'service.ticket.timer'
    _description = 'Service Ticket Timer'

    condition = fields.Boolean('Condition', help="True if Start timer else Stop timer")

    def apply_condition(self):
        active_model = self.env.context.get("active_model")
        active_id = self.env.context.get("active_id")
        ticket = self.env[active_model].browse( active_id )
        # Constraint:  not more of one user at boleta when the state is process 
        # Part of timer ON or OFF
        if self.condition:
            exists_users = self.env['project.tasks.service.ticket'].search( [('user_id', '=', ticket.user_id.id ), ('state', '=', 'process')])
            if len(exists_users.ids) > 0:
                raise ValidationError("Un colaborador no puede tener dos boletas en proceso al mismo tiempo")
            ticket.write({
                "state" : "process",
                "hours_planned_in": datetime.now(),
                "status_timer": "started"
            })
        else:
            ticket.write({
                "state":"closed",
                "hours_planned_out": datetime.now(),
                "status_timer": "finished"
            })
            ticket.action_compute_timer()
        
        return
