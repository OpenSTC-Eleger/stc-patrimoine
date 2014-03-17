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
    
    """ @note: bubble-up name_search of patrimoine_name to equipment_id.name and site_id.name"""
    def _search_func_patrimoine_name(self, cr, uid, obj, name, args, context=None):
        search_args = []
        for arg in args:
            search_args.extend(['|',('equipment_id.name',arg[1],arg[2]),('site_id.name',arg[1],arg[2])])
        return search_args
    
    def _get_provider_name(self, cr, uid, ids, name, args, context=None):
        ret = {}.fromkeys(ids, '')
        for contract in self.browse(cr, uid, ids, context=context):
            name = ''
            if contract.internal_inter:
                name = contract.technical_service_id.name if contract.technical_service_id else ''
            else:
                name = contract.supplier_id.name if contract.supplier_id else ''
            ret[contract.id] = name
        return ret
    
    def _search_func_provider_name(self, cr, uid, obj, name, args, context=None):
        search_args = []
        for arg in args:
            search_args.extend(['|',('technical_service_id.name',arg[1],arg[2]),('partner_id.name',arg[1],arg[2])])
        return search_args
        
    _AVAILABLE_STATE_VALUES = [('draft','Draft'),('confirm','Confirm'),('done','Done')]
    
    """ @return: list of tuples of available 'type renewals' (key,value)
    @note: Override this method to update this list instead of its private name-like method"""
    def get_type_renewal_values(self, cr, uid, context=None):
        return [('auto','Tacite'),('manual','Express')]
    
    def _get_type_renewal_values(self, cr, uid, context=None):
        return self.get_type_renewal_values(cr, uid, context=context)
    
    _actions = {
        'update':lambda self,cr,uid,record,groups_code: True,
        'delete':lambda self,cr,uid,record,groups_code: record.state in ('draft',),
        'confirm':lambda self,cr,uid,record,groups_code: record.state in ('draft',),
        'done':lambda self,cr,uid,record,groups_code: record.state in ('confirm',),
        'extend':lambda self,cr,uid,record,groups_code: record.state in ('confirm','done'),
        }
    
    _columns = {
        'name':fields.char('Name',size=128,required=True),
        "description":fields.text('Description'),
        'sequence':fields.char('Sequence',size=32),
        'patrimoine_is_equipment':fields.boolean('Is Equipment', required=True),
        'equipment_id':fields.many2one('openstc.equipment','Equipment'),
        'patrimoine_name':fields.function(_get_patrimony_name,type='char', fnct_search=_search_func_patrimoine_name, string='Patrimony',store=False),
        'site_id':fields.many2one('openstc.site','Site'),
        'internal_inter':fields.boolean('En régie',),
        'supplier_id':fields.many2one('res.partner','Supplier', domain=[('supplier','=',True)]),
        'technical_service_id':fields.many2one('openstc.service','Internal Service', domain=[('technical','=',True)],help="Technical service that will work according to this contract"),
        'category_id':fields.many2one('openstc.patrimoine.contract.type', 'Category', required=True),
        'provider_name': fields.function(_get_provider_name, type='char',  fnct_search=_search_func_provider_name, string='Provider', store=False),
        'date_start_order':fields.date('Date Start Contract', help="Start Date of the application of the contract"),
        'date_order':fields.date('Date order'),
        'date_end_order':fields.date('Date end Contract',help='Date of the end of this contract. When ended, you could extend it\'s duration or create a new contract.'),
        'deadline_delay':fields.integer('Delay (days)'),
        'type_renewal':fields.selection(_get_type_renewal_values, 'Type renewal'),
        'state':fields.selection(_AVAILABLE_STATE_VALUES, 'State', readonly=True),
        
        }

    _defaults = {
        'sequence':lambda self,cr,uid,ctx: self.pool.get("ir.sequence").next_by_code(cr, uid, 'contract.number', ctx),
        'state':'draft',
        'internal_inter':False,
        'date_order':fields.date.context_today,
        'patrimoine_is_equipment':lambda *a: False,
        'type_renewal': lambda *a: 'auto',
        }


    def onchange_patrimoine_is_equipment(self, cr, uid, ids, patrimoine_is_equipment=False):
        if patrimoine_is_equipment:
            return {'value':{'site_id':False}}
        return {'value':{'equipment_id':False}}
        
openstc_patrimoine_contract()


class openstc_patrimoine_contract_intervention_type(OpenbaseCore):
    _name = "openstc.patrimoine.contract.type"
    _columns = {
        'name':fields.char('Name',size=128, required=True),
        }

openstc_patrimoine_contract_intervention_type()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: