# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import except_orm, Warning, RedirectWarning
import time


class PaidContract(models.TransientModel):
    _name = 'paid.contract'

    name = fields.Char('Tên')
    room_id = fields.Many2one('product.product', 'Tên phòng', readonly=True)
    supplier_id = fields.Many2one('res.partner', 'Khách hàng', readonly=True)
    month = fields.Many2one("apartment.month", "Tháng", required=True)
    month_id = fields.One2many('apartment.month.index', 'id', string="Điện nước", store=True, readonly=True)
    serivce_id = fields.One2many('apartment.service', 'id', string="Dịch vụ", readonly=True)
    power_amount = fields.Float('Tiền điện', readonly=True)
    water_amount = fields.Float('Tiền nước', readonly=True)
    service_amount = fields.Float('Tiền dịch vụ', readonly=True)
    room_price = fields.Float('Tiền thuê nhà', readonly=True)
    amount_total = fields.Float(string='Tổng tiền', readonly=True)
    contract_id = fields.Many2one('apartment.contract')
    month_line = fields.One2many('paid.contract.line.month', 'contract_id')
    service_line = fields.One2many('paid.contract.line.service', 'contract_id')
    is_load = fields.Boolean()
    is_sale = fields.Boolean()

    @api.one
    def create_so(self):
        sale_id = self.env['sale.order'].create({
            'partner_id': self.contract_id.supplier_id.id,
            'contract_id': self.contract_id.id,
            'note': u"Thanh toán tiền thuê nhà hợp đồng %s"%self.contract_id.name +time.strftime("%Y-%m-%d"),
            'name': self.contract_id.name + '/' +time.strftime("%Y-%m-%d")
        })
        power_number = water_number= 0.0
        for order in self:
            for line in order.month_line:
                power_number += line.power_number - line.old_power
                water_number += line.water_number - line.old_water
                line.month_index_ids.write({
                    'is_paid': True,
                    'state': 'paid'
                })
            for line in order.service_line:
                line.service_id.write({
                    'is_paid': True,
                    'state': 'paid'
                })
        price_room = self.env.ref('odoo_chung_cu.price_room')
        price_power = self.env.ref('odoo_chung_cu.price_power')
        price_water = self.env.ref('odoo_chung_cu.price_water')
        price_service = self.env.ref('odoo_chung_cu.price_service')
        if self.room_price > 0:
            sale_id.order_line.create({
                'product_id': price_room.id,
                'product_uom_qty': 1,
                'order_id': sale_id.id,
                'name': price_room.name,
                'price_unit': self.room_price
            })
        if self.power_amount > 0:
            sale_id.order_line.create({
                'product_id': price_power.id,
                'product_uom_qty': power_number,
                'order_id': sale_id.id,
                'name': price_power.name,
                'price_unit': self.power_amount/power_number
            })
        if self.water_amount > 0:
            sale_id.order_line.create({
                'product_id': price_water.id,
                'product_uom_qty': water_number,
                'order_id': sale_id.id,
                'name': price_water.name,
                'price_unit': self.water_amount/water_number
            })
        if self.service_amount > 0:
            sale_id.order_line.create({
                'product_id': price_service.id,
                'product_uom_qty': 1,
                'order_id': sale_id.id,
                'name': price_service.name,
                'price_unit': self.service_amount
            })
        self.is_sale = True

    @api.model
    def default_get(self, fields_list):
        defaults = {
        }
        cxt = self.env.context
        if cxt.get('active_model') == 'apartment.contract':
            contract = self.env['apartment.contract'].browse([cxt.get('active_id'),])
            defaults['room_id'] = contract.room_product_id.room_product.id
            defaults['contract_id'] = contract.id
            defaults['supplier_id'] = contract.supplier_id.id
            defaults['is_load'] = False
        return defaults

    @api.one
    def load_info(self):
        contract_id = self.contract_id
        if contract_id.date_end != False:
            service_contract = self.env['apartment.service'].search([('room_id', '=', self.room_product_id.room_product.id),
                                                                     ('date', '<=', contract_id.date_end),
                                                                     ('date', '>=', contract_id.date_start),
                                                                     ('is_paid', '=', False),
                                                                     ('state', '=', 'confirm')],
                                                                    order='date desc')
            pw = self.env['apartment.month.index'].search([('room_id', '=', self.room_product_id.room_product.id),
                                                           ('state', 'not in', ('draft', 'not_paid', 'cancel')),
                                                           ('date', '<=', contract_id.date_end),
                                                           ('date', '>=', contract_id.date_start),
                                                           ('is_paid', '=', False)],
                                                          order='date desc')
        else:
            service_contract = self.env['apartment.service'].search([('room_id', '=', self.room_product_id.room_product.id),
                                                                     ('is_paid', '=', False),
                                                                     ('date', '>=', contract_id.date_start),
                                                                     ('state', '=', 'confirm')],
                                                                    order='date desc')
            pw = self.env['apartment.month.index'].search([('room_id', '=', self.room_product_id.room_product.id),
                                                           ('state', 'not in', ('draft', 'not_paid', 'cancel')),
                                                           ('date', '>=', contract_id.date_start),
                                                           ('is_paid', '=', False)],
                                                          order='date desc')
        for item in pw:
            self.env['paid.contract.line.month'].create({
                'contract_id': self.id,
                'month_index_ids': item.id,
                'room_id': item.room_id.id,
                'date': item.date,
                'old_water': item.old_water,
                'old_power': item.old_power,
                'water_number': item.water_number,
                'power_number': item.power_number,
                'power_price': item.power_price,
                'water_price': item.water_price,

            })
        for item in service_contract:
            self.env['paid.contract.line.service'].create({
                'room_id': item.room_id.id,
                'contract_id': self.id,
                'service_id': item.id,
                'date': item.date,
                'service_type': item.service_type.id,
                'price': item.price,
                'description': item.description
            })
        self.room_price = contract_id.price
        self.write({'is_load': True})
        self.button_dummy()

    @api.multi
    def button_dummy(self):
        for order in self:
            water = val1 = service = power_number = water_number = 0.0
            for line in order.month_line:
                val1 += (line.power_number - line.old_power)*line.power_price
                water += (line.water_number - line.old_water)*line.water_price
            self.power_amount = val1
            self.water_amount = water
            for line in order.service_line:
                service += line.price
            self.service_amount = service
            self.amount_total = self.power_amount + self.water_amount+self.room_price + self.service_amount


