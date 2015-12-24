# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import except_orm, Warning, RedirectWarning
import time, datetime




class ql_chung_cu_hop_dong(models.Model):
    _name = "apartment.contract"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name = fields.Char('Số hợp đồng', required=True)
    tenent_id = fields.One2many('apartment.tenant', 'contract_id',readonly = True, states={'confirm': [('readonly', False)]})
    # room_id = fields.Many2one('apartment.room', "Phòng", required=True, states={'confirm': [('readonly', True)]})
    price = fields.Float('Đơn giá', states={'confirm': [('readonly', True)]})
    deposit = fields.Float('Số tiền đặt cọc')
    date_created = fields.Date('Ngày tạo hợp đồng')
    date_start = fields.Date('Ngày bắt đầu hợp đồng', required=True, states={'confirm': [('readonly', True)]})
    date_end = fields.Date('Ngày kết thúc hợp đồng')
    water_start = fields.Float('Chỉ số nước ban đầu', required=True, states={'confirm': [('readonly', True)]})
    power_start = fields.Float('Chỉ số điện ban đầu', required=True, states={'confirm': [('readonly', True)]})
    supplier_id = fields.Many2one('res.partner', 'Khách hàng', required=True, states={'confirm': [('readonly', True)]})
    sale_id = fields.One2many('sale.order', 'contract_id', readonly=True)
    room_product_id = fields.One2many('apartment.contract.room','contract_id', string='Phòng', states={'confirm': [('readonly', True)]})
    base_service_product_id = fields.One2many('apartment.contract.base.service','contract_id', string='Dịch vụ cơ bản')
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirm', 'Xác nhận'),
        ('cancel', 'Đã hủy')], 'Trạng thái')
    _defaults = {
        'state': 'draft',
        'date_created': time.strftime('%Y-%m-%d'),
        'date_start': time.strftime('%Y-%m-%d'),
    }
    
    @api.model
    def create(self,vals):
        now = datetime.datetime.now()
        cxt = self.env.context
        id=super(ql_chung_cu_hop_dong, self).create(vals)
        xx = 'CONTRACT-'
        xx += str(id.id)
        xx += str(now.month)
        xx += str((now.year)%1000%100)
        id.update({'name':xx})
    

        return  id
    

    @api.one
    def write(self, vals):
        rs = super(ql_chung_cu_hop_dong, self).write(vals)
        if self.date_end != False:
            if self.date_end < self.date_start:
                raise except_orm('Lỗi!',
                                 'Ngày kết thúc hợp đồng không thể nhỏ hơn ngày bắt đầu hợp đồng')
        return rs

    @api.multi
    def create_field(self):
          return {
            'name': 'view_paid_contract',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'paid.contract',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }

    @api.one
    def create_invoice(self):
        """
        Tạo hóa đơn tiền đặt cọc khi xác nhận hợp đồng
        :return:
        """
        try:
            invoice = self.env['account.invoice'].create({
                'partner_id': self.supplier_id.id,
                'date_invoice': time.strftime('%Y-%m-%d'),
                'comment': u'Hóa đơn đặt cọc tiền thuê nhà %s' %self.room_product_id.room_product.name,
                'type': 'out_invoice',
                'account_id': 8,
            })
            invoice_line = self.env['account.invoice.line'].create({
                'product_id': self.env.ref('odoo_chung_cu.invoice_room').id,
                'price_unit': self.deposit,
                'invoice_id': invoice.id,
                'name': self.room_product_id.room_product.name
            })
        except except_orm as e:
                raise except_orm('Lỗi! Tạo hóa đơn đặt cọc tiền thuê nhà')
        return True

    @api.one
    def create_tenant(self):
        """
        Khi xác nhận hợp đồng thì đưa người ký hợp đồng vào làm tenant chính
        :return:
        """
        try:
            self.env['apartment.tenant'].create({
                                'partner_id': self.supplier_id.id,
                                'contract_id': self.id,
                                'date_start': self.date_start,
                                'is_lead': True,
                            })

        except except_orm as e:
                raise except_orm('Lỗi! Tạo tenant')
        return True

    @api.one
    def action_confirm(self):
            try:
                if len(self.room_product_id) == 1:
                    #  Tạo invoice
                    self.create_invoice()
                    # Set check avalible trong product
                    self.room_product_id.room_product.check_avalible = True
                    # Tạo tenant
                    self.create_tenant()
                    pre_month = self.env['apartment.month.index'].search([('room_id', '=', self.room_product_id.room_product.id),
                                                                          ('state', '=', 'confirm')],
                                                                         order='date desc', limit=1)
                    contract_ids = self.search([('room_product_id.room_product', '=', self.room_product_id.room_product.id), ('state', '=', 'confirm')],
                                               order='date_start desc', limit=1)  # get hop dong truoc do
                    price = self.env['apartment.price'].search([('id', '!=', 0)], order='id desc', limit=1)
                    month = self.env['apartment.month'].search(
                        [('year', '=', datetime.datetime.strptime(self.date_start, '%Y-%m-%d').strftime("%Y")),
                         ('date_start', '<=', self.date_start), ('date_end', '>=', self.date_start)])
                    if contract_ids:
                        if (contract_ids.date_end == False):
                            raise except_orm('Lỗi!', 'Vui lòng thêm ngày kết thúc vào hợp đồng số %s' % contract_ids.name)
                        elif contract_ids.date_end >= self.date_start:
                            raise except_orm('Lỗi!',
                                             'Không thể xác nhận 1 hợp đồng có ngày bắt đầu nhỏ hơn hoặc bằng ngày kết thúc của số hợp đồng %s' % contract_ids.name)
                        elif (self.date_end != False) and (self.date_end < self.date_start):
                            raise except_orm('Lỗi!',
                                             'Ngày kết thúc hợp đồng không thể nhỏ hơn ngày bắt đầu hợp đồng')
                        else:
                            if pre_month:
                                if (pre_month.water_number < self.water_start or pre_month.power_number < self.power_start):
                                    self.env['apartment.month.index'].create({
                                        'room_id': self.room_product_id.room_product.id,
                                        'water_price': price.water_price,
                                        'power_price': price.power_price,
                                        'date': self.date_start,
                                        'month': month.id,
                                        'old_power':pre_month.power_number,
                                        'old_water':pre_month.water_number,
                                        'water_number': self.water_start,
                                        'power_number': self.power_start,
                                        'state': 'confirm'
                                    })
                                    self.state = 'confirm'
                                else:
                                    raise except_orm('Lỗi!',
                                                     'Chỉ số mới không thể nhỏ hơn chỉ số cũ!' )
                    else:
                        month = self.env['apartment.month'].search(
                            [('year', '=', datetime.datetime.strptime(self.date_start, '%Y-%m-%d').strftime("%Y")),
                             ('date_start', '<=', self.date_start), ('date_end', '>=', self.date_start)])
                        pre_month = self.env['apartment.month.index'].search([('room_id', '=', self.room_product_id.room_product.id),
                                                                              ('state', '=', 'confirm')],
                                                                             order='date, id desc', limit=1)
                        if pre_month:
                            if (pre_month.water_number <= self.water_start or pre_month.power_number <= self.power_start):
                                self.env['apartment.month.index'].create({
                                    'room_id': self.room_product_id.room_product.id,
                                    'date': self.date_start,
                                    'water_price': price.water_price,
                                    'power_price': price.power_price,
                                    'month': month.id,
                                    'old_power':pre_month.power_number,
                                    'old_water':pre_month.water_number,
                                    'water_number': self.water_start,
                                    'power_number': self.power_start,
                                    'state': 'confirm'
                                })
                                self.state = 'confirm'
                            elif (self.date_end != False) and (self.date_end < self.date_start):
                                raise except_orm('Lỗi!',
                                                 'Ngày kết thúc hợp đồng không thể nhỏ hơn ngày bắt đầu hợp đồng')
                            else:
                                raise except_orm('Lỗi!',
                                                 'Chỉ số mới không thể nhỏ hơn chỉ số cũ!')
                        else:
                            self.env['apartment.month.index'].create({
                                'room_id': self.room_product_id.room_product.id,
                                'date': self.date_start,
                                'water_price': price.water_price,
                                'power_price': price.power_price,
                                'month': month.id,
                                'water_number': self.water_start,
                                'power_number': self.power_start,
                                'state': 'confirm'
                            })
                            self.state = 'confirm'
                elif len(self.room_product_id) > 1:
                    raise except_orm('Lỗi!','Mỗi hợp đồng chỉ có thể có 1 phòng cho thuê')
                else:
                    raise except_orm('Lỗi!','Vui lòng chọn  1 phòng trong hợp đồng')
            except except_orm as e:
                raise except_orm('Lỗi!')
            return True

    @api.one
    def action_cancel(self):
        self.state = 'cancel'

    @api.model
    def _cron_check_avalible(self):
        date_now = time.strftime('%Y-%m-%d')
        contract_list = self.search([('state', '=', 'confirm'), ('date_end', '!=', False)])
        for contract in contract_list:
            if contract_list.date_end == date_now:
                if contract.room_product_id:
                    contract.room_product_id.room_product.check_avalible = False



