from odoo import fields, models, api, tools


class GetDataHere(models.Model):
    _name = 'get.data.here'
    _description = 'Profit and Loss'
    _auto = False
    _order = 'root asc'

    root = fields.Char()
    sub_category = fields.Many2one('sub.categ', string='Sub Category')
    account_id = fields.Many2one('account.account', string='Chart of Accounts')
    main_category = fields.Many2one('category', string='Category')
    date = fields.Char(string='Date')
    monthly = fields.Char(string='Monthly')
    yearly = fields.Char(string='Yearly')
    balance = fields.Monetary(string='Balance')
    grouped_analytic_account = fields.Char(string='Analytic Account (Grouped)')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    pnl_id = fields.Char(string='PNL ID')
    profit_and_loss_root = fields.Char(string='ID & Category')

    quarter = fields.Char(string='Quarterly')

    total_sales = fields.Monetary()
    gross_profit = fields.Monetary()
    total_raw_materials_used = fields.Monetary(string="Raw Materials Used")




    def init(self):
        tools.drop_view_if_exists(self._cr, 'get_data_here')
        self._cr.execute("""
            CREATE OR REPLACE VIEW get_data_here AS (
SELECT
    ROW_NUMBER() OVER() AS id,
    CONCAT(AML.pnl_id, ' ', AML.root) AS profit_and_loss_root,
    AML.pnl_id AS pnl_id,
    AML.root AS root,
    AML.main_category AS main_category,
    p.name AS main_category_name,
    AML.sub_category AS sub_category,
    AML.account_id AS account_id,
    acc.name AS account_name,
    AML.analytic_account_id AS analytic_account_id,
    AML.is_pnl_or_bs,
    AML.balance AS balance,
    CASE
        WHEN AAA.name LIKE '%8310%' THEN 'PLASIC - SOT'
        WHEN AAA.name LIKE '%8300%' THEN 'PLASIC - TOs'
        WHEN AAA.name LIKE '%8110%' THEN 'ASPM MODULES'
        WHEN AAA.name LIKE '%8100%' THEN 'HERMETICS'
        WHEN AAA.name LIKE '%8120%' THEN 'DIE SALES'
        ELSE 'SUPPORT'
    END AS grouped_analytic_account,
    AML.date AS date,
    AML.monthly AS monthly,
    AML.yearly AS yearly,
    CASE
        WHEN EXTRACT(MONTH FROM TO_DATE(AML.date, 'YYYY-MM-DD')) IN (1, 2, 3) THEN 'Q1'
        WHEN EXTRACT(MONTH FROM TO_DATE(AML.date, 'YYYY-MM-DD')) IN (4, 5, 6) THEN 'Q2'
        WHEN EXTRACT(MONTH FROM TO_DATE(AML.date, 'YYYY-MM-DD')) IN (7, 8, 9) THEN 'Q3'
        ELSE 'Q4'
    END AS quarter,
    SUM(CASE WHEN AML.root = 'SALES' THEN AML.balance ELSE 0 END) OVER() AS total_sales,
    SUM(CASE WHEN AML.root = 'RAW MATERIALS USED' THEN AML.balance ELSE 0 END) OVER() AS total_raw_materials_used,
    (SUM(CASE WHEN AML.root = 'DIRECT LABOR - BASIC' THEN AML.balance ELSE 0 END) OVER() + SUM(CASE WHEN AML.root = 'DL INDIRECT COST' THEN AML.balance ELSE 0 END) OVER()) AS total_direct_labor_cost,
    SUM(CASE WHEN AML.root = 'DIRECT LABOR - BASIC' THEN AML.balance ELSE 0 END) OVER() AS total_direct_labor_basic,
    SUM(CASE WHEN AML.root = 'DL INDIRECT COST' THEN AML.balance ELSE 0 END) OVER() AS total_dl_indirect_cost,
    SUM(CASE WHEN AML.root = 'MANUFACTURING OVERHEAD' THEN AML.balance ELSE 0 END) OVER() AS total_manufacturing_overhead,
    SUM(CASE WHEN AML.root IN ('RAW MATERIALS USED', 'DIRECT LABOR - BASIC', 'DL INDIRECT COST', 'MANUFACTURING OVERHEAD') THEN AML.balance ELSE 0 END) OVER() AS total_cost_of_goods_sold,
    SUM(CASE WHEN AML.root = 'SELLING, GENERAL AND ADMINISTRATIVE EXPENSES' THEN AML.balance ELSE 0 END) OVER() AS total_income_loss_from_operations,
    SUM(CASE WHEN AML.root = 'OTHER (INCOME) AND EXPENSES' THEN AML.balance ELSE 0 END) OVER() AS total_other_income_and_expenses,
    (SUM(CASE WHEN AML.root = 'SALES' THEN AML.balance ELSE 0 END) OVER() - SUM(CASE WHEN AML.root IN ('RAW MATERIALS USED', 'DIRECT LABOR - BASIC', 'DL INDIRECT COST', 'MANUFACTURING OVERHEAD') THEN AML.balance ELSE 0 END) OVER()) AS gross_profit,
    (SUM(CASE WHEN AML.root = 'SELLING, GENERAL AND ADMINISTRATIVE EXPENSES' THEN AML.balance ELSE 0 END) OVER() - SUM(CASE WHEN AML.root = 'OTHER (INCOME) AND EXPENSES' THEN AML.balance ELSE 0 END) OVER()) AS total_income_loss_before_income_tax,
    SUM(CASE WHEN acc.name = 'Income Tax' THEN AML.balance ELSE 0 END) OVER() AS total_income_tax,
    (SUM(CASE WHEN AML.root = 'SELLING, GENERAL AND ADMINISTRATIVE EXPENSES' THEN AML.balance ELSE 0 END) OVER() - SUM(CASE WHEN AML.root = 'OTHER (INCOME) AND EXPENSES' THEN AML.balance ELSE 0 END) OVER() - SUM(CASE WHEN acc.name = 'Income Tax' THEN AML.balance ELSE 0 END) OVER()) AS total_net_loss_income,
    (SUM(CASE WHEN AML.root = 'SELLING, GENERAL AND ADMINISTRATIVE EXPENSES' THEN AML.balance ELSE 0 END) OVER() - SUM(CASE WHEN AML.root = 'OTHER (INCOME) AND EXPENSES' THEN AML.balance ELSE 0 END) OVER() - SUM(CASE WHEN acc.name = 'Interest expense' THEN AML.balance ELSE 0 END) OVER()) AS total_depreciation_and_amortization
FROM
    (
        SELECT
            conn.pnl_id,
            conn.is_pnl_or_bs,
            conn.name AS root,
            conn.connection_categ AS main_category,
            conn.sub_category AS sub_category,
            aml.account_id AS account_id,
            aml.analytic_account_id AS analytic_account_id,
            ABS(SUM(aml.debit) - SUM(aml.credit)) AS balance,
            TO_CHAR(aml.date, 'YYYY-MM-DD') AS date,
            TO_CHAR(aml.date, 'MM-YYYY') AS monthly,
            TO_CHAR(aml.date, 'YYYY') AS yearly
        FROM
            (
                SELECT
                    x.pnl_id,
                    x.is_pnl_or_bs,
                    x.name,
                    x.connection_categ AS connection_categ,
                    x.sub_category AS sub_category,
                    y.account_id AS account_id
                FROM
                    public.profit_and_loss x,
                    public.profit_and_loss_line y
                WHERE
                    x.id = y.pnl_connection
            ) AS conn
        INNER JOIN public.account_move_line AS aml ON aml.account_id = conn.account_id
        GROUP BY
            conn.pnl_id,
            conn.is_pnl_or_bs,
            conn.connection_categ,
            conn.name,
            conn.sub_category,
            aml.account_id,
            aml.analytic_account_id,
            aml.date,
            aml.name
    ) AS AML
LEFT JOIN public.account_analytic_account AS AAA ON AML.analytic_account_id = AAA.id
LEFT JOIN public.profit_and_loss AS p ON AML.main_category = p.connection_categ
LEFT JOIN public.account_account AS acc ON AML.account_id = acc.id
WHERE
    AML.is_pnl_or_bs = 'pnl'
GROUP BY
    profit_and_loss_root,
    AML.pnl_id,
    AML.root,
    AML.main_category,
    p.name,
    AML.sub_category,
    AML.account_id,
    acc.name,
    AML.analytic_account_id,
    AML.balance,
    AML.is_pnl_or_bs,
    AML.date,
    AML.monthly,
    AML.yearly,
    grouped_analytic_account,
    quarter

            )
        """)

    @api.model
    def _default_user(self):
        return self.env.context.get('user_id', self.env.user.id)

    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Currency", readonly=True, store=True, )
