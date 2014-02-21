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

from osv import fields, osv

class openstc_patrimoine_site(osv.osv):
    _name="openstc.patrimoine.site"
    _inherits = {'product.product':'product_id'}
    
    _columns = {
        'site_id':fields.many2one('openstc.site','Site associé'),
        'product_id':fields.many2one('product.product','Produit Associé', required=True, ondelete="cascade"),
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
        'type_prod':'site',
        'sale_ok':lambda *a:False,
        }


openstc_patrimoine_site()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: