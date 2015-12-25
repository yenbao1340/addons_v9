# -*- coding: utf-8 -*-
from openerp import models, fields, api


class apartment_building(models.Model):
    _name = "apartment.building"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name = fields.Char("Tên")
