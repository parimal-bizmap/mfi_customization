from __future__ import unicode_literals
import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt, nowdate, getdate
from frappe import _

@frappe.whitelist()
def set_data_sales_order(source_name, target_doc=None):
    def set_missing_values(source,target):
        customer=frappe.db.get_value("Customer", {'represents_company': source.company},'name')
        target.customer =customer if customer else ''
        company=frappe.db.get_value("Supplier", {'name': source.supplier, 'is_internal_supplier':1},'represents_company')
        target.company =company if company else ''
    doc = get_mapped_doc("Purchase Order", source_name, {
        "Purchase Order": {
            "doctype": "Sales Order",
            "validation": {
                "docstatus": ["=", 1]
            }
         },
        "Purchase Order Item": {
            "doctype": "Sales Order Item"
            }
        },target_doc, set_missing_values)
    return doc