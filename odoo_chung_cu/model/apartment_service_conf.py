# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import except_orm, Warning, RedirectWarning
import time, datetime




class apartment_service_conf(models.Model):
    _name = 'apartment.service.conf'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name = fields.Char('Tên dịch vụ')