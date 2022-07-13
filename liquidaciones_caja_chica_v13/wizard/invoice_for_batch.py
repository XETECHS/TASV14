# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from itertools import groupby
from datetime import datetime, timedelta

from odoo import api, fields, models, tools, workflow, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang

import odoo.addons.decimal_precision as dp


class invoice_for_batch(models.TransientModel):
	_name = 'invoice.batch'
	_description = 'Facturacion por Lotes'
	#_columns = {
	date_start= fields.Date('Del:', required=True, default=fields.Datetime.now)
	date_end= fields.Date('Al:', required=True,default=fields.Datetime.now)
	user_id= fields.Many2one('res.users', 'Vendedor', required=False, help="Vendedor que se le asignaran la ventas",default=lambda self: self.env.user)
	journal_id= fields.Many2one('account.journal', 'Diario', required=True)
	payment_id= fields.Many2one('account.journal', 'Forma de Pago', required=True)
	caja_chica_id= fields.Many2one('caja.chica', 'Liquidacion', required=False, help="Liquidacion de a la que corresponde")
	invoice_batch_line= fields.One2many('invoice.batch.line', 'invoice_batch_id', 'Detalle')
	numero_facturas= fields.Integer('# Facturas', required=False, readonly=True)
	total_facturado= fields.Float('Total Facturado', readonly=True)
	
    @api.multi
    @api.onchange('date_start', 'date_end', 'journal_id')
	def onchange_invoice(self):
		invoice = self.env['account.move']
		res = {'value': {}}
		rs = {}
		total_facturas = 0.00
		invoice_list = []
		if self.journal_id:
			invoice_ids = invoice.search([['date_invoice' ,'>=', self.date_start], ['date_invoice','<=', self.date_end], ['state','=','open'], ['journal_id','=',self.journal_id.id]])
                        if invoice_ids:
                           print "invoice_ids"
   			for invoice in invoice_ids:
				total_facturas += invoice.amount_total
				rs = {
					'invoice_id': invoice.id,
					'fecha': invoice.date_invoice or False,
					'partner_id': invoice.partner_id.id or False,
					'amount_total': invoice.amount_total,
				}
				invoice_list.append((0, 0, rs))
			res['value']['invoice_batch_line'] = invoice_list
			res['value']['numero_facturas'] = len(invoice_ids)
			res['value']['total_facturado'] = total_facturas
		return res
		
    @api.multi
	def action_liquidar(self):
		liquidacion_obj = self.env['caja.chica'] 
		account_invoice = self.env['account.move']
		for line in self:
			for l in line.invoice_batch_line:
				l.invoice_id.write({'caja_chica_id': line.caja_chica_id.id})
			liquidacion_obj.action_liquidar() 
		return True
	
	@api.multi
	def action_validate_invoice(self):
		invoice = self.env['account.move']
		for line in self:
			for x_line in line.invoice_batch_line:
				invoice_id = x_line.invoice_id
				invoice_id.signal_workflow('invoice_open')
				if x_line.anular == True:
					invoice_id.signal_workflow('invoice_cancel')
				else:
					self.create_account_voucher(invoice_id.id, line.payment_id)
					invoice.write(invoice_id.id, {'user_id': line.user_id.id})
		return True
	
	@api.multi
	def create_account_voucher(self, invoice_id, payment_id):
		account_voucher = self.env['account.voucher'] 
		account_voucher_line = self.env['account.voucher.line'] 
		account_invoice = self.env['account.move']
		res = {}
		res_line = {}
		if invoice_id:
			for invoice in account_invoice.browse(invoice_id):
				res = {
                                        'partner_id': invoice.partner_id.id or False,
                                        'date': invoice.date_invoice,
                                        'amount': invoice.amount_total,
                                        'journal_id': payment_id.id or False,
                                        #'invoice_id': invoice.id or False,
                                        'account_id': payment_id.default_credit_account_id.id or payment_id.default_debit_account_id.id,
                                        'currency_id': payment_id.company_id.currency_id.id or False,
                                        'company_id' : payment_id.company_id.id or False,
                                        'state': 'draft',
                                        'pay_now': 'pay_now',
                                        'voucher_type': 'sale',

				}
				voucher_id = account_voucher.create(res)
                                for invoice_line in invoice.invoice_line_ids:
                                    res_line = {
                                        'voucher_id': voucher_id.id,
                                        'name': invoice_line.product_id.name,
                                        'company_id': payment_id.company_id.id or False,
                                        #'move_line_id': self.get_move_line(invoice.account_id, invoice.move_id, invoice.partner_id, invoice.am$
                                        'account_id': invoice_line.account_id.id, 
                                        'product_id': invoice_line.product_id.id,
                                        'price_unit': invoice_line.price_unit,
                                        'quantity': invoice_line.quantity,
                                        'tax_ids':[(4,t.id) for t in invoice_line.invoice_line_tax_ids],
                                    }
                                    account_voucher_line.create(res_line)
				account_voucher_line.create(res_line)
				voucher_id.signal_workflow('proforma_voucher')
			return True

	def get_move_line(self, account_id, move_id, partner_id, amount):
		account_move_line = self.env['account.move.line'] #self.pool.get('account.move.line')
		account_move = self.env['account.move'] #self.pool.get('account.move')
		move_line_id = False
		move_line_ids = account_move_line.search([('partner_id','=', partner_id.id), ('account_id','=', account_id.id), ('move_id','=', move_id.id), ('debit','=', amount)])
		if move_line_ids:
			for move in account_move_line.browse(move_line_ids):
				move_line_id = move.id
		return move_line_id



class invoice_for_batch_line(models.TransientModel):
	_name = 'invoice.batch.line'
	_description = 'Facturacion por Lotes detalle'
	invoice_batch_id= fields.Many2one('invoice.batch', required=False, ondelete="cascade")
	invoice_id= fields.Many2one('account.move', 'Factura', required=True, readonly=True)
	fecha= fields.Date('Fecha', required=False, readonly=True)
	partner_id= fields.Many2one('res.partner', 'Cliente', required=False, readonly=True)
	anular= fields.Boolean('Anular', required=False, default=False)
	amount_total= fields.Float('Monto', required=False, readonly=True)

