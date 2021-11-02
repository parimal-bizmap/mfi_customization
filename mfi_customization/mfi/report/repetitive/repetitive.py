# Copyright (c) 2013, bizmap technologies and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
from frappe.utils import  getdate,today,add_days,flt
import frappe


def execute(filters=None):
	columns  = get_column()
	data	 = get_data(filters)
	return columns, data
def get_column(filters = None):
	return[
		{
			"label":"Client Name",
			"fieldname":"customer",
			"fieldtype":"Link",
			"options":"Customer",
			"width":180	

		},{
			"label":"Serial Number",
			"fieldname":"serial_no",
			"fieldtype":"Link",
			"options":"Asset Serial No",
			"width":150	

		},{
			"label":"Machine Model",
			"fieldname":"machine_model",
			"fieldtype":"Link",
			"options":"Asset",
			"width":120	

		},
		{
			"label":"Number Of Calls",
			"fieldname":"calls",
			"fieldtype":"Data",
			"width":120		

		}
]

def get_data(filters):
	data = []
	fltr={}
	if filters.get("serial_no"):
		fltr.update({"serial_no":filters.get("serial_no")})
	if filters.get("company"):
		fltr.update({"company":filters.get("company")})
	if filters.get("company"):
		fltr.update({"company":filters.get("company")})
	for ast in frappe.get_all("Asset",fltr,['name','customer','serial_no','item_code','project']):
		count=get_count(ast.name,ast.item_code,filters)
		if count>=1:
			data.append({
					"customer":frappe.db.get_value("Project",ast.project,"customer"),
					"serial_no":ast.get('serial_no'),
					"machine_model":ast.name,
					"calls":count
			})
	return data

def get_count(asset,item_code,filters):
	count=0
	records=frappe.get_all("Machine Reading",{"asset":asset,"reading_date":['between',(filters.get('from_date'),filters.get('to_date'))]},["colour_reading","black_and_white_reading"])
	for i,d in enumerate(records):
		colour_diff=0
		bw_diff=0
		if i!=0:
			colour_diff=flt(records[i-1].colour_reading)-flt(records[i].colour_reading)
			bw_diff=flt(records[i-1].black_and_white_reading)-flt(records[i].black_and_white_reading)
			if frappe.db.get_value("Item",item_code,'avg_duty_cycle')>colour_diff or frappe.db.get_value("Item",item_code,'avg_duty_cycle')>bw_diff:
				count+=1
	return count
				
	
	
	
	