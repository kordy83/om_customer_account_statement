# -*- coding: utf-8 -*-
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2019 OM Apps 
#    Email : omapps180@gmail.com
#################################################

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError
from datetime import datetime


class ResPartner(models.Model):
    _inherit = "res.partner"
    
    by_date = fields.Boolean(string='By Date')
    to_date = fields.Date(string='To Date')
    customer_account_lines = fields.One2many('customer.account.line','partner_id', string='Customer Account Lines')
    customer_due_amount = fields.Monetary('Total Due Amount', compute='_get_customer_due_amount')
    customer_overdue_amount = fields.Monetary('Overdue Amount', compute='_get_customer_due_amount')
    not_due = fields.Monetary(string='Not Due')
    first_due = fields.Monetary(string='0-30')
    second_due = fields.Monetary(string='31-60')
    third_due = fields.Monetary(string='61-90')
    fourth_due = fields.Monetary(string='91-120')
    five_due = fields.Monetary(string='120-150')
    six_due = fields.Monetary(string='151-180')
    seven_due = fields.Monetary(string='Greater 180')

    vendor_account_lines = fields.One2many('vendor.account.line', 'partner_id', string='Vendor Account Lines')
    vendor_due_amount = fields.Monetary('Total Due Amount', compute='_get_vendor_due_amount')
    vendor_overdue_amount = fields.Monetary('Overdue Amount', compute='_get_vendor_due_amount')
    v_not_due = fields.Monetary(string='Not Due')
    v_first_due = fields.Monetary(string='0-30')
    v_second_due = fields.Monetary(string='31-60')
    v_third_due = fields.Monetary(string='61-90')
    v_fourth_due = fields.Monetary(string='91-120')
    v_five_due = fields.Monetary(string='120-150')
    v_six_due = fields.Monetary(string='151-180')
    v_seven_due = fields.Monetary(string='Greater 180')

    def _get_customer_due_amount(self):
        for rec in self:
            due_amount=0
            overdue_amount = 0
            for line in rec.customer_account_lines:
                due_amount += line.balance
                if line.is_due:
                    overdue_amount += line.balance
            rec.customer_due_amount = due_amount
            rec.customer_overdue_amount = overdue_amount

    def _get_vendor_due_amount(self):
        for rec in self:
            due_amount=0
            overdue_amount = 0
            for line in rec.vendor_account_lines:
                due_amount += line.balance
                if line.is_due:
                    overdue_amount += line.balance
            rec.vendor_due_amount = due_amount
            rec.vendor_overdue_amount = overdue_amount
    
    def get_payment_amount(self,move_line):
        pool = self.env['account.partial.reconcile'].sudo()
        if move_line.debit:
            payment_lines = pool.search([('debit_move_id','=',move_line.id),
                                         ('credit_move_id.date','<=',self.to_date)])
        else:
            payment_lines = pool.search([('credit_move_id','=',move_line.id),
                                         ('debit_move_id.date','<=',self.to_date)])
        
        amount = 0
        for payment in payment_lines:
            if move_line.debit:
                amount += payment.amount
            else:
                amount += payment.amount * -1
        return amount

    # def Initialize_statement(self):
    #     pool = self.env['account.move.line']
    #     domain = [('partner_id', '=', self.id),
    #               ('date', '<=', self.to_date),
    #               ('move_id.state', '=', 'posted'),
    #               ('account_id.account_type', '=', 'asset_receivable'),
    #               ('company_id', '=', self.env.company.id)]
    #     move_line_ids = pool.sudo().search(domain)
    #     vals = []
    #     for line in move_line_ids:

    def get_customer_lines(self):
        pool = self.env['account.move.line']
        domain = [('partner_id','=',self.id),
                  ('date','<=',self.to_date),
                  ('move_id.state','=','posted'),
                  ('account_id.account_type','=','asset_receivable'),
                  ('company_id','=',self.env.company.id)]
        move_line_ids = pool.sudo().search(domain)
        vals=[]
        for line in move_line_ids:
            if line.debit != line.credit:
                amount = line.debit or line.credit * -1
                paid_amount = self.get_payment_amount(line)
                print ("=======",amount,paid_amount)
                if (amount - paid_amount) != 0:
                    val={
                        'invoice_id':line.move_id and line.move_id.id or False,
                        'invoice_date':line.date,
                        'due_date':line.date_maturity,
                        'amount':amount,
                        'paid_amount':self.get_payment_amount(line),
                        'company_id':self.env.company.id or False,
                    }
                    vals.append((0,0,val))
        return vals

    def get_vendor_lines(self):
        pool = self.env['account.move.line']
        domain = [('partner_id','=',self.id),
                  ('date','<=',self.to_date),
                  ('move_id.state','=','posted'),
                  ('account_id.account_type','=','liability_payable'),
                  ('company_id','=',self.env.company.id)]
        move_line_ids = pool.sudo().search(domain)
        vals=[]
        for line in move_line_ids:
            if line.debit != line.credit:
                amount = line.debit or line.credit * -1
                paid_amount = self.get_payment_amount(line)
                print ("=======",amount,paid_amount)
                if (amount - paid_amount) != 0:
                    val={
                        'invoice_id':line.move_id and line.move_id.id or False,
                        'invoice_date':line.date,
                        'due_date':line.date_maturity,
                        'amount':amount,
                        'paid_amount':self.get_payment_amount(line),
                        'company_id':self.env.company.id or False,
                    }
                    vals.append((0,0,val))
        return vals

    def set_aging(self):
        c_date = datetime.now().date()
        not_due=0
        first_due = 0
        second_due = 0
        third_due = 0
        fourth_due = 0
        five_due = 0
        six_due = 0
        seven_due=0
        for line in self.customer_account_lines:
            if not line.due_date:
                line.due_date = line.invoice_id.invoice_line_ids[0].date_maturity
            if not line.due_date:
                line.due_date = line.invoice_id.invoice_line_ids[0].date
            days = (c_date - line.due_date).days

            if days < 0:
                not_due += line.balance
            elif days <= 30:
                first_due += line.balance
            elif days <= 60:
                second_due += line.balance
            elif days <= 90:
                third_due += line.balance
            elif days <= 120:
                fourth_due += line.balance
            elif days <= 150:
                five_due += line.balance
            elif days <= 180:
                six_due += line.balance
            else:
                seven_due += line.balance
        self.write({
            'not_due':not_due, 'first_due':first_due, 'second_due':second_due, 
            'third_due':third_due, 'fourth_due':fourth_due, 'five_due':five_due, 
            'six_due':six_due, 'seven_due':seven_due
        })

    def v_set_aging(self):
        c_date = datetime.now().date()
        not_due=0
        first_due = 0
        second_due = 0
        third_due = 0
        fourth_due = 0
        five_due = 0
        six_due = 0
        seven_due=0
        for line in self.vendor_account_lines:
            if not line.due_date:
                line.due_date = line.invoice_id.invoice_line_ids[0].date_maturity
            if not line.due_date:
                line.due_date = line.invoice_id.invoice_line_ids[0].date
            days = (c_date - line.due_date).days

            if days < 0:
                not_due += line.balance
            elif days <= 30:
                first_due += line.balance
            elif days <= 60:
                second_due += line.balance
            elif days <= 90:
                third_due += line.balance
            elif days <= 120:
                fourth_due += line.balance
            elif days <= 150:
                five_due += line.balance
            elif days <= 180:
                six_due += line.balance
            else:
                seven_due += line.balance
        self.write({
            'v_not_due':not_due, 'v_first_due':first_due, 'v_second_due':second_due,
            'v_third_due':third_due, 'v_fourth_due':fourth_due, 'v_five_due':five_due,
            'v_six_due':six_due, 'v_seven_due':seven_due
        })
    
    def generate_customer_account_lines(self):
        self.customer_account_lines.unlink()
        if self.by_date:
            if not self.to_date:
                self.to_date = datetime.now().date()
        else:
            self.to_date = datetime.now().date()
        
        line_ids = self.get_customer_lines()
        self.customer_account_lines = line_ids
        self.set_aging()

    def generate_vendor_account_lines(self):
        self.vendor_account_lines.unlink()
        if self.by_date:
            if not self.to_date:
                self.to_date = datetime.now().date()
        else:
            self.to_date = datetime.now().date()

        line_ids = self.get_vendor_lines()
        self.vendor_account_lines = line_ids
        self.v_set_aging()

    def send_customer_statement(self):
        self.generate_customer_account_lines()
        template_id = self.env['ir.model.data']._xmlid_to_res_id('om_customer_account_statement.send_customer_account_statement', raise_if_not_found=False)
        template_id = self.env['mail.template'].browse(template_id)
        template_id.send_mail(self.id, True)

    def send_vendor_statement(self):
        self.generate_vendor_account_lines()
        template_id = self.env['ir.model.data']._xmlid_to_res_id(
            'om_customer_account_statement.send_vendor_account_statement', raise_if_not_found=False)
        template_id = self.env['mail.template'].browse(template_id)
        template_id.send_mail(self.id, True)

    def print_customer_statement(self):
        self.generate_customer_account_lines()
        return self.env.ref('om_customer_account_statement.report_om_customer_statement').report_action(self, data={})

    def print_vendor_statement(self):
        self.generate_vendor_account_lines()
        return self.env.ref('om_customer_account_statement.report_om_vendor_statement').report_action(self, data={})


