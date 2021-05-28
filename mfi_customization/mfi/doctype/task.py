# -*- coding: utf-8 -*-
# Copyright (c) 2020, bizmap technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import getdate,today
from frappe.model.mapper import get_mapped_doc

def validate(doc,method):
	for d in doc.get("current_reading"):
		if d.idx>1:
			frappe.throw("More than one row not allowed")
	if doc.get('__islocal'):
		for d in frappe.get_all("Task",{"issue":doc.issue}):
			frappe.throw("Task <b>{0}</b> Already Exist Against This Issue".format(doc.name))
	if  doc.project:
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
		

def after_insert(doc,method):
	if doc.get('issue'):
		frappe.db.set_value('Issue',doc.get('issue'),'status','Assigned')
	last_reading=today()
	if len(frappe.get_all("Machine Reading",filters={"project":doc.project,"asset":doc.asset,"reading_date":("<",last_reading)},fields=["reading_date","asset","black_and_white_reading","colour_reading","total","machine_type"],limit=1,order_by="reading_date desc"))!=0:
		for d in frappe.get_all("Machine Reading",filters={"project":doc.project,"asset":doc.asset,"reading_date":("<",last_reading)},fields=["reading_date","asset","black_and_white_reading","colour_reading","total","machine_type"],limit=1,order_by="reading_date desc"):
			doc.append("last_readings", {
				"date" : d.get('reading_date'),
				"type" : d.get('machine_type'),
				"asset":d.get('asset'),
				"reading":d.get('black_and_white_reading'),
				"reading_2":d.get('colour_reading')
				})
	else:
		for d in frappe.get_all("Machine Reading",filters={"project":doc.project,"asset":doc.asset,"reading_date":("<=",last_reading)},fields=["reading_date","asset","black_and_white_reading","colour_reading","total","machine_type"],limit=1,order_by="reading_date desc"):
			doc.append("last_readings", {
				"date" : d.get('reading_date'),
				"type" : d.get('machine_type'),
				"asset":d.get('asset'),
				"reading":d.get('black_and_white_reading'),
				"reading_2":d.get('colour_reading')
				})
	doc.save()
	if doc.failure_date_and_time and doc.issue:
		doc.failure_date_and_time=frappe.db.get_value("Issue",doc.issue,"failure_date_and_time")
	if doc.issue:
		doc.description=frappe.db.get_value("Issue",doc.issue,"description")
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
	
	# Share Task with user respectively
	docperm = frappe.new_doc("User Permission")
	docperm.update({
		"user": doc.completed_by,
		"allow": 'Task',
		"for_value": doc.name
	})

	docperm.save(ignore_permissions=True)
	

	# Share Task with user respectively
	# docshare = frappe.new_doc("DocShare")
	# docshare.update({
	# 	"user": doc.completed_by,
	# 	"share_doctype": 'Task',
	# 	"share_name": doc.name,
	# 	"read": 1,
	# 	"write": 1
	# })

	# docshare.save(ignore_permissions=True)
	
			
	

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


@frappe.whitelist()
def make_asset_movement(source_name, target_doc=None, ignore_permissions=False):
	def set_missing_values(source, target):
	   customer = frappe.db.get_value("Task", source_name,'customer')
	   company = frappe.db.get_value("Project",{"customer":customer},'company')
	   target.purpose = "Transfer"
	   target.company = company
	   target.task=source_name



	doclist = get_mapped_doc("Task", source_name, {
		"Task": {
			"doctype": "Asset Movement",
			
		}
	}, target_doc ,set_missing_values, ignore_permissions=ignore_permissions)

	return doclist

@frappe.whitelist()
def set_readings(project,asset,target_doc=None):
	
	reading_list=[]
	for d in frappe.get_all('Asset Readings',filters={'parent':project,'asset':asset,'parenttype':'Project'},fields=['date','type','asset','reading','reading_2']):
		
		reading_list.append({
			'date':d.date,
			'type':d.type,
			'asset':d.asset,
			'black_white':d.get("reading"),
			'colour':d.get("reading_2")
		})
	
	return reading_list


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

@frappe.whitelist()
def get_tech(doctype, txt, searchfield, start, page_len, filters):
	tch_lst = []
	fltr = {}
	dct = {}
	if txt:
			fltr.update({"full_name": ("like", "{0}%".format(txt))})
	for i in frappe.get_roles(filters.get("user")):
		
		for ss in frappe.db.get_all('Support Setting Table',{'back_office_team_role':i},['technician_role','back_office_team_role']):
			for usr in frappe.get_all('User',fltr,['name','full_name']):
				if ss.get('technician_role') in frappe.get_roles(usr.get("name")) and not usr.get("name") == 'Administrator':
					
					if usr.name not in tch_lst:
						tch_lst.append(usr.name)
						dct.update({usr.full_name:usr.name})
	
	return [(y,d) for d,y in dct.items()]


@frappe.whitelist()
def check_material_request_status(task):
	flag = False
	
	for i in frappe.get_all('Material Request',{'task_':task},['status']):
		if i.get('status') not in ['Stopped','Cancelled','Issued']:
			flag = True
	return flag
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

@frappe.whitelist()
def get_asset_in_task(doctype, txt, searchfield, start, page_len, filters):
	cond1 = ''
	cond2 = ''
	cond3 = ''
	if txt:
		cond3 = "and name = '{0}'".format(txt)
	if filters.get("customer"):
			cond2+="where customer ='{0}'".format(filters.get("customer"))

	if filters.get("location"):
			cond1+="and location='{0}'".format(filters.get("location"))
		
	data = frappe.db.sql("""select asset from `tabAsset Serial No` 
			where asset IN (select name from 
			`tabAsset` where docstatus = 1  {0} 
			and project = (select name
			from `tabProject`  {1} {2}))
		""".format(cond1,cond2,cond3))
	return data

