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
	"label": "Issue",
	"fieldtype": "Link",
	"fieldname": "name",
	"options":"Issue",
	'width':120
	},
	{
	"label": "Status",
	"fieldtype": "Data",
	"fieldname": "status",
	'width':80
	},
	{
	"label": "Issue Type",
	"fieldtype": "Link",
	"fieldname": "issue_type",
	"options":"Issue Type",
	'width':110
	},
	{
	"label": "Description",
	"fieldtype": "Data",
	"fieldname": "description",
	'width':110
	},
	{
	"label": "Failure Date",
	"fieldtype": "Data",
	"fieldname": "failure_date",
	'width':100
	},
	{
	"label": "Opening Date",
	"fieldtype": "Data",
	"fieldname": "opening_date",
	'width':100
	},
	{
	"label": "Opening Time",
	"fieldtype": "Data",
	"fieldname": "opening_time",
	'width':100
	},
	{
	"label": "First Responded On",
	"fieldtype": "Data",
	"fieldname": "first_responded_on",
	'width':120
	},
	{
	"label": "Mins to First Response",
	"fieldtype": "Data",
	"fieldname": "mins_to_first_response",
	'width':150
	},
	{
	"label": "Closing Date",
	"fieldtype": "Data",
	"fieldname": "resolution_date",
	'width':150
	},
	{
	"label": "Time Resolution",
	"fieldtype": "Data",
	"fieldname": "time_resolution",
	'width':150
	},
]

def prepare_data(filters):
	data=[]
	for i in frappe.get_all('Issue',fields=["name","status","issue_type","description","failure_date_and_time","opening_date","opening_time","first_responded_on","mins_to_first_response","resolution_date","time_resolution"]):
		# row={
		# 	"ticket":t.issue,
		# 	"call_assigned":t.completed_by,
		# 	"ml_number":t.asset,
		# 	"location":t.location,
		# 	"complaint":t.issue_type
		# }
		data.append(i)
	return data







