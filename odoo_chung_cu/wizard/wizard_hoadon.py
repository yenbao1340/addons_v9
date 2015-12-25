# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import except_orm, Warning, RedirectWarning
import time

class wizard_hoadon(models.TransientModel):
    _name= 'wizardhoadon'
    invoice_date=fields.Date("Ngày ghi hóa đơn")