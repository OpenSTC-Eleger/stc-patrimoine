# -*- coding: utf-8 -*-

##############################################################################
#    Copyright (C) 2012 SICLIC http://siclic.fr
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
#############################################################################

from openbase.openbase_core import OpenbaseCore
from osv import fields, osv
import calendar
from mx.DateTime.mxDateTime import strptime
from datetime import datetime
from lxml import etree
from lxml.builder import E
import re
from tools.translate import _

class openstc_patrimoine_contract(OpenbaseCore):
    _name = "openstc.patrimoine.contract"
    
    
    def _get_patrimony_name(self, cr, uid, ids, name ,args, context=None):
        ret = {}
        for contract in self.browse(cr, uid, ids, context=context):
            name = ''
            if contract.patrimoine_is_equipment:
                if contract.equipment_id:
                    name = contract.equipment_id.name_template
            elif contract.site_id:
                name = contract.site_id.name
            ret.update({contract.id:name})
        return ret
    
    _AVAILABLE_STATE_VALUES = [('draft','Draft'),('confirm','Confirm'),('done','Done')]
    
    _columns = {
        'name':fields.char('Name',size=128,required=True),
        'sequence':fields.char('Sequence',size=32),
        'patrimoine_is_equipment':fields.boolean('Is Equipment', required=True),
        'equipment_id':fields.many2one('openstc.equipment','Equipment'),
        'patrimoine_name':fields.function(_get_patrimony_name,type='char',string='Patrimony',
                                          store={'openstc.patrimoine.contract':[lambda self,cr,uid,ids,ctx:ids,['equipment_id','site_id','patrimoine_is_equipment'],10]}),
        'site_id':fields.many2one('openstc.site','Site'),
        'supplier_id':fields.many2one('res.partner','Supplier', domain=[('supplier','=',True)]),
        'internal_inter':fields.boolean('En régie',),
        'technical_service_id':fields.many2one('openstc.service','Internal Service',help="Technical service that will work according to this contract"),
        'date_start_order':fields.date('Date Start Contract', help="Start Date of the application of the contract"),
        'date_order':fields.date('Date order'),
        'date_end_order':fields.date('Date end Contract',help='Date of the end of this contract. When ended, you could extend it\'s duration or create a new contract.'),
        'state':fields.selection(_AVAILABLE_STATE_VALUES, 'State', readonly=True),
        }

    _defaults = {
        'sequence':lambda self,cr,uid,ctx: self.pool.get("ir.sequence").next_by_code(cr, uid, 'contract.number', ctx),
        'state':'draft',
        'internal_inter':False,
        'date_order':fields.date.context_today,
        'patrimoine_is_equipment':lambda *a: False,
        }


    def onchange_patrimoine_is_equipment(self, cr, uid, ids, patrimoine_is_equipment=False):
        if patrimoine_is_equipment:
            return {'value':{'site_id':False}}
        return {'value':{'equipment_id':False}}
        
openstc_patrimoine_contract()


class openstc_patrimoine_contract_intervention_type(OpenbaseCore):
    _name = "openstc.patrimoine.contract.intervention.type"
    _columns = {
        'name':fields.char('Name',size=128, required=True),
        }

openstc_patrimoine_contract_intervention_type()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: