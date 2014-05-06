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
from datetime import timedelta
from lxml import etree
from lxml.builder import E
import re
from tools.translate import _
import netsvc
class openstc_patrimoine_contract(OpenbaseCore):
    _name = "openstc.patrimoine.contract"
    _parent_name = 'original_contract_id'
    
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
        
    def _search_warning_delay(self, cr, uid, obj ,name, args, context=None):
        ret = []
        cr.execute(''' select id from openstc_patrimoine_contract 
        where date(date_end_order) - date(now()) < 30 + deadline_delay;''')
        ids = cr.fetchall()
        if ids:
            for f,o,v in args:
                ret.append(('id','in' if v else 'not in',ids))
        else:
            ret.append(('id','=',0))
        return ret
    
    _AVAILABLE_STATE_VALUES = [('draft','Draft'),('wait','Wait'),('confirm','Confirm'),('done','Done'), ('cancel','Cancel')]
    
    """ @return: list of tuples of available 'type renewals' (key,value)
    @note: Override this method to update this list instead of its private name-like method"""
    def get_type_renewal_values(self, cr, uid, context=None):
        return [('auto','Tacite'),('manual','Express'), ('none','Aucun')]
    
    def _get_type_renewal_values(self, cr, uid, context=None):
        return self.get_type_renewal_values(cr, uid, context=context)
    
    """ @note: return True if deadline_delay has expired, False otherwise"""
    def _get_delay_passed(self,cr, uid, ids, name ,args,context=None):
        ret = {}.fromkeys(ids, {'delay_passed': False, 'warning_delay':False})
        for contract in self.browse(cr, uid, ids, context=context):
            if contract.state not in ('done','cancel'):
                delta = datetime.strptime(contract.date_end_order, '%Y-%m-%d') - datetime.now()
                contract_remaining_duration = delta.total_seconds() / (3600.0 *24.0)
                #Delay the user has for confirming / canceling renewal
                renewal_remaining_delay = contract_remaining_duration -  contract.deadline_delay
                warning_delay = 30 #@TODO: move it to an ir.property
                ret[contract.id] = {'delay_passed': renewal_remaining_delay <= 0,
                                     'warning_delay': renewal_remaining_delay < warning_delay,
                                     'remaining_delay': renewal_remaining_delay}
        return ret
       
    _actions = {
        'update':lambda self,cr,uid,record,groups_code: record.state in ('draft',),
        'delete':lambda self,cr,uid,record,groups_code: record.state in ('draft','wait'),
        'confirm':lambda self,cr,uid,record,groups_code: record.state in ('wait',),
        #'done':lambda self,cr,uid,record,groups_code: record.state in ('confirm',),
        'renew':lambda self,cr,uid,record,groups_code: record.state not in ('cancel', 'done','draft'),
        'close':lambda self,cr,uid,record,groups_code: record.state not in ('cancel', 'done','draft'),
        'cancel':lambda self,cr,uid,record,groups_code: record.state in ('confirm',),
        'redraft': lambda self,cr,uid,record,groups_code: record.state in ('wait',),
        }
    
    """ write the priority of the record according to its state and the values of 'order' list variable """
    def _get_state_order(self, cr, uid, ids, name, args, context=None):
        order = ['draft','wait','confirm','done']
        max_order = len(order)
        ret = {}.fromkeys(ids, max_order)
        for contract in self.browse(cr, uid, ids, context=context):
            ret[contract.id] = order.index(contract.state) if contract.state in order else max_order
        return ret
    
    _columns = {
        'name':fields.char('Name',size=128,required=True),
        "description":fields.text('Description'),
        "new_description":fields.text('Description of the new contract'),
        'sequence':fields.char('Sequence',size=32),
        'category_id':fields.many2one('openstc.patrimoine.contract.type', 'Category', required=True, select=True),
        'original_contract_id':fields.many2one('openstc.patrimoine.contract', 'original contract'),
        
        'patrimoine_is_equipment':fields.boolean('Is Equipment', required=True),
        'equipment_id':fields.many2one('openstc.equipment','Equipment', select=True),
        'patrimoine_name':fields.function(_get_patrimony_name,type='char', select=True, fnct_search=_search_func_patrimoine_name, string='Patrimony',store=False),
        'site_id':fields.many2one('openstc.site','Site', select=True),
        'internal_inter':fields.boolean('En régie',select=True),
        'supplier_id':fields.many2one('res.partner','Supplier', domain=[('supplier','=',True)], select=True),
        'technical_service_id':fields.many2one('openstc.service','Internal Service', domain=[('technical','=',True)],help="Technical service that will work according to this contract", select=True),
        'provider_name': fields.function(_get_provider_name, type='char',  fnct_search=_search_func_provider_name, string='Provider', store=False),
        
        'date_start_order':fields.date('Date Start Contract', help="Start Date of the application of the contract", select=True),
        'new_date_start_order':fields.date('Date Start of the new Contract', help="Start Date of the application of the new contract"),
        'date_order':fields.date('Date order'),
        'date_end_order':fields.date('Date end Contract',help='Date of the end of this contract. When ended, you could extend it\'s duration or create a new contract.', select=True),
        'new_date_end_order':fields.date('Date end new Contract',help='Date of the end of the new contract'),
        'deadline_delay':fields.integer('Delay (days)'),
        'type_renewal':fields.selection(_get_type_renewal_values, 'Type renewal'),
        'delay_passed':fields.function(_get_delay_passed, multi="delay", method=True, type='boolean', string='To renew', store=False),
        'warning_delay':fields.function(_get_delay_passed, multi="delay", fnct_search= _search_warning_delay,  method=True, type='boolean', string='Near to be renewed', store=False),
        'remaining_delay':fields.function(_get_delay_passed, multi="delay", method=True, type="integer", string="contract remaining duration", store=False),
        
        'state':fields.selection(_AVAILABLE_STATE_VALUES, 'State', readonly=True, required=True),
        'state_order':fields.function(_get_state_order, method=True, required=False, type='integer', store=True),
        
        'cancel_reason':fields.text('Cancel Reason'),
        }
    
    _defaults = {
        'sequence':lambda self,cr,uid,ctx: self.pool.get("ir.sequence").next_by_code(cr, uid, 'contract.number', ctx),
        'state':lambda *a: 'draft',
        'internal_inter':lambda *a: False,
        'date_order':fields.date.context_today,
        'patrimoine_is_equipment':lambda *a: False,
        'type_renewal': lambda *a: 'auto',
        }
    
    _order = "state_order"
    
    """ @return: dict containing values for future renewal contract : 
    * new date start : current date end
    * new date end : new date start + duration of the original contract"""
    def update_new_contract_values(self, cr, uid, ids):
        for contract in self.browse(cr, uid, ids):
            date_end = datetime.strptime(contract.date_end_order, '%Y-%m-%d')
            date_start = datetime.strptime(contract.date_start_order, '%Y-%m-%d')
            delta = date_end - date_start
            new_date_end = date_end + delta
            vals = {'new_description':contract.description,
                    'new_date_start_order':contract.date_end_order,
                    'new_date_end_order': new_date_end.strftime('%Y-%m-%d')}
            contract.write(vals)
        return True
    
    def wkf_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'draft'},context=context)
        return True
    
    def wkf_redraft(self, cr, uid, ids, context=None):
        
        return True
    
    def wkf_wait(self, cr, uid, ids, context=None):
        self.update_new_contract_values(cr, uid, ids)
        self.write(cr, uid, ids, {'state':'wait'},context=context)
        return True
    
    def wkf_confirm(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'confirm'},context=context)
        return True
    
    def wkf_done(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'done'},context=context)
        return True

    def wkf_renew(self, cr, uid, ids, context=None):
        return self.renew(cr, uid, ids, context=context)
    
    def wkf_no_renew(self, cr, uid, ids, context=None):
        return True

    def wkf_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'cancel'},context=context)
        return True

    def onchange_patrimoine_is_equipment(self, cr, uid, ids, patrimoine_is_equipment=False):
        if patrimoine_is_equipment:
            return {'value':{'site_id':False}}
        return {'value':{'equipment_id':False}}
    
    """@note: Return specific values for the newly created contract
    same duration as original contract, new contract begin at date_end of original one """
    def prepare_default_values_renewed_contract(self, cr, uid, original_contract, context=None):
        return {
            'date_start_order':original_contract.new_date_start_order,
            'date_end_order':original_contract.new_date_end_order,
            'description':original_contract.new_description,
            'original_contract_id':original_contract.id
            }
    
    """ @note: for each contract, create a new one with same setting"""
    def renew(self, cr, uid, ids, context=None):
        ret = []
        for contract in self.browse(cr, uid, ids ,context=context):
            vals = self.prepare_default_values_renewed_contract(cr, uid, contract, context=context)
            new_id = self.copy(cr, uid, contract.id, vals, context=context)
            ret.append(new_id)
        return ret
    
    def write(self, cr, uid, ids, vals, context=None):
        wkf_service = netsvc.LocalService('workflow')
        signal = False
        if 'wkf_evolve' in vals:
            signal = vals.pop('wkf_evolve')
        super(openstc_patrimoine_contract, self).write(cr, uid, ids, vals, context=context)
        ret = []
        if signal:
            for id in ids:
                wkf_service.trg_validate(uid, 'openstc.patrimoine.contract', id, signal, cr)
                #try to fetch updated values (work fine for renew action)
                #but if other records are updated without having a link with current id, it won't be returned in 'ret' list
                ret.extend(self.search(cr, uid, [('original_contract_id','child_of', id)], context=context))
        return ret if ret else True
    
openstc_patrimoine_contract()


class openstc_patrimoine_contract_intervention_type(OpenbaseCore):
    _name = "openstc.patrimoine.contract.type"
    
    _actions = {
        'update':lambda self,cr,uid,record,groups_code: True,
        'delete':lambda self,cr,uid,record,groups_code: True,
        
        }
    
    _columns = {
        'name':fields.char('Name',size=128, required=True),
        'code':fields.char('Name',size=32, required=False),
        'parent_id':fields.many2one('openstc.patrimoine.contract.type', 'Parent'),
        }

openstc_patrimoine_contract_intervention_type()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: