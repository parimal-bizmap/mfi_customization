# Copyright (c) 2021, bizmap technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today

class AssetInstallationNote(Document):
	def on_submit(self):
		submit_asset(self)
		# create_stock_entry(self)
		# create_journal_entry(self)

def create_stock_entry(doc):
	warehouse={}
	for d in  doc.get("model_serial_nos"):
		warehouse.update({d.warehouse:(warehouse.get(d.warehouse) or "") +d.serial_no+","})
	se=frappe.new_doc("Stock Entry")
	se.company=frappe.db.get_value("Sales Order",{"name":doc.get('sales_order')},"company")
	se.stock_entry_type="Material Issue"
	se.project=doc.project
	se.asset_delivery_note=doc.name
	for d in warehouse:
		for itm in doc.get("asset_models"):
			se.append("items",{
				"s_warehouse":d,
				"item_code":itm.asset_model,
				"qty":itm.qty,
				"batch_no":doc.batch,
				"serial_no":warehouse.get(d),
				"basic_rate":frappe.db.get_value("Item",itm.asset_model,"valuation_rate") or 0,
				"valuation_rate":frappe.db.get_value("Item",itm.asset_model,"valuation_rate") or 0
			})
	se.save()
	se.submit()

def create_journal_entry(doc):
	total=0
	for d in frappe.get_all("Stock Entry",{"asset_delivery_note":doc.name},["total_outgoing_value"]):
		total+=d.total_outgoing_value
	je=frappe.new_doc("Journal Entry")
	je.company=doc.company
	je.asset_delivery_note=doc.name
	je.posting_date=today()
	je.append("accounts",{
		"account":doc.stock_adjustment_account,
		"reference_type":"Project",
		"reference_name":doc.project,
		"credit_in_account_currency":total
	})
	je.append("accounts",{
		"account":doc.fixed_asset_account,
		"reference_type":"Project",
		"reference_name":doc.project,
		"debit_in_account_currency":total
	})
	je.save()
	je.submit()

def submit_asset(doc):
	if doc.asset:
		asset=frappe.get_doc("Asset",doc.asset)
		if asset.docstatus==0:
			asset.submit()

