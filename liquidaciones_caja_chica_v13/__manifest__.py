# -*- coding: utf-8 -*-

{
    'name': 'Caja Chica & Liquidaciones',
    'version': '1.0',
    'category': 'Contabilidad',
	'description': """
	Cajas Chicas & Liquidaciones
	- Permite Liquidar facturas por cheques emitidos
	- Realiza registro por lotes de facturas de proveedor para asignar, validar y pagar con caja chica
	
	""",
    'author': 'Xetechs, S.A.',
    'support': 'Luis Aquino --> laquino@xetechs.com',
    'depends': ['hr','account', 'payment'],
    'data': [
		'views/liquidacion_caja_chica_view.xml',
        'views/payment_form.xml',
        'secuencias/secuencias.xml',
        'security/multicompany_cajachica_security.xml'
    ],
   
    'installable': True,
    'application': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
