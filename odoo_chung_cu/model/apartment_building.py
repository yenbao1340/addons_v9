# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import except_orm, Warning, RedirectWarning
import time, datetime


class ql_chung_cu_toa_nha(models.Model):
    _name = "apartment.building"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name = fields.Char("T�n")