@frappe.whitelist()
def get_serial_no_list(doctype, txt, searchfield, start, page_len, filters):
 	if txt:
 		filters.update({"name": ("like", "{0}%".format(txt))})
		
 	return frappe.get_all("Asset Serial No",filters=filters,fields = ["name"], as_list=1)


@frappe.whitelist()
def get_serial_on_cust_loc(doctype, txt, searchfield, start, page_len, filters):
	# data = frappe.db.sql("""select name from `tabProject` """)
	fltr1 = {}
	fltr2 = {}
	lst = []
	if filters.get('customer'):
		fltr1.update({'customer':filters.get('customer')})
	if filters.get('location'):
		fltr2.update({'location':filters.get('location')})
	if txt:
		fltr2.update({'serial_no':txt})
	for i in frappe.get_all('Project',fltr1,['name']):
		fltr2.update({'project':i.get('name'),'docstatus':1})
		for j in frappe.get_all('Asset',fltr2,['serial_no']):
			if j.serial_no not in lst:
					lst.append(j.serial_no)
	return [(d,) for d in lst]	


@frappe.whitelist()
def get_asset_serial_on_cust(doctype, txt, searchfield, start, page_len, filters):
		fltr = {}
		asst = {}
		lst = []
		if filters.get('customer'):
			fltr.update({'customer':filters.get('customer')})
		if txt:
			asst.update({'serial_no':("like", "{0}%".format(txt))})
		# asst.update()
		for i  in frappe.get_all('Project',fltr,['name']):
			asst.update({'project':i.get('name'),'docstatus':1})
			for ass in frappe.get_all('Asset',asst,['serial_no']):
				if ass.serial_no not in lst:
					lst.append(ass.serial_no)
		return [(d,) for d in lst]	

@frappe.whitelist()
def get_customer(serial_no,asset):
	project = frappe.get_value('Asset',{'serial_no':serial_no},'project')
	customer = frappe.db.get_value('Project',{'name':project},'customer')
	name =  frappe.db.get_value('Customer',{'name':customer},'name')
	return name
@frappe.whitelist()
def get_asset_on_cust(doctype, txt, searchfield, start, page_len, filters):
		fltr = {}
		asst = {}
		lst = []
		if filters.get('customer'):
			fltr.update({'customer':filters.get('customer')})
		if txt:
			asst.update({'name':("like", "{0}%".format(txt))})
		# asst.update()
		for i  in frappe.get_all('Project',fltr,['name']):
			asst.update({'project':i.get('name'),'docstatus':1})
			for ass in frappe.get_all('Asset',asst,['name']):
				if ass.name not in lst:
					lst.append(ass.name)
		return [(d,) for d in lst]	

def on_change(doc,method):
	create_machine_reading(doc)
	set_reading_from_task_to_issue(doc)
	validate_reading(doc)
	if doc.issue and doc.status not in ['Open','Completed']:
		frappe.db.set_value("Issue",doc.issue,'status',doc.status)

def create_machine_reading(doc):
	for d in doc.get('current_reading'):
		if len(frappe.get_all("Machine Reading",{"task":doc.name,"project":doc.project,"asset":d.get('asset'),"reading_date":d.get('date')}))<1:
			mr=frappe.new_doc("Machine Reading")
			mr.reading_date=d.get('date')
			mr.asset=d.get('asset')
			mr.black_and_white_reading=d.get("reading")
			mr.colour_reading=d.get("reading_2")
			mr.machine_type=d.get('type')
			mr.total=d.get("total")
			mr.project=doc.project
			mr.task=doc.name
			mr.save()
	
def set_reading_from_task_to_issue(doc):
	issue_doc=frappe.get_doc('Issue',{'name':doc.get("issue")})
	duplicate=[]
	for d in doc.get('current_reading'):
		for pr in issue_doc.get('current_reading'):
			if d.type== pr.type and d.asset == pr.asset and d.reading == pr.reading:
				duplicate.append(d.idx)
	for d in doc.get('current_reading'):
		for isu in doc.get("current_reading"):
			isu.date=d.get('date')
			isu.type=d.get('type')
			isu.asset=d.get('asset')
			isu.reading=d.get('reading')
			isu.reading_2=d.get('reading_2')
			issue_doc.save()

def validate_reading(doc):
	for d in doc.get('current_reading'):
		d.total=(d.get('reading') or 0 +d.get('reading_2') or 0)
	if len(doc.get('current_reading'))>0:
		reading=(doc.get('current_reading')[-1]).get('reading') if (doc.get('current_reading')[-1]).get('reading') else (doc.get('current_reading')[-1]).get('reading_2')
		if not str(reading).isdigit():
			frappe.throw("only numbers allowed in reading")
		for lst in doc.get("last_readings"):
			last_reading=lst.get("reading") if lst.get("reading") else lst.get("reading_2")
			current_reading=(doc.get('current_reading')[-1]).get('reading') if (doc.get('current_reading')[-1]).get('reading') else (doc.get('current_reading')[-1]).get('reading_2')
			if last_reading>current_reading:
				frappe.throw("Current Reading Must be Greater than Last Reading")

# @frappe.whitelist()		
# def set_status(user,status):
# 		#for i in  frappe.get_roles(user):
# 			flag = 0
# 			for s in frappe.get_all('Support Setting Table',['technician_role']):
# 				if s.get('technician_role') in frappe.get_roles(user):
# 					flag = 1
				
# 			return flag




