# John Raymark LLavanes
# MIS - 2k23
{
    'name': 'Team Pacific Corporation Accounting Module (PROFIT AND LOSS & BALANCE SHEET)',
    'version': '0.1',
    'category': 'Accounting Extensions',
    'summary': 'Accounting Customization For Odoo 13',
    'sequence': '10',
    'author': 'John Raymark LLavanes - 10450',
    'company': 'Team Pacific Corporation',
    'maintainer': 'MIS - LOC 267',
    'support': 'mis@teamglac.com',
    'website': '',
    'depends': ['account'],
    'live_test_url': '',
    'demo': [],
    'data': [
        # Security
        'security/ir.model.access.csv',
        'security/xml/pnl_security.xml',

        # Views
        'views/team_accounting_profit_and_loss_view_menu.xml',
        'views/team_accounting_profit_and_loss_view.xml',
        'views/analytic_account_view.xml',
        'views/templates.xml',
        'views/query_profit_and_loss_view.xml',
        'views/query_balance_sheet_view.xml',
        'views/profit_and_loss_view_view.xml',
        'views/category_and_sub_categ_view.xml',
        'views/profit_and_loss_config_view.xml',
        'views/blank_page_template.xml',


        # Reports
        'reports/profit_and_loss_report_and_bs.xml',
        'reports/financial_report_template.xml',
        'reports/general_ledger.xml',
        'reports/report_views.xml',

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [
        'static/src/xml/script_view.xml',
        'static/src/xml/financial_reports_view.xml',
        'static/src/xml/general_ledger_view.xml'
    ],

}
