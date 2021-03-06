# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010, 2014 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv
from openerp.osv.orm import TransientModel


class travel_data(TransientModel):
    _name = 'travel.data'
    _inherit = 'travel.data'

    def load_hotel(self, cr, uid, data, context=None):
        product_hotel = self.pool.get('product.hotel')
        product_supplierinfo = self.pool.get('product.supplierinfo')
        pricelist_partnerinfo = self.pool.get('pricelist.partnerinfo')

        result = []
        supplier_id = False
        suppinfo_id = False
        for r in range(7, data.nrows):
            if data.cell_value(r, 0):
                supplier_name = data.cell_value(r, 0).encode('UTF-8')
                supplier_id = self.find_by_name(cr, uid, 'res.partner',
                                                supplier_name, False, context)
                if not supplier_id:
                    raise osv.except_osv('Error!',
                                         "The supplier " + supplier_name + \
                                         " doesn't exist.")
            if data.cell_value(r, 1) and supplier_id:
                hotel_name = data.cell_value(r, 1).encode('UTF-8')
                context.update({'category': 'hotel'})
                hotel_id = self.find_by_name(cr, uid, 'product.hotel',
                                             hotel_name, True, context)
                hotel = product_hotel.browse(cr, uid, hotel_id, context)
                seller_ids = [s.id for s in hotel.seller_ids]
                if seller_ids:
                    product_supplierinfo.unlink(cr, uid, seller_ids, context)
                svals = {
                    'name': supplier_id,
                    'product_id': hotel.product_id.product_tmpl_id.id,
                    'min_qty': 0
                }
                suppinfo_id = product_supplierinfo.create(cr, uid, svals,
                                                          context)
            if data.cell_value(r, 2) and suppinfo_id:
                pvals = {
                    'suppinfo_id': suppinfo_id,
                    'start_date': self.get_date(data.cell_value(r, 2)),
                    'end_date': self.get_date(data.cell_value(r, 3)),
                    'room_type_id': self.find_by_name(cr, uid, 'option.value',
                                                      data.cell_value(r, 4),
                                                      False, context),
                    'meal_plan_id': self.find_by_name(cr, uid, 'option.value',
                                                      data.cell_value(r, 5),
                                                      False, context),
                    'simple': self.get_value((data.cell_value(r, 6))),
                    'price': self.get_value((data.cell_value(r, 7))),
                    'triple': self.get_value((data.cell_value(r, 8))),
                    'extra_adult': self.get_value((data.cell_value(r, 9))),
                    'child': self.get_value((data.cell_value(r, 10))),
                    'second_child': self.get_value((data.cell_value(r, 11))),
                    'min_quantity': 0
                }
                pricelist_partnerinfo.create(cr, uid, pvals, context)
        return result
