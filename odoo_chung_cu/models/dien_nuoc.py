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
from openerp import models, fields, api
import time
from openerp.exceptions import except_orm, Warning, RedirectWarning

class QuanLyChungCuDien(models.Model):
    _name = 'quan.ly.chung.cu.dien'
    _description = "Module quản lý chỉ số điện các phòng"

    name = fields.Char(string='Name')
    product_power = fields.Many2one('product.product', string='Phòng')
    old_power = fields.Float(string='Chỉ số điện cũ')
    new_power = fields.Float(string='Chỉ số điện mới')
    date = fields.Date(string='Ngày ghi chỉ số')
    contract_id = fields.Many2one('quan.ly.chung.cu.hop.dong', string='Hợp đồng')
    power_price = fields.Float(related='product_power.list_price', string='Đơn giá')
    paid_contract_id = fields.Many2one('paid.contract')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('paid', 'Paid')
    ])

    @api.model
    def default_get(self, fields_list):
        defaults = {
            'product_power': self.env.ref('odoo_chung_cu.price_power').id,
            'date': time.strftime("%Y-%m-%d"),
        }
        cxt = self.env.context
        model = cxt.get('paid_contract', '')
        if model == 'paid_contract':
            old_power = self.search([('product_power', '=', self.env.ref('odoo_chung_cu.price_power').id), ('contract_id', '=', cxt['contract_id']), ('state', '=', 'paid')],  limit=1, order='date desc')
            defaults['contract_id'] = cxt['contract_id']
            if old_power:
                defaults['old_power'] = old_power.new_power
            else:
                defaults['old_power'] = 0
            raise Warning(defaults)
        return defaults

    @api.one
    def check_old_power(self, new_power, contract_id):
        old_power = self.search([('product_power', '=', self.env.ref('odoo_chung_cu.price_power').id),('contract_id', '=', contract_id), ('state', '=', 'paid')],  limit=1, order='date desc')
        if old_power:
            if old_power.new_power <= new_power:
                value = {
                    'contract_id': contract_id.id,
                    'product_power': contract_id.product_room,
                    'old_power': old_power.new_power,
                    'new_power': new_power,
                    'date': time.strftime("%Y-%m-%d")
                }
                self.create(value)
            else:
                raise except_orm('Không thể xác nhận hợp đồng!', 'Chỉ số điện mới không thể nhỏ hơn chỉ số đơn cũ')
        else:
            value = {
                'contract_id': contract_id.id,
                'product_power': contract_id.product_room,
                'new_power': new_power,
                'date':time.strftime("%Y-%m-%d")
            }
            self.create(value)

    @api.model
    def create_power(self, new_power, contract_id):
        """
        Tạo bản ghi điện cho hợp đồng
        :param new_power:
        :return:
        """
        try:
            if new_power:
                self.check_old_power(new_power, contract_id)
            else:
                raise except_orm('Không thể xác nhận hợp đồng!', 'Chỉ số điện mới không thể nhỏ hơn chỉ số đơn cũ')
        except except_orm as e:
            ecls, emsg = e.args

    @api.model
    def create(self, vals):
        try:
            create = super(QuanLyChungCuDien, self).create(vals)
            cxt = self.env.context
            if cxt['active_model'] == 'quan.ly.chung.cu.hop.dong':
                contract_id = self.env['quan.ly.chung.cu.hop.dong'].browse(cxt['active_id'])
                old_power = self.search([
                    ('contract_id', '=', contract_id.id),
                    ('state', '=', 'paid')
                ])
                if old_power:
                    if old_power.new_power < vals['new_power']:
                        raise except_orm('Lỗi, Chỉ số điện mới không thể nhỏ hơn chỉ số điện cũ')
                    else:
                        vals['old_power'] = old_power.new_power
                        return create
                else:
                    return create
            else:
                return create
        except except_orm as e:
            return e


class QuanLyChungCuNuoc(models.Model):
    _name = 'quan.ly.chung.cu.nuoc'

    name = fields.Char(string='Name')
    product_water = fields.Many2one('product.product', string='Phòng')
    old_water = fields.Float(string='Chỉ số nước cũ')
    new_water = fields.Float(string='Chỉ số nước mới')
    date = fields.Date(string='Ngày ghi chỉ số')
    contract_id = fields.Many2one(string='Hợp đồng')
    water_price = fields.Float(related='product_water.list_price', string='Đơn giá')
    paid_contract_id = fields.Many2one('paid.contract')

    @api.model
    def default_get(self, fields_list):
        defaults = {
            'product_water': self.env.ref('odoo_chung_cu.price_water').id,
            'date': time.strftime("%Y-%m-%d"),
        }
        cxt = self.env.context
        model = cxt.get('paid_contract', '')
        if model == 'paid_contract':
            old_water = self.search([('product_water', '=', self.env.ref('odoo_chung_cu.price_water').id), ('contract_id', '=', cxt['contract_id'])],  limit=1, order='date desc')
            if old_water:
                defaults['old_power'] = old_water.new_power
            else:
                defaults['old_power'] = 0
        return defaults

    @api.one
    def check_old_water(self, new_water, contract_id):
        old_water = self.search([('product_water', '=', self.product_water.id)],  limit=1, order='date desc')
        if old_water:
            if old_water.new_power <= new_water:
                value = {
                    'contract_id': contract_id.id,
                    'product_power': contract_id.product_room,
                    'old_power': old_water.new_power,
                    'new_power': new_water,
                    'date': time.strftime("%Y-%m-%d")
                }
                self.create(value)
            else:
                raise except_orm('Không thể xác nhận hợp đồng!', 'Chỉ số nước mới không thể nhỏ hơn chỉ số đơn cũ')
        else:
            value={
                'contract_id': contract_id.id,
                'product_power': contract_id.product_room,
                'new_power': new_water,
                'date':time.strftime("%Y-%m-%d")
            }
            self.create(value)

    @api.model
    def create_power(self, new_power, contract_id):
        """
        Tạo bản ghi điện cho hợp đồng
        :param new_power:
        :return:
        """
        try:
            if new_power:
                self.check_old_power(new_power, contract_id)
            else:
                raise except_orm('Không thể xác nhận hợp đồng!', 'Chỉ số điện mới không thể nhỏ hơn chỉ số đơn cũ')
        except except_orm as e:
            raise e