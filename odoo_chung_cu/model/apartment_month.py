# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import except_orm, Warning, RedirectWarning
import time, datetime





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
