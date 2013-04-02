# -*- coding: utf-8 -*-
##############################################################################
#
#    ModuleName module for OpenERP, Description
#    Copyright (C) 200X Company (<http://website>) author
#
#    This file is a part of ModuleName
#
#    ModuleName is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    ModuleName is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields,osv

class product_product(osv.osv):
    _inherit = "product.product"
    _name = "product.product"
    
    def return_type_prod_values(self, cr, uid, context=None):
        ret = super(product_product, self).return_type_prod_values(cr, uid, context)
        ret.extend([('patrimoine','Patrimoine')])
        return ret
    
    _columns = {    
        }
    
"""    def create(self, cr, uid, vals, context=None):
        if context:
            if 'name_prod' in context:
                vals.update({'name':context['name_prod']})
        return super(product_product, self).create(cr, uid, vals, context=context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if context:
            if 'name_prod' in context:
                vals.update({'name':context['name_prod']})
        return super(product_product, self).write(cr, uid, ids, vals, context=context)"""
    
product_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
