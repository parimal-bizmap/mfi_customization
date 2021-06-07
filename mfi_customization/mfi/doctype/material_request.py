import frappe

def validate(doc,method):
	for emp in frappe.get_all("Employee",{"user_id":frappe.session.user},['reports_to']):
		if emp.reports_to:
			for emp2 in frappe.get_all("Employee",{"name":emp.reports_to},['user_id']):
				if emp2.user_id:
					doc.approver=emp2.user_id
					doc.approver_name=frappe.db.get_value("User",emp2.user_id,"full_name")
	
	
	#User Permission For Approver   
	if doc.approver and doc.name and not doc.is_new():
		if not len(frappe.get_all("User Permission"),{"for_value":doc.name,"user":doc.approver}):
			docperm = frappe.new_doc("User Permission")
			docperm.update({
				"user": doc.approver,
				"allow": 'Material Request',
				"for_value": doc.name
			})
			docperm.save(ignore_permissions=True)
		
