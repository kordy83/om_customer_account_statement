# -*- coding: utf-8 -*-
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2019 OM Apps 
#    Email : omapps180@gmail.com
#################################################

from odoo import models, fields, api
from odoo.tools.misc import formatLang
from datetime import datetime,date


class customer_statement_report(models.AbstractModel):
    _name = 'report.om_customer_account_statement.cust_acc_template'
    _description="Customer Account Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['res.partner'].browse(docids)
        docargs = {
            'doc_ids':docids,
            'docs': docs,
            'doc_model': 'res.partner',
            'company':self.env.company,
        }
        return docargs

class vendor_statement_report(models.AbstractModel):
    _name = 'report.om_customer_account_statement.vendor_acc_template'
    _description="Vendor Account Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['res.partner'].browse(docids)
        docargs = {
            'doc_ids':docids,
            'docs': docs,
            'doc_model': 'res.partner',
            'company':self.env.company,
        }
        return docargs
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
