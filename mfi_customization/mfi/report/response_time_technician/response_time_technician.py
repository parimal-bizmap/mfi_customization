# Copyright (c) 2013, bizmap technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data
def get_columns(filters = None):
	return[
			{
			"label":"Month",
			"fieldname":"month",
			"fieldtype":"Data"	

		},{
			"label":"Technician Name",
			"fieldname":"techn_name",
			"fieldtype":"Data"	

		},{
			"label":">4",
			"fieldname":"gt4",
			"fieldtype":"Data"	

		},{
			"label":"<4",
			"fieldname":"lt4",
			"fieldtype":"Data"	

		},{
			"label":">8",
			"fieldname":"gt8",
			"fieldtype":"Data"	

		},{
			"label":">48",
			"fieldname":"gt48",
			"fieldtype":"Data"	

		},{
			"label":"Repetitive",
			"fieldname":"asset_cnt",
			"fieldtype":"Data"	

		}]


def get_data(filters):
	data=[]
	fltr = {}
	fltr1 ={}
	if filters.get("techn_name"):
		fltr1.update({"email":filters.get("techn_name")})
	if filters.get("from_date") and filters.get("to_date"):
		fltr.update({'assign_date':['between',(filters.get('from_date'),filters.get('to_date'))]})
	if filters.get("c_name"):
		fltr.update({"company":filters.get("c_name")})
	for ur in frappe.get_all("User",fltr1):
		row={
				"techn_name":ur.name,
			}
		
		gt4_count=0
		lt4_count=0
		gt8_count=0
		gt48_count=0
		month =[]
		mon_st =""
		asset_cnt =0
		fltr.update({'completed_by':ur.name})
		for tk in frappe.get_all("Task",fltr,['attended_date_time','assign_date','asset','completed_by']):
			if tk.get('attended_date_time') and tk.get('assign_date'):
				response_time_diff = (tk.get("attended_date_time") - tk.get('assign_date')) 
				hrs = ((response_time_diff.seconds//60)%60)/60
				response_time = round(((response_time_diff.days * 24) + (((response_time_diff.seconds//3600)) + hrs)),2)	
				if response_time > 4:
					gt4_count+=1
				if response_time < 4:
					lt4_count+=1
				if response_time > 8:
					gt8_count+=1
				if response_time > 8:
					gt48_count+1
				asset_cnt = len(frappe.get_all("Task",{'completed_by':ur.name,'asset':tk.asset}))
				month.append(tk.get("assign_date").strftime("%B"))
		for i in set(month):
			mon_st += "{0},".format(i)	
					
				
	
		row.update({
			"month":mon_st,
			"gt4":gt4_count,
			"lt4":lt4_count,
			"gt8":gt8_count,
			"gt48":gt48_count,
			"asset_cnt":asset_cnt
		})
		if len(frappe.get_all("Task",{'completed_by':ur.name})) > 0:
			data.append(row)
	return data