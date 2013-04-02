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

from osv import fields, osv

class openstc_patrimoine_contract(osv.osv):
    _name = "openstc.patrimoine.contract"
    
    _AVAILABLE_STATE_VALUES = [('draft','Draft'),('confirm','Confirm'),('done','Done')]
    _AVAILABLE_PERIOD_VALUES = [('day','Day'),('week','Week'),('month','Month'),('year','Year')]
    
    _columns = {
        'name':fields.char('Name',size=128,required=True),
        'sequence':fields.char('Sequence',size=32),
        'patrimoine_id':fields.many2one('product.product','patrimony associated'),
        'supplier_id':fields.many2one('res.partner','Supplier', domain=[('supplier','=',True)]),
        'internal_inter':fields.boolean('En régie',),
        'technical_service_id':fields.many2one('openstc.service','Internal Service',help="Technical service that will work according to this contract"),
        'type_intervention':fields.many2many('openstc.patrimoine.contract.intervention.type','openstc_patrimoine_contract_type_rel','contract_id','type_inter_id','Intervention type(s) contracted'),
        'first_inter':fields.datetime('Date first intervention'),
        'last_inter':fields.datetime('Date last intervention'),
        'date_order':fields.datetime('Date order'),
        'state':fields.selection(_AVAILABLE_STATE_VALUES, 'State', readonly=True),
        #TODO:'intervention_ids':fields.one2many('')
        'recurrence':fields.selection(_AVAILABLE_PERIOD_VALUES, 'Recurrence'),
        'recurrence_weight':fields.integer('Each'),
        }

    _defaults = {
         'state':'draft',
        'recurrence_weight':1,
        'recurrence':'day',
        'internal_inter':False,
        'date_order':fields.date.context_today,
        }

openstc_patrimoine_contract()

class openstc_patrimoine_contract_intervention_type(osv.osv):
    _name = "openstc.patrimoine.contract.intervention.type"
    _columns = {
        'name':fields.char('Name',size=128, required=True),
        }
    
openstc_patrimoine_contract_intervention_type()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: