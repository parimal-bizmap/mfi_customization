import frappe
from datetime import datetime

# bench execute mfi_customization.mfi.patch.set_first_responded_on_issue.execute
def execute():
	for d in frappe.get_all("Issue"):
		issue=frappe.get_doc("Issue",d.name)
		task_data = frappe.db.get_value("Task", {"issue": issue.name}, ['attended_date_time', 'status'], as_dict=1)
		if task_data:	
			if task_data.attended_date_time:
				issue.first_responded_on = task_data.attended_date_time
				issue.save()
			elif issue.status == 'Working' or task_data.get('status') == 'Working' :
				issue.first_responded_on = datetime.now()
				issue.save()
