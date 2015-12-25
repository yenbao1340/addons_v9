# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import except_orm, Warning, RedirectWarning
import time

class wizard_hoadon(models.TransientModel):
    _name= 'wizardhoadon'
    invoice_date=fields.Date("Ngày ghi hóa đơn", require= True)
    
    @api.one
    def taohoadon(self):
        gethopdong=self.env['apartment.contract'].search([('state','=','draft')])
        hopdongid=[]
        for i in gethopdong:
            hopdongid.append(i.id)
        hopdong=self.env['apartment.contract'].browse(hopdongid)
        try:
            for i in hopdong:
                invoice = self.env['account.invoice'].create({
                    'partner_id': i.supplier_id.id,
                    'date_invoice': self.invoice_date,
                    'type': 'out_invoice',
                    'account_id': 8,
                })
                print invoice
        except except_orm as e:
                raise except_orm('Lỗi! Tạo hóa đơn đặt cọc tiền thuê nhà')
        return True