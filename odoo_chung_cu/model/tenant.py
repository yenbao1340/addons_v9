# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import except_orm

class Tenant(models.Model):
    _name = 'apartment.tenant'

    partner_id = fields.Many2one('res.partner', "Khách hàng", required = True)
    contract_id = fields.Many2one('apartment.contract', 'Hợp đồng')
    date_start = fields.Date('Ngày bắt đầu', required = True)
    date_end = fields.Date('Ngày kết thúc')
    gui_xe = fields.Boolean('Gửi xe tháng')
    type = fields.Char('Loại xe')
    color = fields.Char('Màu xe')
    number = fields.Char('Biển số xe')
    is_lead = fields.Boolean('Is Lead')

    def unlink(self, cr, uid, ids, context=None):
        species = self.browse(cr, uid, ids)
        if species.is_lead == True:
            raise except_orm('Lỗi!',
                                 'Không thể xóa Tenant chính')
        rs = super(Tenant, self).unlink(cr, uid, ids, context)
        return rs

    @api.model
    def create(self, vals):
        rs = super(Tenant, self).create(vals)
        cxt = self.env.context
        if cxt['params'].has_key('id'):
            if cxt['params']['id']:
                rs.contract_id = cxt['params']['id']
        return rs