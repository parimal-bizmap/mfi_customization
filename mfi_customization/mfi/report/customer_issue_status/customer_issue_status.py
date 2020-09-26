# Copyright (c) 2013, bizmap technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	data = prepare_data(filters)
	columns = get_columns(filters)

	return columns, data

def get_columns(filters=None):
	return [
	{
	"label": "Ticket no",
	"fieldtype": "Data",
	"fieldname": "ticket",
	'width':90
	},
	{
	"label": "Call assigned by ",
	"fieldtype": "Data",
	"fieldname": "call_assigned",
	'width':90
	},
	{
	"label": "ML - Number",
	"fieldtype": "Data",
	"fieldname": "ml_number",
	'width':90
	},
	{
	"label": "Location",
	"fieldtype": "Data",
	"fieldname": "location",
	'width':90
	},
	{
	"label": "Nature of complaint",
	"fieldtype": "Data",
	"fieldname": "complaint",
	'width':100
	},
	{
	"label": "Serial No",
	"fieldtype": "Data",
	"fieldname": "customer_name",
	'width':100
	},
	{
	"label": "Counter Mono",
	"fieldtype": "Data",
	"fieldname": "customer_group",
	'width':120
	},
	{
	"label": "Counter color",
	"fieldtype": "Data",
	"fieldname": "second_customer_group",
	'width':150
	},
	{
	"label": "Total Counter",
	"fieldtype": "Link",
	"fieldname": "customer",
	"options": "Customer",
	'width':150
	},
	{
	"label": "Time Response",
	"fieldtype": "Data",
	"fieldname":"time_response",
	'width':90
	},
	{
	"label": "Time Resolution",
	"fieldtype": "Data",
	"fieldname": "time_resolution",
	'width':90
	},
	{
	"label": "Time Closed",
	"fieldtype": "Data",
	"fieldname": "Time Close",
	'width':90
	},
	{
	"label": "Total Time consumed",
	"fieldtype": "Data",
	"fieldname": "time_consumed",
	'width':90
	},
	{
	"label": "Same day fix",
	"fieldtype": "Data",
	"fieldname": "same_day",
	'width':90
	},
	{
	"label": "Comment",
	"fieldtype": "Data",
	"fieldname": "comment",
	'width':90
	},
	{
	"label": "Remark",
	"fieldtype": "Data",
	"fieldname": "remark",
	'width':100
	}
]

def prepare_data(filters):
	data=[]
	# for i in frappe.get_all('Issue',fields=['name','']):
		
	return data







