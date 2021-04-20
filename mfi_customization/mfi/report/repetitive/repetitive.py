# Copyright (c) 2013, bizmap technologies and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
from frappe.utils import  getdate
import frappe


def execute(filters=None):
	columns  = get_column()
	data	 = get_data(filters)
	return columns, data
def get_column(filters = None):
	return[{
			"label":"Task",
			"fieldname":"tk",
			"fieldtype":"Data"	

		},
			{
			"label":"Client Name",
			"fieldname":"customer",
			"fieldtype":"Data"	

		},{
			"label":"Serial Number",
			"fieldname":"serial_no",
			"fieldtype":"Data"	

		},{
			"label":"Machine Model",
			"fieldname":"machine_model",
			"fieldtype":"Data"	

		},
		{
			"label":"Call Date",
			"fieldname":"call_date",
			"fieldtype":"Data"	

		},
		{
			"label":"Number Of Calls",
			"fieldname":"calls",
			"fieldtype":"Data"	

		}


]


def get_data(filters):
	data = []
	fltr1 = {}
	fltr2 = {}
	if filters.get("serial_no"):
			fltr1.update({'serial_no':filters.get("serial_no")})
	if filters.get("client_name"):
			fltr1.update({'customer':filters.get("client_name")})
			print(fltr1)
	if filters.get("from_date") and filters.get("to_date"):
		fltr2.update({'failure_date_and_time':['between',(filters.get('from_date'),filters.get('to_date'))]})
	for tk in frappe.get_all("Task",fltr2,['failure_date_and_time','asset','name']):
		print(fltr1)
		fltr1.update({'name':tk.get('asset')})
		
		for ast in frappe.get_all("Asset",fltr1,['customer','serial_no','item_code']):
			data.append({
					"tk":tk.name,
					"customer":ast.get('customer'),
					"serial_no":ast.get('serial_no'),
					"machine_model":tk.get('asset'),
					"call_date": tk.get("failure_date_and_time").strftime("%d-%m-%Y"),
					"calls":get_count(tk.name,tk.asset,ast.item_code)
			})
	
	return data

def get_count(name,asset,item_code):
	count=0
	for cu_rd in frappe.get_all("Asset Readings",{"parenttype":"Task","parentfield":"current_reading","parent":name},['asset','date','reading_2','reading']):
		for ls_rd in frappe.get_all("Asset Readings",filters={"parenttype":"Task","parentfield":"last_readings","parent":name,"asset":cu_rd.asset},fields=['asset','date','reading_2','reading'],order_by="date desc",limit=1):
			days_diff=(getdate(cu_rd.date)-getdate(ls_rd.date)).days
			reading_diff=int(cu_rd.reading or 0)-int(ls_rd.reading or 0)
			reading2_diff=int(cu_rd.reading_2 or 0)-int(ls_rd.reading_2 or 0)

			if days_diff >= 1 and days_diff <= 30 and frappe.db.get_value("Item",item_code,'avg_duty_cycle')>reading2_diff or frappe.db.get_value("Item",item_code,'avg_duty_cycle')>reading_diff:
				count+=1
	return count
				
	
	
	
	