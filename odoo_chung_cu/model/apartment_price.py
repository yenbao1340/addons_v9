# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import except_orm, Warning, RedirectWarning
import time, datetime




class ApartmentPrice(models.Model):
    _name = 'apartment.price'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    water_price = fields.Float('Giá nước/m3')
    power_price = fields.Float('Giá điện/Kwh')