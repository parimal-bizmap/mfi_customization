# Copyright (c) 2013, bizmap technologies and contributors
# For license information, please see license.txt
from __future__ import unicode_literals

import frappe


def execute(filters=None):
	columns  = get_column()
	data	 = get_data(filters)
	return columns, data
def get_column(filters = None):
	return[
			{
			"label":"Client Name",
			"fieldname":"client_name",
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
	condition = ""
	fltr={}
	if filters.get('from_date') and filters.get('to_date') :
			fltr.update({'failure_date_and_time':['between',(filters.get('from_date'),filters.get('to_date'))]})
			condition+=" where failure_date_and_time between '{0}' and '{1}'".format(filters.get('from_date'),filters.get('to_date'))
	if filters.get('serial_no'):
			condition+=" and serial_no ='{0}'".format(filters.get('serial_no'))	
	if filters.get('client_name'):
			condition+=" and customer ='{0}'".format(filters.get('client_name'))	
	if filters.get('c_name'):
			condition+=" and company ='{0}'".format(filters.get('c_name'))
	issue_list = frappe.db.sql("""select 
    	    customer as client_name,
        	serial_no,
         	asset_name as machine_model,
			DATE_FORMAT(resolution_date, "%b") as call_date
    	    from 
			`tabIssue` {0} """.format(condition),as_dict=1)
	data=[]
	for d in issue_list:
		fltr.update({'serial_no':d.serial_no})
		data.append(d.update({'calls':len(frappe.get_all("Issue",fltr))}))
	return data



# def get_data(filters):
# 	print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
# 	data = []
# 	fltr_1 = {}
# 	fltr_2 = {}
# 	fltr_3 = {}
# 	s_no = ''
		
# 	if filters:
# 		for i,d in enumerate(filters):
# 			if d=='serial_no':
# 				fltr_1.update({d:filters.get(d)})
# 				print(s_no)
# 			elif d=='from_date':
# 				# fltr_2.update({d:filters.get(d)})
# 				frm_date = filters.get(d)
# 				print(frm_date)
# 			elif d=='to_date':
# 				#fltr_3.update({d:filters.get(d)})
# 				to_date = filters.get(d)
# 				print(to_date)
					
# 			print(i,d)
# 	for ti in frappe.get_all('Issue',fltr_1,['name','subject','customer','issue_type','asset_name','failure_date_and_time','serial_no']):
# 		if ti.failure_date_and_time != None:
# 			call_date = ti.failure_date_and_time.strftime("%d-%m-%Y")
# 			print()
# 			if frm_date <= call_date and call_date <= to_date:
# 				row = {
# 				"call_date":call_date,
# 				"client_name":ti.customer,
# 				"serial_no":ti.serial_no,
# 				"machine_model":ti.asset_name
# 				}
# 				print("$$$$$$$$$$$$$$$$$")
# 				print(ti)


# 			# count = 0
# 			# for s_no in frappe.get_all('Issue',['serial_no']):
# 			# 	if s_no.serial_no == ti.serial_no:
# 			# 		count+=1
# 			# 	row['calls']=count
# 				data.append(row)
# 	return data
	

		
		
		
	
	
	# if filters:
	# 	for i,d in enumerate(filters):
	# 		if i==0:
	# 			condition+="Where pr.{0}='{1}'".format(d,filters.get(d))
	# 			print(d,filters.get(d),condition)
	# 		elif i==1:
	# 			condition+=" and so.{0}='{1}'".format(d,filters.get(d))
	# 			print(print(d,filters.get(d),condition))
	# 		print(i,d)