# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import except_orm, Warning, RedirectWarning
import time





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
