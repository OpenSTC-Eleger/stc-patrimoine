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
#override of res.users to add accreditation and licenses of each user of the company

class openstc_users_accreditation(osv.osv):
    
    _name = 'openstc.users.accreditation'
    _columns = {
        'name':fields.char('Name', size=256),
        'code':fields.char('Code',size=32),
        'validity_length_year':fields.integer('Year(s) of length validity'),
        }
    
openstc_users_accreditation()


class openstc_users_license(osv.osv):
    
    _name = 'openstc.users.license'
    _columns = {
        'name':fields.char('Name', size=256),
        'code':fields.char('Code',size=32),
        'validity_length_year':fields.integer('Year(s) of length validity'),
        }
    
openstc_users_license()

class res_users(osv.osv):
    _inherit = 'res.users'
    _columns = {
        'openstc_accreditation_ids':fields.one2many('openstc.users.accreditation.rel','user_id','Accreditation(s)'),
        'openstc_license_ids':fields.one2many('openstc.users.license.rel','user_id','License(s)'),
    }
    
res_users()

class openstc_users_accreditation_rel(osv.osv):
    _name = 'openstc.users.accreditation.rel'
    _columns = {
        'user_id':fields.many2one('res.users','Owner'),
        'accreditation_id':fields.many2one('openstc.users.accreditation', 'Accreditation', required=True),
        'date_validity':fields.date('Validity Date'),
        }
openstc_users_accreditation_rel()

class openstc_users_license_rel(osv.osv):
    _name = 'openstc.users.license.rel'
    _columns = {
        'user_id':fields.many2one('res.users','Owner'),
        'license_id':fields.many2one('openstc.users.license', 'License', required=True),
        'date_validity':fields.date('Validity Date'),
        }
openstc_users_license_rel()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
