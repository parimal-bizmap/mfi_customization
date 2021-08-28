# Copyright (c) 2021, bizmap technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today

class MachineReadingTool(Document):
	pass

@frappe.whitelist()	
def get_machine_reading(project):
	asset_list=[]
	for ast in frappe.get_all("Asset",filters={'project':project}, fields=['name',"asset_name"],order_by="name"):
		asset_list.append(({"asset":ast.name,"asset_name":ast.asset_name}))
	return asset_list



@frappe.whitelist()
def create_machine_reading(readings):
	print("###########")
	print(readings)
	return []