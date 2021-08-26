# Copyright (c) 2021, bizmap technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class MachineReadingTool(Document):
	pass

@frappe.whitelist()	
def get_machine_reading(project):
	print("////////////project", project)
	# frappe.db.get_value('')
	fields = ['posting_date','reading_date','asset','billing_status','reading_type', 'machine_type', 'colour_reading', 'black_and_white_reading', 'total']
	machine_reading_data = frappe.get_all("Machine Reading",{'project':project}, ['asset'])
	print("!!!!!!!!!!! machine_reading_data", machine_reading_data)
	return machine_reading_data

@frappe.whitelist()
def mark_machine_reading(project, machine_reading):
	print("ASAS")
	import json
	machine_reading = json.loads(machine_reading);
	reading = []
	print("@@@@@ machine_reading", machine_reading)
	if machine_reading :
		for read in machine_reading.get("asset_reading"):
			print("////////read", read)
			reading.append({
				# "assessment_criteria": criteria,
				"reading": flt(machine_reading["asset_reading"][read])
			})
		reading_result = get_machine_reading_doc(project, machine_reading["asset_reading"])
		print("!!!!!!!!!!!!reading_result", reading_result)
		reading_result.update({
			"project": machine_reading.get("project"),
			"asset": machine_reading.get("asset"),
			"comment": machine_reading.get("comment"),
			"black_and_white_reading":machine_reading.get("black_and_white_reading"),
			"details": reading
		})
		reading_result.save()
		details = {}
		# for d in reading_result.details:
		# 	details.update({d.assessment_criteria: d.grade})
		reading_result_dict = {
			"name": reading_result.name,
			"project": reading_result.project,
			"black_and_white_reading": reading_result.black_and_white_reading,
			# "grade": reading_result.grade,
			"details": details
		}
		return reading_result_dict

def get_machine_reading_doc(project, asset):
	machine_reading = frappe.get_all("Machine Reading", filters={"project": project,
			"asset": asset, "docstatus": ("!=", 2)})
	if machine_reading:
		doc = frappe.get_doc("Machine Reading", machine_reading[0])
		if doc.docstatus == 0:
			return doc
		elif doc.docstatus == 1:
			frappe.msgprint(_("Result already Submitted"))
			return None
	else:
		return frappe.new_doc("Machine Reading")
