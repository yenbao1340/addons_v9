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
from openerp.tools.translate import _
from openerp import models, fields, api
from openerp.exceptions import except_orm
import time


class QuanLyChungCuHopDong(models.Model):
    _inherit = 'mail.thread'
    _name = 'quan.ly.chung.cu.hop.dong'
    _order = 'id desc'

    @api.model
    def _check(self):
        return [('check_avalible', '=', False), ('customer', '=', True)]

    name = fields.Char(string='Số hợp đồng', compute='_get_name')
    partner_id = fields.Many2one('res.partner', string='Khách hàng', required=True, domain=_check)
    product_room = fields.One2many('quan.ly.chung.cu.phong', 'contract_id', string='Phòng cho thuê', required=True)
    product_base_service = fields.One2many('quan.ly.chung.cu.dich.vu', 'contract_id', string='Dịch vụ cơ bản')
    date_start = fields.Date(string='Ngày bắt đầu hợp đồng', required=True)
    date_end = fields.Date(string='Ngày kết thúc hợp đồng')
    down_payment = fields.Float(string='Tiền đặt cọc')
    sale_id = fields.One2many('sale.order', 'contract_id', readonly=True)
    power_start = fields.Float(string='Chỉ số điện ban đầu')
    water_start = fields.Float(string='Chỉ số nước ban đầu')
    tenant_ids = fields.One2many('quan.ly.chung.cu.tenant', 'contract_id', string='Tenant')
    state = fields.Selection([('draft', 'Nháp'), ('confirm', 'Xác nhận'), ('ended', 'Hết hạn hợp đồng'), ('cancel', 'Đã hủy')], string='Trạng thái')

    @api.model
    def default_get(self, fields_list):
        default = {}
        default['state'] = 'draft'
        default['date_start'] = time.strftime("%Y-%m-%d")
        return default

    @api.multi
    def pay_contract(self):
          return {
            'name': 'view_paid_contract',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'paid.contract',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }

    @api.one
    def _get_name(self):
        total_record = self.search([(1, '=', 1)])
        name = 'HD-0%d/%s' %(len(total_record)+1, time.strftime("%Y"))
        self.name = name

    @api.one
    def create_invoice(self):
        """
        Tạo hóa đơn nhận tiền đặt cọc khi confirm hợp đồng
        :return:
        """
        invoice = self.env['account.invoice']
        invoice_line = self.env['account.invoice.line']
        try:
            invoice = invoice.create({
                'partner_id': self.partner_id.id,
                'date_invoice': time.strftime('%Y-%m-%d'),
                'comment': u'Hóa đơn đặt cọc tiền thuê nhà %s' %self.product_room.room_product.name,
                'type': 'out_invoice',
                'account_id': 8,
            })
            invoice_line.create({
                'product_id': self.env.ref('odoo_chung_cu.invoice_room').id,
                'price_unit': self.down_payment,
                'invoice_id': invoice.id,
                'name': self.product_room.room_product.name
            })
        except except_orm as e:
                raise except_orm('Lỗi! Tạo hóa đơn đặt cọc tiền thuê nhà')
        return True

    @api.one
    def create_lead_tenant(self):
        tenant_model = self.env['quan.ly.chung.cu.tenant']
        tenant_data = {
            'partner_id': self.partner_id.id,
            'contract_id': self.id,
            'date_start': self.date_start,
            'is_lead': True,
        }
        tenant_model.create(tenant_data)

    @api.one
    def check_date_end(self):
        """

        :return:
        """

    @api.one
    def check_avalible(self):
        self.partner_id.check_avalible = True
        self.product_room.room_product.check_avalible = True

    @api.one
    def action_confirm(self):
        """
        Xử lý khi người dùng nhấn nút xác nhận hợp đồng
        :return:
        """
        if not self.product_room:
            raise except_orm(u'Lỗi', u'Không thể xác nhận 1 hợp đồng không có phòng cho thuê')
        if len(self.product_room) >1:
            raise except_orm(u'Lỗi', u'Không thể xác nhận hợp đồng có nhiều hơn 1 phòng cho thuê')
        else:
            try:
            # Tao invoice
                self.create_invoice()
                # Tao tenant chinh
                self.create_lead_tenant()
                # Đánh dấu partner, product đã có trong hợp đồng
                self.check_avalible()
                # Chuyển trạng thái sang confirm
                self.state = 'confirm'
            except except_orm as e:
                raise Warning(e)


