from odoo import fields, models


class ProfitAndLoss(models.Model):
    _name = 'profit.and.loss'
    _description = 'Profit and Loss'
    _rec_name = 'connection_categ'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True)
    pnl_line_connection = fields.One2many('profit.and.loss.line', 'pnl_connection', store=True)
    connection_categ = fields.Many2one('category', string='Category')

    sub_category = fields.Many2one('sub.categ', string='Sub Category',
                                   domain="[('connection_categ', '=', connection_categ)]", default=0)


    is_pnl_or_bs = fields.Selection([
        ('pnl', 'Profit and loss',),
        ('bs', 'Balance Sheet')], string='Profit and Loss or Balance Sheet', related='connection_categ.is_pnl_or_bs',
        store=True)
    # code = fields.Char(string='Code Sequence', required=True, default='00001', related='connection_categ.code',
    #                    store=True)

    # def name_get(self):
    #     result = []
    #     for rec in self:
    #         result.append((rec.id, '%s - %s' % (rec.code, rec.connection_categ)))
    #     return result


class ProfitAndLossLine(models.Model):
    _name = 'profit.and.loss.line'
    _rec_name = 'account_id'

    pnl_connection = fields.Many2one('profit.and.loss', string='Connection')
    account_id = fields.Many2one('account.account', string='Chart of Account')
