# -*- coding: utf-8 -*-

from odoo import models, fields, api

from datetime import datetime

class StockPicking(models.Model):
    _inherit = "stock.picking"

    project_id = fields.Many2one('project.project', 'Proyecto', required=False, readonly=False)
StockPicking()