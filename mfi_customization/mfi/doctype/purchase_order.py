from __future__ import unicode_literals
import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt, nowdate, getdate
from frappe import _

def on_submit(doc,method):
    create_sales_order(doc)

def create_sales_order(doc):
    if doc.company=="Mfi managed document solutions ltd":
        sales_doc = get_mapped_doc("Purchase Order", doc.name, {
            "Purchase Order": {
                "doctype": "Sales Order",
                "field_map": {
                    "schedule_date":"delivery_date"
                },
            },
            "Purchase Order Item": {
                "doctype": "Sales Order Item"
                }
            }, ignore_permissions=True)
        customer=frappe.db.get_value("Customer", {'represents_company': doc.company},'name')
        sales_doc.customer =customer if customer else ''
        company=frappe.db.get_value("Supplier", {'name': doc.supplier, 'is_internal_supplier':1},'represents_company')
        sales_doc.company =company if company else ''
        for d in sales_doc.get("items"):
            d.warehouse="Stores - MFIINTL"
        sales_doc.save()
        frappe.db.set_value("Sales Order",{"name":sales_doc.name},"delivery_date",doc.schedule_date)