# Copyright (c) 2013, bizmap technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import date_diff, add_days, getdate


def execute(filters=None):
	columns  = get_columns()
	data	 = get_data(filters)
	return columns, data

def get_columns(filters = None):
	
	return[{
			"label":"Helpdesk",
			"fieldname":"helpdesk",
			"fieldtype":"Data"	

		},{
			"label":"Support Technician Name",
			"fieldname":"support_tech",
			"fieldtype":"Data"	

		},
			{
			"label":"Number of calls",
			"fieldname":"no_of_calls",
			"fieldtype":"Data"	

		},{
			"label":"Average Wait Time (Days)",
			"fieldname":"avg_wait_time",
			"fieldtype":"Data"	

		},{
			"label":"Resolved",
			"fieldname":"resolved",
			"fieldtype":"Data"	

		},{
			"label":"Pending Calls",
			"fieldname":"pending_calls",
			"fieldtype":"Data"	

		},{
			"label":"Productivity Per Day (%)",
			"fieldname":"prod_per_day",
			"fieldtype":"Data"	

		},{
			"label":"Average Time On Call",
			"fieldname":"average_time_on_call",
			"fieldtype":"Data"	

		}

		]


def get_data(filters):
		data = []
		fltr = {}
		fltr2 = {}
		fltr3 = {}
		assign_issue_cnt = 0
		unassign_issue_cnt = 0
		total_issue_cnt = len(frappe.get_all("Issue"))
		if filters.get("support_tech"):
			fltr.update({'email':filters.get("support_tech")})
		if filters.get('from_date') and filters.get('to_date') :
			fltr2.update({'assign_date':['between',(filters.get('from_date'),filters.get('to_date'))]})
		if filters.get("c_name"):
			fltr3.update({'company':filters.get("c_name")})
			fltr2.update({'company':filters.get("c_name")})

		for i in frappe.get_all('Issue',fltr3,['name','customer']):	
			for tk in frappe.get_all('Task',{'issue':i.get("name")},['completed_by','assign_date','attended_date_time']):
				assign_issue_cnt+=1
								

		
		unassign_issue_cnt = total_issue_cnt - assign_issue_cnt

		
		data.append({'helpdesk': unassign_issue_cnt})		
		
	
		for usr in frappe.get_all("User",fltr,["first_name","last_name","email"]):
				row = {}
				cnt = 0
				avg_wt = 0
				avg_wait_time = 0
				resolved_call_cnt = 0
				total_calls_cnt = 0
				pending_calls_cnt = 0
				on_call_cnt = 0
				avg_on_call_cnt = 0
				avg_time_on_call = 0
				prod_per_day = 0
				fltr2.update({"completed_by":usr.get("email")})
				no_of_day_productivity = date_diff(filters.get("to_date"),filters.get("from_date"))
				

				for tk2 in frappe.get_all('Task',fltr2,['completed_by','assign_date','attended_date_time','status','completion_date_time']):
					total_calls_cnt += 1 
					if tk2.get("attended_date_time") and tk2.get("assign_date"):
						cnt += 1
						avg_wt +=  date_diff(tk2.get("attended_date_time"), tk2.get("assign_date"))
					if tk2.get("completion_date_time") and tk2.get("assign_date"):
						on_call_cnt += 1
						avg_on_call_cnt +=  date_diff(tk2.get("completion_date_time"), tk2.get("assign_date"))
					if tk2.get("status") == 'Completed':
						resolved_call_cnt += 1
					if tk2.get("status") in ['Open','Pending Review','Overdue','Working']:
						pending_calls_cnt += 1
				
				if no_of_day_productivity != 0:
					prod_per_day = round(((resolved_call_cnt/no_of_day_productivity) * 100),2)
					
				if cnt != 0:
		 			avg_wait_time = (avg_wt/cnt)
				if on_call_cnt != 0:
					avg_time_on_call = (avg_on_call_cnt/on_call_cnt)
				
				row.update({
					'no_of_calls':total_calls_cnt,
					'support_tech': usr.get("first_name"),
					'avg_wait_time': avg_wait_time,
					'resolved': resolved_call_cnt,
					'pending_calls': pending_calls_cnt,
					'prod_per_day': prod_per_day,
					'average_time_on_call': avg_time_on_call

				})
				
				if len(frappe.get_all("Task",{'completed_by':usr.email})) > 0:
					data.append(row)
		
		return data



		# for usr in frappe.get_all('User',)
		# for usr in frappe.get_all("User",fltr,["first_name","last_name","email"]):
		# 		# no_calls= len(frappe.get_all("Task",{"completed_by":usr.get("email")}))
		# 		avg_wait_time = 0
		# 		avg_wt = 0
		# 		cnt = 0
		# 		for tk in frappe.get_all('Task',{"completed_by":usr.get("email")},["completed_by","assign_date","attended_date_time"]):
		# 			if tk.get("attended_date_time") and tk.get("assign_date"):
		# 				print(tk.get("attended_date_time"))
		# 				print(tk.get("assign_date"))
		# 				cnt += 1
		# 				avg_wt +=  date_diff(tk.get("attended_date_time"), tk.get("assign_date"))
		# 				print(str(avg_wt)+"avgwt")
		# 		print(cnt)	
		# 		if cnt != 0:
		# 			avg_wait_time = (avg_wt/cnt)

		# 		data.append({
		# 				'no_of_calls':cnt,
		# 				'support_tech': usr.get("first_name"),
		# 				'avg_wait_time': avg_wait_time,
		# 				'email':usr.get("email")

		# 		})



	
		# for tk in frappe.get_all('Task',fltr,["completed_by","assign_date","attended_date_time"]):
		# 	for usr in frappe.get_all("User",{"email":tk.get("completed_by")},["first_name","last_name","email"]):
		# 		no_calls= len(frappe.get_all("Task",{"completed_by":usr.get("email")}))
		# 		avg_wait_time =  date_diff(tk.get("attended_date_time"), tk.get("assign_date"))
		# 		print(avg_wait_time)
		# 		data.append({
		# 				'no_of_calls':no_calls,
		# 				'support_tech': usr.get("first_name"),
		# 				'avg_wait_time':avg_wait_time,
		# 				'email':usr.get("email")

		# 		})