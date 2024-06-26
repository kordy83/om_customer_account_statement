# -*- coding: utf-8 -*-
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2019 OM Apps 
#    Email : omapps180@gmail.com
#################################################

{
    'name': 'Customer Account Statement',
    'category': 'Account',
    'sequence':5,
    'version': '17.0.1.0',
    'summary': "Plugin will help to Print Customer Statement,Customer Bank Statement,Client Statement,Overdue Statement,Print Account Statement Report, Partner Statement of Account,Print Account Overdue Statement,send customer statement Odoo",
    'description': "Application Will help to print customer account statement. You can also send customer account statement or customer overdue account statement with ageing. ",
    'author': 'OM Apps',
    'website': '',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/customer_views.xml',
        'reports/report_template.xml',
        'reports/report.xml',
        'edi/mail_template_data.xml',
    ],
    'installable': True,
    'application': True,
    'images' : ['static/description/banner.png'],
    'license':'OPL-1',
    "price": 18,
    "currency": "EUR",
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
