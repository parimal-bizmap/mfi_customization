# -*- coding: utf-8 -*-
# Copyright (c) 2020, bizmap technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def make_task(source_name, target_doc=None):
	return get_mapped_doc("Issue", source_name, {
		"Issue": {
			"doctype": "Task"
		}
	}, target_doc)

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


@frappe.whitelist()
def get_serial_no_list(doctype, txt, searchfield, start, page_len, filters):
	location=''
	asset=''
	if filters.get('location'):
		location=" where location='{0}'".format(filters.get('location'))
	if filters.get('asset'):
		if not filters.get('location'):
			location=" where location='{0}'".format(filters.get('asset'))
		else:
			location="and asset='{0}'".format(filters.get('asset'))
	return frappe.db.sql("""select name
		from `tabAsset Serial No` {location} {asset}
		"""
		.format(location = location, asset=asset
		))

def validate(doc,method):
	if doc.status=="Closed":
		for t in frappe.get_all('Task',filters={'issue':doc.name},fields=['name','status']):
			if t.status != 'Completed':
				frappe.throw("Please Complete <b>Issue '{0}'</b>".format(t.name))