class QuanLyChungCuPhong(models.Model):
    _name = 'quan.ly.chung.cu.phong'

    @api.model
    def _check(self):
        return [('categ_id', '=', self.env.ref('odoo_chung_cu.room_product').id), ('check_avalible', '=', False)]

    sequence = fields.Integer('Sequence', help="Gives the sequence order when displaying a list of contract lines.")
    contract_id = fields.Many2one('apartment.contract', string='Contract', invisible=1, ondelete='cascade')
    room_product = fields.Many2one('product.product', string='Phòng', domain=_check, required=True)
    room_price = fields.Float(string='Đơn giá')

    @api.onchange('room_product')
    def _get_price(self):
        if self.room_product:
            self.room_price = self.room_product.list_price


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    contract_id = fields.Many2one('quan.ly.chung.cu.hop.dong', readonly=1)


class QuanLyChungCuTenant(models.Model):
    _name = 'quan.ly.chung.cu.tenant'

    @api.model
    def _check(self):
        return [('check_avalible', '=', False), ('customer', '=', True)]
    partner_id = fields.Many2one('res.partner', string="Khách hàng", required=True, domain=_check)
    contract_id = fields.Many2one('apartment.contract', string='Hợp đồng')
    date_start = fields.Date(string='Ngày bắt đầu')
    date_end = fields.Date(string='Ngày kết thúc')
    gui_xe = fields.Boolean(string='Gửi xe tháng')
    type = fields.Char(string='Loại xe')
    color = fields.Char(string='Màu xe')
    number = fields.Char(string='Biển số xe')
    is_lead = fields.Boolean(string='Is Lead', invisible=1)

    def unlink(self, cr, uid, ids, context=None):
        species = self.browse(cr, uid, ids)
        if species.is_lead == True:
            raise except_orm('Lỗi!',
                             'Không thể xóa Tenant chính')
        rs = super(QuanLyChungCuTenant, self).unlink(cr, uid, ids, context)
        return rs

    @api.model
    def create(self, vals):
        rs = super(QuanLyChungCuTenant, self).create(vals)
        cxt = self.env.context
        if cxt['params'].has_key('id'):
            if cxt['params']['id']:
                rs.contract_id = cxt['params']['id']
        return rs


class QuanLyChungCuDichVu(models.Model):
    _name = 'quan.ly.chung.cu.dich.vu'

    @api.model
    def _check(self):
        return [('categ_id', '=', self.env.ref('odoo_chung_cu.base_product').id)]

    sequence = fields.Integer('Sequence', help="Gives the sequence order when displaying a list of contract lines.")
    contract_id = fields.Many2one('apartment.contract', string='Contract', invisible=1, ondelete='cascade')
    product_base_service = fields.Many2one('product.product', string='Dịch vụ cơ bản', domain=_check, required=True)
    product_base_service_price = fields.Float(string='Đơn giá')

    @api.onchange('room_product')
    def _get_price(self):
        if self.product_base_service:
            self.product_base_service_price = self.product_base_service.list_price


class QuanLyChungCuDichVuKhac(models.Model):
    _name = 'quan.ly.chung.cu.dich.vu.khac'

    @api.model
    def _check(self):
        return [('categ_id', '=', self.env.ref('odoo_chung_cu.other_product').id), ('check_avalible', '=', False)]

    sequence = fields.Integer('Sequence', help="Gives the sequence order when displaying a list of contract lines.")
    contract_id = fields.Many2one('apartment.contract', string='Contract', invisible=1, ondelete='cascade')
    product_other_service = fields.Many2one('product.product', string='Dịch vụ khác', domain=_check, required=True)
    product_other_service_price = fields.Float(string='Đơn giá')

    @api.onchange('room_product')
    def _get_price(self):
        if self.product_other_service:
            self.product_other_service_price = self.product_other_service.list_price


