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

{
    "name": "openstc_patrimoine",
    "version": "0.1",
    "depends": ["openbase",],
    "author": "BP",
    "category": "Category",
    "description": """
    Base Module for patrimony Management.
    it contains base description of patrimonies (materials like cars or technical prod) and sites.
    It extends openstc.equipment and openstc.site from openstc base module.
    """,
    "data": [
            "views/openstc_patrimoine_data.xml", 
            "views/openstc_patrimoine_view.xml",
            "views/openstc_patrimoine_menu.xml",
            #"unit_tests/unit_tests.xml",
            "security/ir.model.access.csv",
             ],
    "demo": [],
    "test": [],
    "installable": True,
    "active": False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
