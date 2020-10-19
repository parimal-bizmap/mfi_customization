# Copyright (c) 2013, bizmap technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate

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
	"fieldname": "failure_date_and_time",
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
	from datetime import datetime as dt
	for i in frappe.get_all('Issue',fields=["name","status","issue_type","description","failure_date_and_time","opening_date","opening_time","first_responded_on","resolution_date"]):
		import datetime
		t = i.resolution_date
		if i.resolution_date:
			days=0
			if getdate(t)==getdate(i.opening_date):
				time_resolution=datetime.timedelta(hours=int(t.strftime('%H')),minutes=int(t.strftime('%M')), seconds=int(t.strftime('%S')))-i.opening_time
				totsec = time_resolution.total_seconds()
				h = totsec//3600
				m = (totsec%3600) // 60
				sec =(totsec%3600)%60 
				i.update({'time_resolution':"D:%d  H: %d M: %d S: %d" %(days,h,m,sec)})
			else:
				days=(getdate(t)-getdate(i.opening_date)).days
				close=datetime.timedelta(hours=int(t.strftime('%H')),minutes=int(t.strftime('%M')), seconds=int(t.strftime('%S')))
				time_resolution=i.opening_time-close
				if close>i.opening_time:
					time_resolution=close-i.opening_time
				totsec = time_resolution.total_seconds()
				h = totsec//3600
				m = (totsec%3600) // 60
				sec =(totsec%3600)%60 
				i.update({'time_resolution':"D:%d  H: %d M: %d S: %d" %(days,h,m,sec)})
		data.append(i)
	return data







