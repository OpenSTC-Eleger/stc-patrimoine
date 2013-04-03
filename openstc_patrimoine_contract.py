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
        'first_inter':fields.datetime('Date first intervention', help="Date of the first intervention planned or executed in this contract"),
        'last_inter':fields.datetime('Date last intervention', help="Planned date of the next intervention, you can change it as you want."),
        'next_inter':fields.datetime('Date next intervention', help="Date of the last intervention executed in this contract"),
        'date_order':fields.datetime('Date order'),
        'date_end_order':fields.datetime('Date end order',help='Date of the end of this contract. When ended, you could extend it\'s duration or create a new contract.'),
        'state':fields.selection(_AVAILABLE_STATE_VALUES, 'State', readonly=True),
        #TODO:'intervention_ids':fields.one2many('')
        'recurrence':fields.selection(_AVAILABLE_PERIOD_VALUES, 'Recurrence'),
        'recurrence_weight':fields.integer('Each'),
        }

    _defaults = {
        'sequence':lambda self,cr,uid,ctx: self.pool.get("ir.sequence").next_by_code(cr, uid, 'contract.number', ctx),
        'state':'draft',
        'recurrence_weight':1,
        'recurrence':'day',
        'internal_inter':False,
        'date_order':fields.date.context_today,
        }

    #compute next inter date and create all the interventions associated
    def get_all_recurrences(self, cr, uid, ids, context=None):
        dates = []
        for contract in self.browse(cr, uid, ids, context=context):
            if contract.date_end_order:
                recurrence_weight = 1
                
                #date_ref = datetime.strptime(contract.first_inter,'%Y-%m-%d %H:%M:%S')
                dates.append(contract.first_inter)
                if contract.recurrence:
                    #give value to recurrence_weight, keep default value to 1 otherwise
                    if contract.recurrence_weight:
                        recurrence_weight = contract.recurrence_weight
                    #begin compute dates
                    if contract.recurrence == 'month':
                        #get nb of occurrences
                        #year nb
                        year =  int(contract.date_end_order[:4]) - int(contract.first_inter[:4])
                        #month nb
                        month = int(contract.date_end_order[5:7]) - int(contract.first_inter[5:7])
                        #day ref
                        day = int(contract.first_inter[8:10])
                        year_iter = int(contract.first_inter[:4])
                        month_iter = int(contract.first_inter[5:7])
                        for i in range(int((month + year * 12) / recurrence_weight)):
                            month_iter += recurrence_weight
                            if month_iter >12:
                                month_iter = 1
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
                        year =  int(contract.date_end_order[:4]) - int(contract.first_inter[:4])
                        #month ref
                        month = int(contract.first_inter[5:7])
                        #day ref
                        day = int(contract.first_inter[8:10])
                        year_iter = int(contract.first_inter[:4])
                        for i in range(int(year / recurrence_weight)):
                            year_iter += recurrence_weight
                            #avoid date error, i.e. 30 Feb
                            max_day = calendar.monthrange(year_iter, month)
                            day_iter = min(max_day,day)
                            dates.append('-'.join([str(year_iter),
                                                   '0' + str(month) if month < 10 else  str(month),
                                                   '0' + str(day_iter) if day_iter <10 else  str(day_iter)]))
                    #TOCHECK: do we keep daily and weekly recurrence or remove them? 
                #TODO: write all tasks at each dates computed.
            #write next_inter date if exists
            else:
                raise osv.except_osv("Error","No End Date registered for this contract. This case is not efficient for now, please supply an end date.")
            now = datetime.now()
            for date in dates:
                if date > str(now):
                    self.write(cr, uid, [contract.id], {'next_inter':date}, context=context)
                    break
            
        return
    
    

openstc_patrimoine_contract()

class openstc_patrimoine_contract_intervention_type(osv.osv):
    _name = "openstc.patrimoine.contract.intervention.type"
    _columns = {
        'name':fields.char('Name',size=128, required=True),
        }
    
openstc_patrimoine_contract_intervention_type()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: