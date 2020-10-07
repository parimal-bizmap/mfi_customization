# -*- coding: utf-8 -*-
# Copyright (c) 2020, bizmap technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def make_task(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.asset_=source.asset
		target.set('older__reading',[])
		for d in source.get('current_reading'):
			target.append("current_reading", {
				"date":d.get('date'),
				"type":d.get('type'),
				"asset":d.get('asset'),
				"reading":d.get('reading')
			})
		if source.project:
			pro_doc=frappe.get_doc('Project',source.project)
			for d in pro_doc.get('machine_readings'):
				if d.get('asset')==source.asset:
					target.append("older__reading", {
						"date":d.get('date'),
						"type":d.get('type'),
						"asset":d.get('asset'),
						"reading":d.get('reading')
					})
	return get_mapped_doc("Issue", source_name, {
		"Issue": {
			"doctype": "Task"
		}
	}, target_doc,set_missing_values)

@frappe.whitelist()
def get_asset_list(doctype, txt, searchfield, start, page_len, filters):
	location=''
	if filters.get('location'):
		location="and location='{0}'".format(filters.get('location'))

	return frappe.db.sql("""select asset,asset_name
		from `tabAsset List` 
		where
			parent='{project}' {location}"""
		.format(project = filters.get("project") , location=location
		))

def validate(doc,method):
	if doc.status=="Closed":
		for t in frappe.get_all('Task',filters={'issue':doc.name},fields=['name','status']):
			if t.status != 'Completed':
				frappe.throw("Please Complete <b>Issue '{0}'</b>".format(t.name))
