# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import except_orm, Warning, RedirectWarning
import time, datetime





class ql_chung_cu_phong(models.Model):
    _name = "apartment.room"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name = fields.Char("Tên phòng")
    building_id = fields.Many2one('apartment.building', 'Tòa nhà')