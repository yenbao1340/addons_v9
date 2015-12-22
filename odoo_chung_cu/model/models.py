# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import except_orm, Warning, RedirectWarning
import time, datetime


class ql_chung_cu_toa_nha(models.Model):
    _name = "apartment.building"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name = fields.Char("Tên")


class ql_chung_cu_phong(models.Model):
    _name = "apartment.room"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name = fields.Char("Tên tòa nhà")
    building_id = fields.Many2one('apartment.building', 'Tòa nhà')


class ql_chung_cu_month(models.Model):
    _name = "apartment.month"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name = fields.Char('Tháng', requieqred=True)
    year = fields.Selection([
        ('2015', '2015'),
        ('2016', '2016'),
        ('2017', '2017'),
        ('2018', '2018'),
        ('2019', '2019'),
        ('2020', '2020')], 'Năm', requieqred=True)
    date_start = fields.Date('Ngày bắt đầu')
    date_end = fields.Date('Ngày kết thúc')
    _defaults = {
        'year': datetime.date.today().strftime('%Y')
    }


class ql_chung_cu_dien_nuoc(models.Model):
    _name = "apartment.month.index"
    _order = 'id desc'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name = fields.Char(compute='_get_name')
    room_id = fields.Many2one('product.product', "Phòng", required=True, states={'draft': [('readonly', False)]})
    date = fields.Date('Ngày ghi chỉ số',readonly = True, required=True, states={'draft': [('readonly', False)]})
    old_water = fields.Float('Chỉ số nước cũ', states={'draft': [('readonly', False)]})
    old_power = fields.Float('Chỉ số điện cũ', states={'draft': [('readonly', False)]})
    water_number = fields.Float("Chỉ số nước mới", required=True, states={'draft': [('readonly', False)]})
    power_number = fields.Float("Chỉ số điện mới", required=True, states={'draft': [('readonly', False)]})
    # month = fields.Many2one("apartment.month", "Tháng", required=True, states={'confirm': [('readonly', True)]})
    power_price = fields.Float("Giá điện", states={'draft': [('readonly', False)]})
    water_price = fields.Float("Giá nước", states={'draft': [('readonly', False)]})
    is_paid = fields.Boolean('Đã thanh toán')
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirm', 'Xác nhận'),
        ('paid', 'Đã thanh toán'),
        ('not_paid', 'Không thanh toán'),
        ('cancel', 'Đã hủy')], 'Trạng thái')
    _defaults = {
        'is_paid': False,
    }

    @api.one
    def not_paid(self):
        self.write({
            'state': 'not_paid'
        })

    @api.model
    def create(self, vals):
        cxt = self.env.context
        action = self.env['ir.actions.act_window'].browse(cxt['params']['action'])
        next_month = self.env['apartment.month.index'].search([('room_id', '=', vals['room_id']),
                                                                  ('state', 'not in', ('draft', 'not_paid', 'cancel')),
                                                                  ('date', '>', vals['date'])],
                                                                 order='date asc', limit=1)
        print next_month
        if action.res_model == 'apartment.month.index':
            if (vals['old_water'] > vals['water_number'] or vals['old_power'] > vals['power_number']):
                raise except_orm('Lỗi!', 'Chỉ số mới không thể nhỏ hơn chỉ số cũ')
            elif next_month:
                if (next_month.water_number < vals['water_number'] or next_month.water_number < vals['power_number']):
                    raise except_orm('Lỗi!', 'Chỉ số sau không thể lớn hơn chỉ số trước' )
            return super(ql_chung_cu_dien_nuoc, self).create(vals)
        else:
            return super(ql_chung_cu_dien_nuoc, self).create(vals)

    @api.model
    def default_get(self, fields_list):
        defaults = {
        }
        cxt = self.env.context
        action = self.env['ir.actions.act_window'].browse(cxt['params']['action'])
        price = self.env['apartment.price'].search([('id', '!=', 0)], order='id desc', limit=1)
        if action.res_model == 'apartment.month.index':
            defaults['power_price'] = price.power_price
            defaults['date'] = time.strftime('%Y-%m-%d')
            defaults['water_price'] = price.water_price
            defaults['state'] = 'draft'
        return defaults

    def _get_name(self):
        for record in self:
            record.name = self.room_id.name + ' - ' + self.date

    @api.one
    def action_confirm(self):
        pre_month = self.env['apartment.month.index'].search([('room_id', '=', self.room_id.id),
                                                                  ('state', 'not in', ('draft', 'not_paid', 'cancel')),
                                                                  ('date', '<=', self.date)],
                                                                 order='date desc', limit=1)
        next_month = self.env['apartment.month.index'].search([('room_id', '=', self.room_id.id),
                                                                  ('state', 'not in', ('draft', 'not_paid', 'cancel')),
                                                                  ('date', '>', self.date)],
                                                                 order='date asc', limit=1)
        if pre_month:
            if next_month:
                if pre_month.state=='paid' and next_month.state == 'paid':
                     raise except_orm('Lỗi!', 'Không thể xác nhận phiếu điện nước ở giữa 2 phiếu đã thanh toán' )
        self.state = 'confirm'

    @api.one
    def action_cancel(self):
        self.state = 'cancel'

    @api.onchange('room_id')
    def onchange_service(self):
        if self.room_id:
            pre_month = self.env['apartment.month.index'].search([('room_id', '=', self.room_id.id),
                                                                  ('state', 'not in', ('draft', 'cancel')),
                                                                  ('date', '<=', self.date)],
                                                                 order='date desc', limit=1)
            if pre_month:
                self.old_water = pre_month.water_number
                self.old_power = pre_month.power_number
            else:
                self.old_water = 0.0
                self.old_power = 0.0

class ApartmentPrice(models.Model):
    _name = 'apartment.price'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    water_price = fields.Float('Giá nước/m3')
    power_price = fields.Float('Giá điện/Kwh')


class apartment_service_conf(models.Model):
    _name = 'apartment.service.conf'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name = fields.Char('Tên dịch vụ')

class apartment_service(models.Model):
    _name = 'apartment.service'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    """
        Module cho phép người dùng nhập dịch vụ sử dụng cho tòa nhà
    """
    name = fields.Char(compute='_get_name')
    room_id = fields.Many2one('apartment.room', "Phòng", required=True)
    date = fields.Date('Ngày ghi dịch vụ', required=True)
    service_type = fields.Many2one('product.product', 'Dịch vụ', required=True)
    price = fields.Float('Tổng tiền')
    description = fields.Text('Ghi chú')
    is_paid = fields.Boolean('Đã thanh toán')
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirm', 'Xác nhận'),
        ('paid', 'Đã thanh toán'),
        ('cancel', 'Đã hủy')], 'Trạng thái')
    _defaults = {
        'state': 'draft',
        'date': time.strftime('%Y-%m-%d'),
        'is_paid': False
    }

    @api.multi
    def _get_name(self):
        for record in self:
            record.name = self.room_id.name + ' - ' + self.service_type.name

    @api.one
    def action_confirm(self):
        self.state = 'confirm'

    @api.one
    def action_cancel(self):
        self.state = 'cancel'


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    contract_id = fields.Many2one('apartment.contract')

