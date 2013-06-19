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
import calendar
from mx.DateTime.mxDateTime import strptime
from datetime import datetime
from lxml import etree
from lxml.builder import E
import re
from tools.translate import _

class openstc_patrimoine_contract(osv.osv):
    _name = "openstc.patrimoine.contract"
    
    _AVAILABLE_STATE_VALUES = [('draft','Draft'),('confirm','Confirm'),('done','Done')]
    
    _columns = {
        'name':fields.char('Name',size=128,required=True),
        'sequence':fields.char('Sequence',size=32),
        'patrimoine_id':fields.many2one('product.product','patrimony associated'),
        'supplier_id':fields.many2one('res.partner','Supplier', domain=[('supplier','=',True)]),
        'internal_inter':fields.boolean('En régie',),
        'technical_service_id':fields.many2one('openstc.service','Internal Service',help="Technical service that will work according to this contract"),
        #'type_intervention':fields.many2many('openstc.patrimoine.contract.intervention.type','openstc_patrimoine_contract_type_rel','contract_id','type_inter_id','Intervention type(s) contracted'),
        'contract_line':fields.one2many('openstc.patrimoine.contract.line', 'contract_id', 'Intervention Lines'),
        'date_start_order':fields.date('Date Start Contract', help="Start Date of the application of the contract"),
        'date_order':fields.date('Date order'),
        'date_end_order':fields.date('Date end Contract',help='Date of the end of this contract. When ended, you could extend it\'s duration or create a new contract.'),
        'state':fields.selection(_AVAILABLE_STATE_VALUES, 'State', readonly=True),
        #TODO:'intervention_ids':fields.one2many('')
        }

    _defaults = {
        'sequence':lambda self,cr,uid,ctx: self.pool.get("ir.sequence").next_by_code(cr, uid, 'contract.number', ctx),
        'state':'draft',
        'internal_inter':False,
        'date_order':fields.date.context_today,
        }


    
    def fields_get(self, cr, uid, allfields=None, context=None, write_access=True):
        res = super(openstc_patrimoine_contract,self).fields_get(cr, uid, allfields, context, write_access)
#        for data in self.pool.get("openstc.patrimoine.contract.intervention.type").parse_datas(cr, uid, context):
#            res[data[0]] = {'type':'boolean','string':data[1]}
        return res
    
    def is_type_inter(self, name):
        return name.startswith('type_inter_')
    
    def get_type_inter_id(self, name):
        return int(name.split('type_inter_')[1])
    
    #write values to many2many field according to dynamic fields values
    def compute_type_inter_values(self, cr, uid, values, context=None):
        to_add = []
        to_remove = []
        dynamic_fields = [x[0] for x in self.pool.get("openstc.patrimoine.contract.intervention.type").parse_datas(cr, uid, context)]
        for key, value in values.items():
            if key in dynamic_fields:
                if self.is_type_inter(key):
                    if value:
                        to_add.append(self.get_type_inter_id(key)) 
                    else:
                        to_remove.append(self.get_type_inter_id(key))
        values['type_intervention'] = [(3,x) for x in to_remove] + [(4,x) for x in to_add]
        return values
    
    #write values to dynamic fields according to m2m values
    def compute_dynamic_type_inter_values(self, cr, uid, values, context=None):
        dynamic_fields = [x[0] for x in self.pool.get("openstc.patrimoine.contract.intervention.type").parse_datas(cr, uid, context)]
        if 'type_intervention' in values:
            for field in dynamic_fields:
                if self.get_type_inter_id(field) in values['type_intervention']:
                    values[field] = True
                else:
                    values[field] = False
        return values
    
    def get_all_recurrences(self, cr, uid, ids, context=None):
        for contract in self.browse(cr, uid, ids, context=context):
            line_ids = [line.id for line in contract.contract_line]
            self.pool.get("openstc.patrimoine.contract.line").get_all_recurrences(cr, uid, line_ids, context=context)
        return True
    
    def create(self, cr, uid, vals, context=None):
        #self.compute_type_inter_values(cr, uid, vals, context)
        res = super(openstc_patrimoine_contract, self).create(cr, uid, vals, context=context)
        return res
    
    #Override to push contract dates modifications to recur date of each lines contract  
    def write(self, cr, uid, ids, vals, context=None):
        #self.compute_type_inter_values(cr, uid, vals, context)
        
        if 'date_start_order' in vals or 'date_end_order' in vals:
            for contract in self.browse(cr, uid, ids, context=context):
                values = []
                action = {}
                if 'date_start_order' in vals:
                    vals['date_start_order'] = vals['date_start_order'][:10]
                    action.update({'start_recur':vals['date_start_order']})
                if 'date_end_order' in vals:
                    vals['date_end_order'] = vals['date_end_order'][:10]
                    action.update({'end_recur':vals['date_end_order']})
                values.extend([(1,line.id,action) for line in contract.contract_line])
                if 'contract_line' in vals:
                    vals['contract_line'].extend(values)
                else:
                    vals['contract_line'] = values
                super(openstc_patrimoine_contract, self).write(cr, uid, [contract.id], vals, context=None)
        else:
            super(openstc_patrimoine_contract, self).write(cr, uid, ids, vals, context=None)
        return True
    
