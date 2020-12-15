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
		location="where location='{0}'".format(filters.get('location'))

	return frappe.db.sql("""select name,asset_name
		from `tabAsset`  {location}"""
		.format(location=location))


@frappe.whitelist()
def get_serial_no_list(doctype, txt, searchfield, start, page_len, filters):
	cond=''
	for i,d in enumerate(filters.keys()):
		if i==0:
			cond+="where {0}='{1}'".format(d,filters.get(d))

		else:
			cond+="and {0}='{1}'".format(d,filters.get(d))
		
	return frappe.db.sql("""select name
		from `tabAsset Serial No` {condition}
		""".format(condition=cond))

def validate(doc,method):
	if doc.status=="Closed":
		for t in frappe.get_all('Task',filters={'issue':doc.name},fields=['name','status']):
			if t.status != 'Completed':
				frappe.throw("Please Complete <b>Issue '{0}'</b>".format(t.name))
		if len(frappe.get_all('Task',filters={'issue':doc.name},fields=['name','status']))==0:
			if len(doc.get('current_reading'))==0:
				frappe.throw("Please add Asset readings before closing issue")
	# if doc.status=='Open' and doc.get('__islocal'):
	# 	import datetime
	# 	import pytz
	# 	tz = pytz.timezone('Africa/Nairobi')
	# 	ct = datetime.datetime.now(tz=tz)
	# 	print(type(ct))
	# 	doc.opening_date_=ct.isoformat()
		
