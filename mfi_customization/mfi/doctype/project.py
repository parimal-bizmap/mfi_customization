# -*- coding: utf-8 -*-
# Copyright (c) 2020, bizmap technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.mapper import get_mapped_doc

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

@frappe.whitelist()
def make_asset_delivery_note(source_name, target_doc=None):
    def set_missing_values(source,target):
        if source.customer:
            target.customer_name=frappe.db.get_value("Customer",source.customer,"customer_name")
        if source.sales_order:
            sales_order_doc=frappe.get_doc("Sales Order",source.sales_order)
            for d in sales_order_doc.get("asset_quotation_selection"):
                if frappe.db.get_value("Item",d.asset,'is_fixed_asset'):
                    target.append("asset_models",{
                        "asset_model":frappe.db.get_value("Item",d.asset,'stock_item'),
                        "model_name":d.asset_name,
                        "qty":d.qty
                    })
    return get_mapped_doc("Project", source_name, {
        "Project": {
            "doctype": "Asset Delivery Note"
        }
    }, target_doc,set_missing_values)

def validate(doc,method):
    if doc.sales_order:
        for d in frappe.get_all("Sales Order",{"name":doc.sales_order},['total_contract_amount']):
            doc.estimated_costing=d.total_contract_amount

