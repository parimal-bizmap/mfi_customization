# -*- coding: utf-8 -*-
# Copyright (c) 2020, bizmap technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import getdate,today
from frappe.model.mapper import get_mapped_doc

def validate(doc,method):
	if doc.issue_type in ['Toner Request','Machine Issue'] and doc.project:
		pro_doc=frappe.get_doc('Project',doc.project)
		if doc.status=='Completed' and doc.project:
			duplicate=[]
			for d in doc.get('current_reading'):
				for pr in pro_doc.get('machine_readings'):
					if getdate(d.date) ==  getdate(pr.date) and d.type== pr.type and d.asset == pr.asset:
						duplicate.append(d.asset)
			for d in doc.get('current_reading'):
				if d.asset not in duplicate:
					pro_doc.append("machine_readings", {
					"date" : d.get('date'),
					"type" : d.get('type'),
					"asset":d.get('asset'),
					"reading":d.get('reading')
					}) 
			pro_doc.save()


		if doc.status=='Completed' :
			for t in frappe.get_all('Asset Repair',filters={'task':doc.name}):
				ar=frappe.get_doc('Asset Repair',t.name)
				ar.repair_status='Completed'
				ar.completion_date=today()
				ar.save()
				ar.submit()



	if doc.get('issue'):
		frappe.db.set_value('Issue',doc.get('issue'),'status','Assigned')
		

def after_insert(doc,method):
	if doc.issue_type in ['Toner Request','Machine Issue'] and doc.project:
		task_list=[]
		for t in frappe.get_all('Asset Repair',filters={'task':doc.name}):
			task_list.append(t.name)
		if doc.status!='Completed' and doc.name not in task_list:
			asset_doc = frappe.new_doc("Asset Repair")
			asset_doc.task=doc.name
			asset_doc.asset_name=doc.asset
			asset_doc.project=doc.project
			asset_doc.assign_to=doc.completed_by
			asset_doc.description=doc.description
			asset_doc.failure_date=doc.failure_date_and_time
			for d in doc.get('current_reading'):
				asset_doc.append("repair_on_reading", {
					"date" : d.get('date'),
					"type" : d.get('type'),
					"asset":d.get('asset'),
					"reading":d.get('reading')
					}) 
			asset_doc.save()

def after_delete(doc,method):
	for t in frappe.get_all('Asset Repair',filters={'task':doc.name}):
		frappe.delete_doc('Asset Repair',t.name)

@frappe.whitelist()
def make_material_req(source_name, target_doc=None):
	doclist = get_mapped_doc("Task", source_name, {
		"Task": {
			"doctype": "Material Request"
		}
	}, target_doc )

	return doclist

def set_item_from_material_req(doc,method):
	if doc.get('task_') and doc.status=="Issued":
		task=frappe.get_doc('Task',doc.get('task_'))
		items=[]
		for t in task.get('refilled__items'):
			items.append(t.item)
		for d in doc.get('items'):
			if d.get('item_code') not in items:
				task.append("refilled__items", {
							"item": d.get('item_code'),
							"warehouse": d.get('warehouse'),
							"qty": d.get('qty')
						})
		task.material_request=doc.name
		task.save()

		


				
			





