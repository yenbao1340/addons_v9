# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import except_orm, Warning, RedirectWarning
import time, datetime




class apartment_service(models.Model):
    _name = 'apartment.service'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    """
        Module cho phép người dùng nhập dịch vụ sử dụng cho tòa nhà
    """
    name = fields.Char(compute='_get_name')
    room_id = fields.Many2one('apartment.room', "Phòng", required=True)
    date = fields.Date('Ngày ghi dịch vụ', required=True)
    service_type = fields.Many2one('apartment.service.conf', 'Loại dịch vụ', required=True)
    price = fields.Float('Tổng tiền')
    description = fields.Char('Ghi chú')
    is_paid = fields.Boolean('Đã thanh toán')
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirm', 'Xác nhận'),
        ('paid', 'Đã thanh toán'),
        ('cancel', 'Đã hủy')], 'Trạng thái')
    _defaults = {
        'state': 'draft',
        'date': time.strftime('%Y-%m-%d'),
        'is_paid': False
    }

   
    
    @api.multi
    def _get_name(self):
        for record in self:
            record.name = self.room_id.name + ' - ' + self.service_type.name

    @api.one
    def action_confirm(self):
        self.state = 'confirm'

    @api.one
    def action_cancel(self):
        self.state = 'cancel'
        
    def ticket_44(self,cr,uid,ids,arg,name="",context=None):
        list_id ={}
        check=self.browse(cr, uid, ids)
        for i in ids:
            id=self.browse(cr,uid,i)
            if(id.room_id == check.room_id):
                if(id.state =='draft'):
                    id_date = id.date.split('-')
                    check_date = check.date.split('-')
                    if(id_date[0] == check_date[0]):
                        if(id_date[1] == check_date[1]):                        
                            list_id[i]=id[0].id
        return list_id 