#    def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
#        #force reading of dynamic fields
#        if not fields:
#            fields = self.fields_get(cr, uid, context=context).keys()
#        if not 'type_intervention' in fields:
#            fields.append('type_intervention')
#        res = super(openstc_patrimoine_contract,self).read(cr, uid, ids, fields, context=context, load=load)
#        if not isinstance(res, list):
#            res = [res]
#        for values in res:
#            self.compute_dynamic_type_inter_values(cr, uid, values, context)
#        return res
    
openstc_patrimoine_contract()

class openstc_patrimoine_contract_line(osv.osv):
    _name = "openstc.patrimoine.contract.line"
    
    _AVAILABLE_PERIOD_VALUES = [('day','Day'),('week','Week'),('month','Month'),('year','Year')]
    
    #get first occurrence in draft state as next_inter, and last occurrence in done state as last_inter
    def _get_next_inter(self, cr, uid, ids, name, args, context=None):
        ret = {}
        for line in self.browse(cr, uid, ids, context=context):
            next_inter = False
            last_inter = False
            ret[line.id] = {}
            #get occurrences list, ordered by date_order (according to _order attribute of object)
            for occurrence in line.occurrence_line:
                if occurrence.is_active() and not next_inter:
                    next_inter = occurrence.date_order
                elif not occurrence.is_active() and not last_inter:
                    last_inter = occurrence.date_order
            ret[line.id] = {'next_inter':next_inter, 'last_inter':last_inter}
        return ret
    
    def _get_line_from_occur(self, cr, uid, ids, context=None):
        occ = self.pool.get("openstc.patrimoine.contract.occurrence").browse(cr, uid, ids, context=context)
        ret = []
        for item in occ:
            if item.contract_line_id.id not in ret:
                ret.append(item.contract_line_id.id)
        return ret
    
    _columns = {
        #'name':fields.char('Name',size=128),
        'contract_id':fields.many2one('openstc.patrimoine.contract', 'Contract linked'),
        'start_recur':fields.date('Recurrence start date', help="Date of recurrence beginning"),
        'end_recur':fields.date('Recurrence end date', help="Date of recurrence ending"),
        #'last_inter':fields.datetime('Date last intervention', help="Planned date of the next intervention, you can change it as you want."),
        'last_inter':fields.function(_get_next_inter, multi='recur', method=True, type='date',string='Date last intervention', help="Planned date of the next intervention, you can change it as you want.",
                                     store={'openstc.patrimoine.contract.occurrence':(_get_line_from_occur, ['date_order','state'], 10),
                                            'openstc.patrimoine.contract.line':(lambda self,cr,uid,ids,ctx={}:ids,['occurence_line'],11)}),
        #'next_inter':fields.datetime('Date next intervention', help="Date of the last intervention executed in this contract"),
        'next_inter':fields.function(_get_next_inter, multi='recur', method=True, type='date', string='Date next intervention', help="Date of the last intervention executed in this contract",
                                     store={'openstc.patrimoine.contract.occurrence':(_get_line_from_occur, ['date_order','state'], 10),
                                            'openstc.patrimoine.contract.line':(lambda self,cr,uid,ids,ctx={}:ids,['occurence_line'],11)}),
        'recurrence':fields.selection(_AVAILABLE_PERIOD_VALUES, 'Recurrence'),
        'recurrence_weight':fields.integer('Each'),
        'type_inter':fields.many2one('openstc.patrimoine.contract.intervention.type','Intervention Type'),
        'occurrence_line':fields.one2many('openstc.patrimoine.contract.occurrence', 'contract_line_id', 'Occurrence(s)'),
        'technical_service_id':fields.related('contract_id','technical_service_id',type='many2one',relation='openstc.service', string='Internal Service', store=True),
        'patrimoine_id':fields.related('contract_id','patrimoine_id',type='many2one',relation='product.product',string="patrimony associated", store=True),
        }

    _defaults = {
        'recurrence_weight':1,
        'recurrence':'year',
        
        }
    
    _order = "next_inter,technical_service_id"

    def parse_datas(self, cr, uid, context=None):
        ret = []
        ids = self.search(cr, uid, [], context=context)
        for data in self.browse(cr, uid, ids, context=context):
            ret.append(('type_inter_%s' % (str(data.id),), data.name))
        return ret
    
    def update_view_inter_type(self, cr, uid, context=None):
        #get xml object : openstc.patrimoine.contract.inherit.type to overwrite it's arch field
        view = self.pool.get('ir.model.data').get_object(cr, 1, 'openstc_patrimoine', 'openstc_patrimoine_contract_form_inherit_type', context)
        if view and view._table_name == 'ir.ui.view':
            xml = []
            xml1 = []
            xml = E.field(
                          *(E.separator(string=_('Intervention Type(s) contracted'), 
                                        colspan='4'),
                            E.group(
                                   *([E.field(name=x[0]) for x in self.parse_datas(cr, uid, context)]),
                                   col="6", colspan="4")),
                          position="replace", 
                          name="type_intervention")
            xml.addprevious(etree.Comment("GENERATED AUTOMATICALLY BY OPENSTC PATRIMOINE CONTRACTS"))
            xml_content = etree.tostring(xml, pretty_print=True, xml_declaration=True, encoding="utf-8")
            #self.write onto xml arch field
            view.write({'arch': xml_content})
        return True
    
        #compute next inter date and create all the interventions associated
    #TOCHECK: do we keep daily and weekly recurrence or remove them?
    def get_all_recurrences(self, cr, uid, ids, context=None):
        for contract in self.browse(cr, uid, ids, context=context):
            dates = []
            if contract.end_recur:
                recurrence_weight = 1
                
                #date_ref = datetime.strptime(contract.start_recur,'%Y-%m-%d %H:%M:%S')
                dates.append(contract.start_recur[:10])
                if contract.recurrence:
                    #give value to recurrence_weight, keep default value to 1 otherwise
                    if contract.recurrence_weight:
                        recurrence_weight = contract.recurrence_weight
                    #begin compute dates
                    if contract.recurrence == 'month':
                        #get nb of occurrences
                        #year nb
                        year =  int(contract.end_recur[:4]) - int(contract.start_recur[:4])
                        #month nb
                        month = int(contract.end_recur[5:7]) - int(contract.start_recur[5:7])
                        #day ref
                        day = int(contract.start_recur[8:10])
                        year_iter = int(contract.start_recur[:4])
                        month_iter = int(contract.start_recur[5:7])
                        for i in range(int((month + year * 12) / recurrence_weight)):
                            month_iter += recurrence_weight
                            if month_iter >12:
                                month_iter -= 12
                                year_iter += 1
                            #avoid date error, i.e. 30 Feb
                            max_day = calendar.monthrange(year_iter, month_iter)
                            day_iter = min(max_day,day)
                            dates.append('-'.join([str(year_iter),
                                                   '0' + str(month_iter) if month_iter <10 else  str(month_iter),
                                                   '0' + str(day_iter) if day_iter <10 else  str(day_iter)]))
                    elif contract.recurrence == 'year':
                        #get nb of occurrences
                        #year nb
                        year =  int(contract.end_recur[:4]) - int(contract.start_recur[:4])
                        #month ref
                        month = int(contract.start_recur[5:7])
                        #day ref
                        day = int(contract.start_recur[8:10])
                        year_iter = int(contract.start_recur[:4])
                        for i in range(int(year / recurrence_weight)):
                            year_iter += recurrence_weight
                            #avoid date error, i.e. 30 Feb
                            max_day = calendar.monthrange(year_iter, month)
                            day_iter = min(max_day,day)
                            dates.append('-'.join([str(year_iter),
                                                   '0' + str(month) if month < 10 else  str(month),
                                                   '0' + str(day_iter) if day_iter <10 else  str(day_iter)]))
                            
                #TODO: write all tasks at each dates computed.
            else:
                raise osv.except_osv("Error","No End Date registered for this contract. This case is not efficient for now, please supply an end date.")
            now = datetime.now()
            #if last occurrence is > than end recur, we force it to end recur value
            if len(dates) > 0:
                if dates[-1] > contract.end_recur[:10]:
                    dates[-1] = contract.end_recur[:10]
            #write earlier date of intervention (dates before now are ignored)
            values = [(2,x.id) for x in contract.occurrence_line]
            for date in dates:
                if date > str(now):
                    values.append((0,0,{'date_order':date}))
            self.write(cr, uid, [contract.id], {'occurrence_line':values}, context=context)        
        return True
    
    def create(self, cr, uid, vals, context=None):
        ret = super(openstc_patrimoine_contract_line, self).create(cr, uid, vals, context=None)
        #self.update_view_inter_type(cr, uid, context)
        return ret
    
    def write(self, cr, uid, ids, vals, context=None):
        ret = super(openstc_patrimoine_contract_line, self).write(cr, uid, ids, vals, context=None)
        #self.update_view_inter_type(cr, uid, context)
        return ret
    
    def delete(self, cr, uid, ids, context=None):
        ret = super(openstc_patrimoine_contract_line, self).delete(cr, uid, ids, context=None)
        #self.update_view_inter_type(cr, uid, context)
        return ret
    
