# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Odoo Chung Cu',
    'version': '1.1',
    'author': 'Pham Dang Hao<danghao.cntt@gmail.com>',
    'category': 'Chung Cu Management',
    'description': """
Chung Cu Management.
====================

Odoo Chung Cu:
--------------------------------------------
    * Menu quản lý chung cư
    * Tạo invoice, sale order khi tạo hợp đồng hoặc thanh toán tiền hàng tháng
    * Quản lý dịch vụ của từng phòng
    """,
    'website': 'https://www.facebook.com/pham.terry',
    'depends': ['sale', 'product', 'account'],
    'data': [
        'data/product.xml',
        'data/product_categ.xml',
        'views/menu.xml',
        'views/khach_hang.xml',
        'views/ql_hop_dong.xml',
        'views/seq_hop_dong.xml',
        'views/paid_contract.xml',
    ],

    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
