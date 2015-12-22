# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import except_orm, Warning, RedirectWarning
import time, datetime


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    contract_id = fields.Many2one('apartment.contract')