openstc_patrimoine_contract_line()

class openstc_patrimoine_contract_occurrence(osv.osv):
    
    def get_state_values(self, cr, uid, context=None):
        return [('draft','Draft'),('done','Done'),('alert','Alert'),('cancel','Cancel'),('in_progress','In Progress')]
    
    def _get_func_state_values(self, cr, uid, context=None):
        return self.get_state_values(cr, uid, context=context)
    
    _name = 'openstc.patrimoine.contract.occurrence'
    _columns = {
        'date_order':fields.date('Date Order', required=True),
        'state':fields.selection(_get_func_state_values, 'State'),
        'contract_line_id':fields.many2one('openstc.patrimoine.contract.line', 'Line Contract linked'),
        'observation':fields.text('Observations'),
        'technical_service_id':fields.related('contract_line_id','technical_service_id',type='many2one',relation='openstc.service', string='Internal Service', store=True),
        'patrimoine_id':fields.related('contract_line_id','patrimoine_id',type='many2one',relation='product.product',string="patrimony associated", store=True),
        'type_inter':fields.related('contract_line_id','type_inter', type="many2one", relation='openstc.patrimoine.contract.intervention.type', string="Type Inter", store=True)
        }
    _defaults = {
        'state':lambda *a: 'draft',
        }
        
    def is_active(self, cr, uid, ids, context=None):
        if isinstance(ids, list):
            ids = ids[0]
        return self.browse(cr, uid, ids, context=context).state not in ('done','cancel')
    
    _order = "date_order"
    
