# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import except_orm, Warning, RedirectWarning
import time





class PaidContractServiceLine(models.TransientModel):
    _name = 'paid.contract.line.service'

    room_id = fields.Many2one('product.product', "Phòng", required=True)
    contract_id = fields.Many2one('paid.contract', invisible= "1")
    service_id = fields.Many2one('apartment.service', invisible= "1")
    date = fields.Date('Ngày ghi dịch vụ', required=True)
    service_type = fields.Many2one('apartment.service.conf', 'Loại dịch vụ', required=True)
    price = fields.Float('Tổng tiền')
    description = fields.Char('Ghi chú')

