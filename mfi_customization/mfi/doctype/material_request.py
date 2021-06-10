import frappe

def validate(doc,method):
	for emp in frappe.get_all("Employee",{"user_id":frappe.session.user},['material_request_approver']):
		if emp.material_request_approver:
			for emp2 in frappe.get_all("Employee",{"name":emp.material_request_approver},['user_id']):
				if emp2.user_id:
					doc.approver=emp2.user_id
					doc.approver_name=frappe.db.get_value("User",emp2.user_id,"full_name")
		if doc.approver and len(frappe.get_all("User Permission",{"for_value":doc.name,"user":doc.approver}))==0 and not doc.get("__islocal"):
			docperm = frappe.new_doc("User Permission")
			docperm.update({
				"user": doc.approver,
				"allow": 'Material Request',
				"for_value": doc.name
			})
			docperm.save(ignore_permissions=True)
	
	
	#User Permission For Approver  
def after_insert(doc,method):
	if doc.approver and len(frappe.get_all("User Permission",{"for_value":doc.name,"user":doc.approver}))==0:
		docperm = frappe.new_doc("User Permission")
		docperm.update({
			"user": doc.approver,
			"allow": 'Material Request',
			"for_value": doc.name
		})
		docperm.save(ignore_permissions=True)

	