class CustomerAccountLines(models.Model):
    _name = 'customer.account.line'
    _description = 'Customer Account Lines'
    _order = 'invoice_date'
    
    invoice_id = fields.Many2one('account.move', string='Invoice Number')
    invoice_date = fields.Date(string='Invoice Date')
    due_date = fields.Date(string='Due Date')
    amount = fields.Monetary(string='Invoice Amount')
    paid_amount = fields.Monetary(string='Paid Amount')
    balance = fields.Monetary(string='Balance', compute='compute_balance')
    company_id = fields.Many2one('res.company', string='Company')
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    partner_id = fields.Many2one('res.partner', ondelete='cascade')
    is_due = fields.Boolean(string='Is Due', compute='compute_is_due')
    
    @api.depends('due_date')
    def compute_is_due(self):
        for line in self:
            if line.due_date < datetime.now().date() and line.balance > 0:
                line.is_due = True
            else:
                line.is_due = False
    
    @api.depends('amount','paid_amount')
    def compute_balance(self):
        for rec in self:
            rec.balance = rec.amount - rec.paid_amount

class VendorAccountLines(models.Model):
    _name = 'vendor.account.line'
    _description = 'Vendor Account Lines'
    _order = 'invoice_date'

    invoice_id = fields.Many2one('account.move', string='Invoice Number')
    invoice_date = fields.Date(string='Invoice Date')
    due_date = fields.Date(string='Due Date')
    amount = fields.Monetary(string='Invoice Amount')
    paid_amount = fields.Monetary(string='Paid Amount')
    balance = fields.Monetary(string='Balance', compute='compute_balance')
    company_id = fields.Many2one('res.company', string='Company')
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    partner_id = fields.Many2one('res.partner', ondelete='cascade')
    is_due = fields.Boolean(string='Is Due', compute='compute_is_due')

    @api.depends('due_date')
    def compute_is_due(self):
        for line in self:
            if line.due_date < datetime.now().date() and line.balance > 0:
                line.is_due = True
            else:
                line.is_due = False

    @api.depends('amount', 'paid_amount')
    def compute_balance(self):
        for rec in self:
            rec.balance = rec.amount - rec.paid_amount
