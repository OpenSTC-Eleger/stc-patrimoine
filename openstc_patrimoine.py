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

class openstc_patrimoine_site(osv.osv):
    _name="openstc.patrimoine.site"
    _inherits = {#'openstc.site':'site_id',
                 'product.product':'product_id'}
    
    _columns = {
        #'site_id':fields.many2one('openstc.site','Site associé'),
        'product_id':fields.many2one('product.product','Produit Associé'),
        'service_site_id':fields.many2one('openstc.service','Service Responsable'),
        'manager_id':fields.many2one('res.users','Responsable'),
        'surface':fields.float('Surface',digits=(4,2)),
        'site_parent_id':fields.many2one('openstc.patrimoine.site','Site Parent'),
        #surcouche site voirie
        'revetment_type':fields.char('Type de revêtement',size=128),
        'luminaire_type':fields.char('Type de luminaire',size=128),
        #surcouche site Terrain
        'build_surface':fields.float('Surface Bâti(m²)',digits=(4,2)),
        'width':fields.float('Largeur', digits=(4,2)),
        'lenght':fields.float('Longueur',digits=(4,2)),
        #ref cadastrale ????
        #surchouche site Batiment
        'sdo':fields.float('SDO',digits=(4,2),help="SDO = Surface Dans Oeuvre"),
        'shon':fields.float('SHON',digits=(4,2), help="SHON = Surface Hors Oeuvre Nette"),
        'effectif_personnel':fields.integer('Effectif personnel'),
        'time_openning':fields.text('Horaires d\'ouverture'),
        'frequentation_an':fields.integer('Fréquentation par an'),
        'frequentation_max':fields.integer('Féquentation Maximale'),
        'build_type':fields.char('Type de construction',size=128),
        'floor_nb':fields.integer('Nombre de niveaux'),
        'mh_ismh_classification':fields.selection([('mh','MH'),('ismh','ISMH')], 'Classement MH/ISMH'),
        'erp_classification':fields.char('Classement ERP', size=32),
        'built_year':fields.integer('Année de construction'),
        'security_com':fields.char('Comission Sécurité', size=64),
        'floor_nature':fields.text('Nature des sols'),
        'wall_revetment':fields.text('Revêtement mural'),
        
        }
    
    _defaults = {
        'type_prod':'patrimoine',
        'sale_ok':lambda *a:False,
        }


openstc_patrimoine_site()

class equipment(osv.osv):
    
    _inherit = "openstc.equipment"
    _name = "openstc.equipment"

    _columns = {
        'manager_id':fields.many2one('res.users','Responsable'),
        'energy_type':fields.char('Type d\'énergie',size=128),
        'length_amort':fields.integer('Durée d\'amortissement'),
        'purchase_price':fields.float('Prix d\'achat',digits=(6,2)),
        
        }

    _defaults = {
        'type_prod':'materiel',
        }

equipment()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: