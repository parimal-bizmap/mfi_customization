# -*- coding: utf-8 -*-
# Copyright (c) 2020, bizmap technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

@frappe.whitelist()
def fetch_asset_maintenance_team(maintenance_team):
    doc=frappe.get_doc('Asset Maintenance Team',maintenance_team)
    resp={
        'manager':doc.maintenance_manager,
        'name':doc.maintenance_manager_name,
    }
    team=[]
    for d in doc.get('maintenance_team_members'):
        team.append({'member':d.get('team_member'),
                    'name':d.get('full_name'),
                    'role':d.get('maintenance_role')})
    resp.update({'team_members_list':team})
    return resp

def validate(doc,method):
    for a in doc.get('asset_list'):
        frappe.db.set_value('Asset',a.asset,'asset_owner','Customer')
        frappe.db.set_value('Asset',a.asset,'customer',doc.customer)
        frappe.db.set_value('Asset',a.asset,'project',doc.name)

