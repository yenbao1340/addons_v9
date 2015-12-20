# -*- coding: utf-8 -*-
from openerp import models, fields, api

class product_product(models.Model):
    _inherit = 'product.product'

    check_avalible = fields.Boolean(default=False, string='is avalible')

