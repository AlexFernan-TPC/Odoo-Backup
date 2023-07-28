from odoo import fields, models, api, tools
import pandas as pd

class BalanceSheet(models.Model):
    _name = 'balance.sheet'
    _description = 'Balance Sheet'
    _auto = False
    _order = 'root asc'

    root = fields.Char(string='Name')
    sub_category = fields.Many2one('sub.categ', string='Sub Category')
    account_id = fields.Many2one('account.account', string='Chart of Accounts')
    main_category = fields.Many2one('category', string='Category')
    date = fields.Char(string='Date')
    monthly = fields.Char(string='Monthly')
    yearly = fields.Char(string='Yearly')
    debit = fields.Monetary(string='debit')
    credit = fields.Monetary(string='credit')
    balance = fields.Monetary(string='Balance')
    grouped_analytic_account = fields.Char(string='Analytic Account (Grouped)')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')

    pnl_id = fields.Char(string='ID')
    balance_sheet_root = fields.Char(string='ID & Category')

    quarter = fields.Char(string='Quarterly')

    # @api.model
    # def get_balance_sheet_data(self):
    #     # Connect to the PostgreSQL database
    #     conn = psycopg2.connect(database="COMM_FIN_IMP", user="admin", password="09105252140",
    #                             host="localhost", port="5432")
    #
    #     # Query to retrieve the data from the database table
    #     query = """
    #     SELECT id, root, sub_category, account_id, main_category, date, monthly, yearly, debit, credit, balance, grouped_analytic_account, analytic_account_id, pnl_id, balance_sheet_root, quarter
    #     FROM balance_sheet
    #     """
    #
    #     # Use Pandas to read the data from the database
    #     df = pd.read_sql_query(query, conn)
    #
    #     # Close the database connection
    #     conn.close()
    #
    #     return df

    #     def init(self):
    #         tools.drop_view_if_exists(self._cr, 'balance_sheet')
    #         self._cr.execute("""
    #             CREATE OR REPLACE VIEW balance_sheet AS (
    # SELECT ROW_NUMBER() OVER() AS id,
    #                 CONCAT(AML.pnl_id, ' ', AML.root) AS balance_sheet_root,
    #                 AML.pnl_id AS pnl_id,
    #                 AML.root AS root,
    #                 AML.main_category AS main_category,
    #                 AML.sub_category AS sub_category,
    #                 AML.account_id AS account_id,
    #                 AML.analytic_account_id AS analytic_account_id,
    #                 AML.is_pnl_or_bs,
    #                 AML.debit as debit ,
    #                 AML.credit as credit,
    #                 AML.balance AS balance,
    #                 CASE
    #                     WHEN AAA.name LIKE '%8310%' THEN 'PLASIC - SOT'
    #                     WHEN AAA.name LIKE '%8300%' THEN 'PLASIC - TOs'
    #                     WHEN AAA.name LIKE '%8110%' THEN 'ASPM MODULES'
    #                     WHEN AAA.name LIKE '%8100%' THEN 'HERMETICS'
    #                     WHEN AAA.name LIKE '%8120%' THEN 'DIE SALES'
    #                     ELSE 'SUPPORT'
    #                 END AS grouped_analytic_account,
    #                 AML.date AS date,
    #                 AML.monthly AS monthly,
    #                 AML.yearly AS yearly,
    #                 CASE
    #                     WHEN EXTRACT(MONTH FROM TO_DATE(AML.date, 'YYYY-MM-DD')) IN (1, 2, 3) THEN 'Q1'
    #                     WHEN EXTRACT(MONTH FROM TO_DATE(AML.date, 'YYYY-MM-DD')) IN (4, 5, 6) THEN 'Q2'
    #                     WHEN EXTRACT(MONTH FROM TO_DATE(AML.date, 'YYYY-MM-DD')) IN (7, 8, 9) THEN 'Q3'
    #                     ELSE 'Q4'
    #                 END AS quarter
    #             FROM (
    #                 SELECT
    #                     conn.pnl_id,
    #                     conn.is_pnl_or_bs,
    #                     conn.name AS root,
    #                     conn.connection_categ AS main_category,
    #                     conn.sub_category AS sub_category,
    #                     aml.account_id AS account_id,
    #                     aml.analytic_account_id AS analytic_account_id,
    #                     aml.debit as debit,
    #                     aml.credit as credit,
    #                     ABS(SUM(aml.debit) - SUM(aml.credit)) AS balance,
    #                     TO_CHAR(aml.date, 'YYYY-MM-DD') AS date,
    #                     TO_CHAR(aml.date, 'MM-YYYY') AS monthly,
    #                     TO_CHAR(aml.date, 'YYYY') AS yearly
    #                 FROM (
    #                     SELECT
    #                         x.pnl_id,
    #                         x.is_pnl_or_bs,
    #                         x.name,
    #                         x.connection_categ AS connection_categ,
    #                         x.sub_category AS sub_category,
    #                         y.account_id AS account_id
    #                     FROM
    #                         public.profit_and_loss x,
    #                         public.profit_and_loss_line y
    #                     WHERE x.id = y.pnl_connection
    #                 ) AS conn
    #                 INNER JOIN public.account_move_line AS aml ON aml.account_id = conn.account_id
    #                 GROUP BY
    #                     conn.pnl_id,
    #                     conn.is_pnl_or_bs,
    #                     conn.connection_categ,
    #                     conn.name,
    #                     conn.sub_category,
    #                     aml.account_id,
    #                     aml.analytic_account_id,
    #                     aml.date,
    #                     aml.name,
    #                    aml.debit,
    #                 aml.credit,
    #                 aml.balance
    #             ) AS AML
    #             LEFT JOIN public.account_analytic_account AS AAA ON AML.analytic_account_id = AAA.id
    #             WHERE AML.is_pnl_or_bs = 'bs'
    #             GROUP BY
    #                 balance_sheet_root,
    #                 AML.pnl_id,
    #                 AML.root,
    #                 AML.main_category,
    #                 AML.sub_category,
    #                 AML.account_id,
    #                 AML.analytic_account_id,
    #                 AML.debit,
    #                 AML.credit,
    #                 AML.balance,
    #                 AML.is_pnl_or_bs,
    #                 AML.date,
    #                 AML.monthly,
    #                 AML.yearly,
    #                 grouped_analytic_account,
    #                 quarter
    #             )
    #         """)

    @api.model
    def _default_user(self):
        return self.env.context.get('user_id', self.env.user.id)

    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Currency", readonly=True, store=True)