openstc_patrimoine_contract_occurrence()

class openstc_patrimoine_contract_intervention_type(osv.osv):
    _name = "openstc.patrimoine.contract.intervention.type"
    _columns = {
        'name':fields.char('Name',size=128, required=True),
        }

    def parse_datas(self, cr, uid, context=None):
        ret = []
        ids = self.search(cr, uid, [], context=context)
        for data in self.browse(cr, uid, ids, context=context):
            ret.append(('type_inter_%s' % (str(data.id),), data.name))
        return ret
    
    def update_view_inter_type(self, cr, uid, context=None):
        #get xml object : openstc.patrimoine.contract.inherit.type to overwrite it's arch field
        view = self.pool.get('ir.model.data').get_object(cr, 1, 'openstc_patrimoine', 'openstc_patrimoine_contract_form_inherit_type', context)
        if view and view._table_name == 'ir.ui.view':
            xml = []
            xml1 = []
            xml = E.field(
                          *(E.separator(string=_('Intervention Type(s) contracted'), 
                                        colspan='4'),
                            E.group(
                                   *([E.field(name=x[0]) for x in self.parse_datas(cr, uid, context)]),
                                   col="6", colspan="4")),
                          position="replace", 
                          name="type_intervention")
            """for data in self.parse_datas(cr, uid, context):
                xml1.append(E.field(name=data[0]))
            xml1 = E.group(*(xml1), colspan="4", col="6")
            xml1.insert(0,E.separator(string=_('Intervention Type(s) contracted'), colspan="4"))
            xml = E.field(*(xml1), name='type_intervention', position='replace')
            """
            xml.addprevious(etree.Comment("GENERATED AUTOMATICALLY BY OPENSTC PATRIMOINE CONTRACTS"))
            xml_content = etree.tostring(xml, pretty_print=True, xml_declaration=True, encoding="utf-8")
            #self.write onto xml arch field
            view.write({'arch': xml_content})
        return True
    
    def create(self, cr, uid, vals, context=None):
        ret = super(openstc_patrimoine_contract_intervention_type, self).create(cr, uid, vals, context=None)
        #self.update_view_inter_type(cr, uid, context)
        return ret
    
    def write(self, cr, uid, ids, vals, context=None):
        ret = super(openstc_patrimoine_contract_intervention_type, self).write(cr, uid, ids, vals, context=None)
        #self.update_view_inter_type(cr, uid, context)
        return ret
    
    def delete(self, cr, uid, ids, context=None):
        ret = super(openstc_patrimoine_contract_intervention_type, self).delete(cr, uid, ids, context=None)
        #self.update_view_inter_type(cr, uid, context)
        return ret
    
openstc_patrimoine_contract_intervention_type()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: