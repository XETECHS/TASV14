# -*- coding: utf-8 -*-

from odoo import models, fields, api

from datetime import datetime

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    comments = fields.Text(string='Comments')
    title = fields.Char('Title', help="SO Title", required=True)
    is_project = fields.Boolean('Is Project', help="Select an existing project")
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', copy=False)
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tag', copy=False)
    project_id = fields.Many2one('project.project', string='Project', copy=False)
    project_date_start = fields.Date(string='Start Date')
    project_date = fields.Date(string='Expiration Date', index=True, tracking=True)
    presentation_date = fields.Date(string='Fecha de Entrega', help="Fecha usada para el reporte Trabajos Extra Realizados")

    
    @api.onchange('title')
    def _onchange_title(self):
        if not self.title:
            return
        self.title = self.title.capitalize()

    def _analytic_account_line(self, analytic_id, analytic_tag_ids):
        self.ensure_one()
        for line in self.order_line:
            line.write( dict(analytic_account_id=analytic_id.id, analytic_tag_ids=[(6, 0, analytic_tag_ids.ids)]) )
        return True

    #def _requisiton_lines(self, order):
    #    if order:
    #        for line in order.

    def _create_project(self):
        project = self.env['project.project']
        analytic = self.env['account.analytic.account']
        analytic_tag = self.env['account.analytic.tag']
        lines = []
        res_lines = []
        for record in self:
            if not record.is_project:
                lines = self._create_project_requisition_lines()
                name = '%s %s'%( record.partner_id.name, record.title)
                analytic_id = analytic.create({
                    'name': name,
                    'company_id': record.company_id.id,
                    'partner_id': record.partner_id.id
                })
                analytic_tag_id = analytic_tag.create( dict(name=name) )

                project_id = project.create({
                    'name': name,
                    'user_id': self.env.user.id,
                    'sale_id': self.id or False,
                    'partner_id': record.partner_id.id,
                    'date_start' : self.project_date_start,
                    'date' : self.project_date,
                    'analytic_account_id': analytic_id.id,
                    'project_requisition_lines_ids': lines,
                    'analytic_tag_ids': [(6, 0 , [analytic_tag_id.id])]
                })

                record.write({
                    'analytic_account_id': analytic_id.id,
                    'project_id':project_id.id,
                    'analytic_tag_ids': [(6, 0 , [analytic_tag_id.id])]
                })
                record._analytic_account_line(analytic_id, analytic_tag_id)
        return True

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        self._create_project()
        self.create_task()
        self._create_stock_location()
        return res

    @api.onchange('project_id')
    def _onchange_project_id(self):
        if not self.project_id:
            return
        self.analytic_account_id = self.project_id.analytic_account_id
        self.analytic_tag_ids = self.project_id.analytic_tag_ids
    
    def create_task(self):
        parent_id = False
        parent_task = {}
        task = self.env['project.task']
        for line in self.order_line:
            if line.product_id.is_task:
                parent_task = {
                    'name': line.name,
                    'project_id': self.project_id.id,
                    'partner_id': self.partner_id.id,
                    'date_assign': datetime.now(),
                    'date_deadline': self.validity_date,
                    'description': line.name,
                    'user_id': self.env.uid,
                }
                if line.product_uom.name == 'Mts²':
                    parent_task['planned_m2'] = line.product_uom_qty
                elif line.product_uom.name in ('Mts', 'Metro Ln'):
                    parent_task['planned_m'] = line.product_uom_qty
                else:
                    parent_task['planned_hours'] = line.product_uom_qty
                
                parent_id = task.create(parent_task)

        return True
    
    def _create_project_requisition_lines(self):
        lines = []
        #products = {}
        #product_obj = self.env['product.product']
        for rec in self:
            #for line in rec.order_line:
            order_lines_dict, cost_lines_dict = self.group_by_product(order_lines=rec.order_line)
            for key, items in cost_lines_dict.items():
                qty_per_line = 0.00
                product_rec = self.env['product.product'].browse([key])
                res = {
                        'product_id': product_rec.id or False,
                        'name': product_rec.name,
                        'quantity': qty_per_line or 0.00,
                        'product_uom': product_rec.uom_id.id or False, 
                }
                lines.append((0,0, res))
            for key, items in order_lines_dict.items():
                qty_per_line = 0.00
                product_rec = self.env['product.product'].browse([key])
                for item in self.env['sale.order.line'].browse(items):
                    qty_per_line += item.product_uom_qty or 0.00
                res = {
                        'product_id': product_rec.id or False,
                        'name': product_rec.name,
                        'quantity': qty_per_line or 0.00,
                        'product_uom': product_rec.uom_id.id or False, 
                }
                lines.append((0,0, res))
        return lines

    def group_by_product(self, order_lines=False):
        order_lines_dict = {}
        cost_lines_dict = {}
        if order_lines:
            for line in order_lines:
                if line.product_id.type == 'product':
                    if line.product_id.id not in order_lines_dict:
                        order_lines_dict[line.product_id.id] = []
                    order_lines_dict[line.product_id.id].append(line.id)

        return order_lines_dict, cost_lines_dict

    def _create_stock_location(self):
        location_obj = self.env['stock.location']
        location_id = location_obj.create({
            'name': self.project_id.name,
            'usage': 'internal',
            'comment': self.project_id.name,
        })
        if location_id:
            self.project_id.write({
                'stock_location_id': location_id and location_id.id,
            })
        return True

    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        if self.project_id:
            self.project_id.write({
                'active': False,
            })
            self.project_id.stock_location_id.write({
                'active': False,
            })
        if self.analytic_account_id and self.analytic_tag_ids:
            self.analytic_account_id.write({
                'active': False,
            })
            self.analytic_tag_ids.write({
                'active': False,
            })
        return res
SaleOrder()

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')

SaleOrderLine()
