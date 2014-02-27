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
from osv import fields,osv

class openstc_equipement(OpenbaseCore):
    _inherit = "openstc.equipment"

    
    _columns = {
            'patrimoine_contract_ids':fields.one2many('openstc.patrimoine.contract', 'equipment_id', 'Contracts linked'),
            #'occurrences_contract_ids':fields.one2many('openstc.patrimoine.contract.occurrence','equipment_id', string="Incoming internal interventions"),

        }
openstc_equipement()

class openstc_site(OpenbaseCore):
    _inherit = "openstc.site"

    
    _columns = {
            'patrimoine_contract_ids':fields.one2many('openstc.patrimoine.contract', 'site_id', 'Contracts linked'),
            #'occurrences_contract_ids':fields.one2many('openstc.patrimoine.contract.occurrence','site_id', string="Incoming internal interventions"),

        }
openstc_equipement()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
