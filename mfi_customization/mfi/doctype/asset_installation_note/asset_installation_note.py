# Copyright (c) 2021, bizmap technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today

class AssetInstallationNote(Document):
	def on_submit(self):
		submit_asset(self)
		create_stock_entry(self)
		# create_journal_entry(self)
		validate_date(self)
		create_machine_reading(self)

def create_stock_entry(doc):
	se=frappe.new_doc("Stock Entry")
	se.company=doc.company
	se.stock_entry_type="Material Issue"
	se.project=doc.project
	se.asset_delivery_note=doc.asset_delivery_note
	for ast in frappe.get_all("Asset",{"name":doc.asset},["item_code"]):
		for itm in frappe.get_all("Item",{"name":ast.item_code},["stock_item"]):
			se.append("items",{
				"s_warehouse":frappe.db.get_value("Serial No",doc.asset_serial_no,"warehouse"),
				"item_code":itm.stock_item,
				"qty":1,
				"batch_no":frappe.db.get_value("Serial No",doc.asset_serial_no,"batch_no"),
				"serial_no":doc.asset_serial_no,
				"basic_rate":frappe.db.get_value("Item",itm.stock_item,"valuation_rate") or 0,
				"valuation_rate":frappe.db.get_value("Item",itm.stock_item,"valuation_rate") or 0
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

def validate_date(doc):
	if not doc.inst_date:
		frappe.throw("Please Fill Installation Date")

def create_machine_reading(doc):
	mr=frappe.new_doc("Machine Reading")
	mr.reading_date=doc.inst_date
	mr.asset=doc.asset
	mr.reading_type="Installation"
	mr.machine_type=doc.machine_type
	mr.colour_reading=doc.color_reading
	mr.black_and_white_reading=doc.black_and_white_reading
	mr.project=doc.project
	mr.save()