# Copyright (c) 2013, bizmap technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import re

def execute(filters=None):
	columns = get_columns()
	data  = get_data(filters)
	return columns, data

def get_columns(filters = None):
	
	return[
			{
			"label":"Response Time (hours)",
			"fieldname":"response_time",
			"fieldtype":"Data"	

		},{
			"label":"Call Assign Date",
			"fieldname":"call_assign_date",
			"fieldtype":"Data"	

		},{
			"label":"Call Resolved Date Time",
			"fieldname":"call_resolution_date",
			"fieldtype":"Data"	

		},{
			"label":"Client Name",
			"fieldname":"client_name",
			"fieldtype":"Data"	

		},{
			"label":"Machine Model",
			"fieldname":"machine_model",
			"fieldtype":"Data"	

		},{
			"label":"Serial Number",
			"fieldname":"serial_no",
			"fieldtype":"Data"	

		},{
			"label":"Nature of Problem",
			"fieldname":"nature_of_prob",
			"fieldtype":"Data"	

		},
		]

def get_data(filters):
	data = []
	response_time = 0
	call_assign_date = 0
	fltr = ""
	lgc_value = ""
	digit = 0
	fltr2 = {}
	row ={}

	if filters.get("response_time"):
		fltr = filters.get("response_time")
		lgc_value = fltr[0]
		digit = fltr[1:]
		
	if filters.get("client_name"):
		fltr2.update({"customer":filters.get("client_name")})
	if filters.get("c_name"):
		fltr2.update({"company":filters.get("c_name")})

	for i in frappe.get_all('Issue',fltr2,['name','company','failure_date_and_time','response_date_time','resolution_date','customer','asset','serial_no','issue_type']):
		#Calculating the diff and converting time in fours
		if i.get('response_date_time') and i.get('failure_date_and_time'):
			
			response_time_diff = (i.get('response_date_time')- i.get("failure_date_and_time")) 
			hrs = ((response_time_diff.seconds//60)%60)/60
			response_time = round(((response_time_diff.days * 24) + (((response_time_diff.seconds//3600)) + hrs)),2)			
		
		else:
			response_time = None
		#applying filters according to condition set
		if i.get('response_date_time') != None:
			call_assign_date = (i.get('response_date_time')).strftime("%d/%m/%Y")
		if lgc_value == '>' and  int(digit) <= response_time:
				row = {
			'response_time': response_time,
			'call_assign_date':call_assign_date ,
			'call_resolution_date': i.get("resolution_date"),
			'client_name':i.get("customer"),
			'machine_model':i.get("asset"),
			'serial_no':i.get("serial_no"),
			'nature_of_prob': i.get("issue_type")
					}
		elif lgc_value == '<' and  int(digit) >= response_time:
				row = {
			'response_time': response_time,
			'call_assign_date':call_assign_date ,
			'call_resolution_date': i.get("resolution_date"),
			'client_name':i.get("customer"),
			'machine_model':i.get("asset"),
			'serial_no':i.get("serial_no"),
			'nature_of_prob': i.get("issue_type")
					}
		#if no condition filter is applied
		elif lgc_value == '':
				row = {
			'response_time': response_time,
			'call_assign_date':call_assign_date ,
			'call_resolution_date': i.get("resolution_date"),
			'client_name':i.get("customer"),
			'machine_model':i.get("asset"),
			'serial_no':i.get("serial_no"),
			'nature_of_prob': i.get("issue_type")
					}
		data.append(row)
	
		
		

	return data