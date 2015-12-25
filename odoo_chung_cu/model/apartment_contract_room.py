# -*- coding: utf-8 -*-
from openerp import models, fields, api





class ContractRoomLine(models.Model):
    """
    Module này lưu thông tin phòng của contract
    """
    _name = "apartment.contract.room"

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