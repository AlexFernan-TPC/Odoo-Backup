# pylint: disable=manifest-required-author
{

    'name': "Accrual Transactions",

    'summary': """
        Accrual Transaction Records
        ===========
        capture required accounting transaction once products are received
            """,

    'author': "Agile Software Solutions and Technologies OPC",
    'website': "https://agiletech.ph",

    # any module necessary for this one to work correctly
    'depends': ['account', 'purchase', 'stock', 'purchase_stock', 'om_account_accountant', 'om_account_asset', 'om_account_budget',
                'team_accounting', 'accounting_pdf_reports', 'mrp', 'sale', 'purchase_requisition'],



    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/purchase_data.xml',
        'views/product_category_view.xml',
        'views/res_partner_view.xml',
        'views/buyoff_result_view.xml',
        'views/purchase_order_views.xml',
        'views/purchase_requisition_view.xml',
        'views/account_asset_category_views.xml',
        'views/product_template_views.xml',
        'views/package_type_views.xml',
        'views/sale_order_views.xml',

    ],
    'license': 'LGPL-3',
}
