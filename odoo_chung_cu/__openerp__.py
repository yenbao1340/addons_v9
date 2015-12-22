# -*- coding: utf-8 -*-
{
    'name': 'Quản lý chung cư',
    'version': '0.1',
    'author': 'Terry',
    'category': 'Quản lý chung cư',
    'website': 'https://www.facebook.com/pham.terry',
    'summary': 'Chung cư',
    'description': """
""",
    'depends': [
        'base',
        'mail',
        'sale',
        'product'
    ],
    'data': [
        'view/menu.xml',
        'view/views.xml',
        'view/wizard_view.xml',
        'view/wizard_line_view.xml',
        'view/contract.xml',
        'view/tenant_view.xml',
        'data/product_category.xml',
        # 'data/month_data.xml',
        'data/cities.xml',
        'data/product.xml',
        #'data/cron_job.xml',
    ],
    'installable': True,
    'application': True,
}
