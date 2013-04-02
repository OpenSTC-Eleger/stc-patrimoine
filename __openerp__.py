# -*- coding: utf-8 -*-
##############################################################################
#
#   Openstc-oe
#
##############################################################################

{
    "name": "openstc_patrimoine",
    "version": "0.1",
    "depends": ["openstc",],
    "author": "BP",
    "category": "Category",
    "description": """
    Base Module for patrimony Management.
    it contains base description of patrimonies (materials like cars or technical prod) and sites.
    It extends openstc.equipment and openstc.site from openstc base module.
    """,
    "data": [
        "views/openstc_patrimoine_view.xml",
        "views/openstc_patrimoine_menu.xml",
             ],
    "demo": [],
    "test": [],
    "installable": True,
    "active": False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
