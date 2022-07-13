# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from itertools import groupby
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang

import odoo.addons.decimal_precision as dp

class AccountMove(models.Model):
	_inherit = "account.move"
	
	@api.constrains('name', 'journal_id', 'state')
	def _check_unique_sequence_number(self):
		moves = self.filtered(lambda move: move.state == 'posted')
		if not moves:
			return
		else:
			return

        #self.flush()

        # /!\ Computed stored fields are not yet inside the database.
        #self._cr.execute('''
        #    SELECT move2.id, move2.name
        #    FROM account_move move
        #    INNER JOIN account_move move2 ON
        #        move2.name = move.name
        #        AND move2.journal_id = move.journal_id
        #        AND move2.move_type = move.move_type
        #        AND move2.id != move.id
        #    WHERE move.id IN %s AND move2.state = 'posted'
        #''', [tuple(moves.ids)])
        #res = self._cr.fetchall()
        #if res:
        #    raise ValidationError(_('Posted journal entry must have an unique sequence number per company.\n'
        #                            'Problematic numbers: %s\n') % ', '.join(r[1] for r in res))

AccountMove()


class caja_chica(models.Model):
	_name = "caja.chica"
	_description = "Liquidacion de Caja Chica"
	_order = 'id desc'
	
	@api.depends('invoice_ids', 'payment_ids')
	def _compute_total(self):
		for l in self:
			amount_total = amount_payments = 0.0
			for invoice in l.invoice_ids:
				amount_total += invoice.amount_total
			for pay in l.payment_ids:
				amount_payments += pay.amount
				#amount_tax += line.price_tax
			l.update({
				'amount_invoices': amount_total,
				'amount_payment': amount_payments,
				'amount_residual': (amount_payments - amount_total),
			})


	name= fields.Char('Liquidacion', required=True, readonly=True, states={'draft': [('readonly', False)]}, help="Nombre descriptivo de la liquidacion de la caja chica")
	number= fields.Char('Correlativo', required=False, readonly=True, states={'draft': [('readonly', False)]}, help="Correlativo de la liquidacion de la caja chica")
	date= fields.Date('Fecha', required=True, readonly=True, states={'draft': [('readonly', False)]}, help="Fecha de la liquidacion",default=fields.Date.today())
	state= fields.Selection([('draft', 'Borrador'),
								  ('valido', 'Validada'),
								  ('liquida', 'Liquidada'),
								  ('anulada', 'Anulada')], 'Estado', required=False, readonly=True, help="Estado de la liquidacion", default='draft')
	journal_id= fields.Many2one('account.journal', 'Diario', required=True, readonly=True, states={'draft': [('readonly', False)]}, help="Diario con se emitira la forma de pago")
	company_id= fields.Many2one('res.company', 'Empresa', required=False, readonly=True, default=lambda self: self.env['res.company']._company_default_get('caja.chica'))
	notas= fields.Text('Notas Internas', required=False, readonly=True, states={'draft': [('readonly', False)]})
	invoice_ids= fields.One2many('account.move', 'caja_chica_id', 'Facturas', readonly=True, states={'draft': [('readonly', False)]})
	payment_ids = fields.Many2many("account.payment", string='Cheques', readonly=False, copy=False, states={'draft': [('readonly', False)]})
	employee_id = fields.Many2one('hr.employee', 'Colaborador', required=True, readonly=True, states={'draft': [('readonly', False)]})
	currency_id = fields.Many2one("res.currency", string="Moneda", related="journal_id.currency_id", readonly=True)
	amount_payment = fields.Monetary('Cheques', compute="_compute_total", store=True, readonly=True, track_visibility='always')
	amount_residual = fields.Monetary('Saldo', compute="_compute_total", store=True, readonly=True, track_visibility='always')
	amount_invoices = fields.Monetary(string='Facturas', store=True, readonly=True, compute='_compute_total', track_visibility='always')
	
	@api.model
	def create(self, vals):
		sequence = self.env['ir.sequence'].next_by_code('caja.chica') or 'New'#unicode(self.pool.get('ir.sequence').get(cr, uid, 'caja.chica'))
		vals['number'] = sequence
		return super(caja_chica, self).create(vals)
		
	def action_validar(self):
		return self.write({'state': 'valido'})
	
	def action_cancelar(self):
		return self.write({'state': 'anulada'})
	def action_liquidar(self):
		invoices_ids = []
		invoice = self.env['account.move']
		for line in self:
			if not line.invoice_ids:
				raise UserError(_('No se puede procesar la liquidacion porque no tiene facturas asignadas..!'))
			for x_line in line.invoice_ids:
				invoice_id = x_line
				if invoice_id.state=='draft':
					invoice_id.post()
					#invoices_ids.append(invoice_id.id)
					#invoice_id.write({'state': 'paid'})
					self.action_payment_invoice(invoice_id)
			self.write({'state': 'liquida'})
		return True
		

	def action_payment_invoice(self, invoice):
		payment_obj = self.env['account.payment']
		pay = {}
		domain = [('account_internal_type', 'in', ('receivable', 'payable')), ('reconciled', '=', False)]
		for l in self:
			pay = {
				'payment_type' : 'outbound',
				'payment_method_id': self.get_payment_method().id or 2,
				'partner_type': 'supplier',
				'partner_id': invoice.partner_id.id,
				'amount': invoice.amount_total or 0.00,
				'currency_id': l.journal_id.currency_id.id or invoice.currency_id.id,
				'destination_account_id': invoice.line_ids[0].account_id.id,
				'journal_id': l.journal_id.id,
				'date': l.date or fields.Date.today(),
				'ref': 'Liquidacion No. %s'  %(l.name)
			}
			pay_id = payment_obj.create(pay)
			pay_id.action_post()
			if pay_id and invoice:
				payment_lines = pay_id.line_ids.filtered_domain(domain)
				invoice_lines = invoice.line_ids.filtered_domain(domain)
				for account in payment_lines.account_id:
					(payment_lines + invoice_lines).filtered_domain([('account_id', '=', account.id), ('reconciled', '=', False)]).reconcile()
				#invoice.write({
				#	'payment_id': pay_id.id or False,
				#})

	def get_payment_method(self):
		method_id = False
		method_obj = self.env['account.payment.method']
		method_id = method_obj.search([('code', '=', 'manual'), ('payment_type', '=', 'outbound')], limit=1)
		return method_id

class account_invoice(models.Model):
	_inherit = "account.move"
	#_columns = {
	caja_chica_id= fields.Many2one('caja.chica', 'Liquidacion', required=False, readonly=True, copy=False, states={'draft': [('readonly', False)]}, help="Liquidacion de a la que corresponde")
	

