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

# @frappe.whitelist()
# def get_asset_in_issue(doctype, txt, searchfield, start, page_len, filters):
# 	cond1=''
# 	cond2=''
# 	if filters.get("customer"):
# 			print(filters.get("customer"),"***************")
# 			cond2+="where customer ='{0}'".format(filters.get("customer"))

# 	if filters.get("location"):
# 			cond1+="where location='{0}'".format(filters.get("location"))
		
# 	data = frappe.db.sql("""select asset from `tabAsset Serial No` where asset IN (select name from `tabAsset` {0} and project = (select name
# 		from `tabProject`  {1}))
# 		""".format(cond1,cond2))
# 	print(data)
# 	return data
@frappe.whitelist()
def get_asset_in_issue(doctype, txt, searchfield, start, page_len, filters):
	cond1 = ''
	cond2 = ''
	cond3 = ''
	if txt:
		cond3 = "and name = '{0}'".format(txt)
	if filters.get("customer"):
			cond2+="where customer ='{0}'".format(filters.get("customer"))

	if filters.get("location"):
			cond1+="where location='{0}'".format(filters.get("location"))
		
	data = frappe.db.sql("""select asset from `tabAsset Serial No` 
			where asset IN (select name from `tabAsset` {0} and project = (select name
		from `tabProject`  {1} {2}))
		""".format(cond1,cond2,cond3))
	return data


@frappe.whitelist()
def get_serial_no_list(doctype, txt, searchfield, start, page_len, filters):
 	if txt:
 		filters.update({"name": ("like", "{0}%".format(txt))})
 	return frappe.get_all("Asset Serial No",filters=filters,fields = ["name"], as_list=1)

def validate(doc,method):
	if doc.status=="Closed":
		for t in frappe.get_all('Task',filters={'issue':doc.name},fields=['name','status']):
			if t.status != 'Completed':
				frappe.throw("Please Complete <b>Issue '{0}'</b>".format(t.name))
		if len(frappe.get_all('Task',filters={'issue':doc.name},fields=['name','status']))==0:
			if len(doc.get('current_reading'))==0:
				frappe.throw("Please add Asset readings before closing issue")
@frappe.whitelist()
def get_customer(serial_no,asset):
	project = frappe.get_value('Asset',{'serial_no':serial_no},'project')
	customer = frappe.db.get_value('Project',{'name':project},'customer')
	name =  frappe.db.get_value('Customer',{'name':customer},'name')
	return name

@frappe.whitelist()
def get_location(doctype, txt, searchfield, start, page_len, filters):
	lst = []
	fltr = {}
	if txt:
			fltr.update({"location": ("like", "{0}%".format(txt))})
	for i in frappe.get_all('Project',filters,['name']):
		fltr.update({'project':i.get('name')})
		for a in frappe.get_all('Asset',fltr,['location']):
			if a.location not in lst:
				lst.append(a.location)
	return [(d,) for d in lst]	
		
# @frappe.whitelist()
# def get_live_asset(doctype, txt, searchfield, start, page_len, filters):
# 	cond = ''
# 	if txt:
# 		cond= "and name = '{0}'".format(txt)
# 	data =  frappe.db.sql("""select name from `tabAsset` where docstatus = 1 {0}""".format(cond))
# 	return data