class PaidContractOrderLine(models.TransientModel):
    _name = 'paid.contract.line.month'

    contract_id = fields.Many2one('paid.contract', invisible="1")
    month_index_ids = fields.Many2one('apartment.month.index', invisible="1")
    room_id = fields.Many2one('product.product', "Phòng", required=True)
    date = fields.Date('Ngày ghi chỉ số', required=True)
    old_water = fields.Float('Chỉ số nước cũ')
    old_power = fields.Float('Chỉ số điện cũ')
    water_number = fields.Float("Chỉ số nước mới", required=True)
    power_number = fields.Float("Chỉ số điện mới", required=True)
    power_price = fields.Float("Giá điện")
    water_price = fields.Float("Giá nước")

    @api.model
    def default_get(self, fields_list):
        defaults = {
        }
        price = self.env['apartment.price'].search([('id', '!=', 0)], order='id desc', limit=1)
        defaults['power_price'] = price.power_price
        defaults['date'] = time.strftime('%Y-%m-%d')
        defaults['water_price'] = price.water_price
        return defaults

    @api.onchange('room_id')
    def onchange_service(self):
        if self.room_id:
            pre_month = self.env['apartment.month.index'].search([('room_id', '=', self.room_product_id.room_product.id),
                                                                  ('state', 'not in', ('draft', 'not_paid', 'cancel')),
                                                                  ('date', '<=', self.date)],
                                                                 order='date desc', limit=1)
            if pre_month:
                self.old_water = pre_month.water_number
                self.old_power = pre_month.power_number
            else:
                self.old_water = 0.0
                self.old_power = 0.0

    @api.model
    def create(self, vals):
        cxt = self.env.context
        rs = super(PaidContractOrderLine, self).create(vals)
        if rs.month_index_ids:
            return None
        else:
            month_id = self.env['apartment.month.index'].create({
                'room_id': vals['room_id'],
                'date': vals['date'],
                'old_water': vals['old_water'],
                'old_power': vals['old_power'],
                'power_price': vals['power_price'],
                'water_price': vals['water_price'],
                'water_number': vals['water_number'],
                'power_number': vals['power_number'],

            })
            rs.month_index_ids = month_id.id
            month_id.action_confirm()
        return rs

class PaidContractServiceLine(models.TransientModel):
    _name = 'paid.contract.line.service'

    room_id = fields.Many2one('product.product', "Phòng", required=True)
    contract_id = fields.Many2one('paid.contract', invisible= "1")
    service_id = fields.Many2one('apartment.service', invisible= "1")
    date = fields.Date('Ngày ghi dịch vụ', required=True)
    service_type = fields.Many2one('apartment.service.conf', 'Loại dịch vụ', required=True)
    price = fields.Float('Tổng tiền')
    description = fields.Char('Ghi chú')

