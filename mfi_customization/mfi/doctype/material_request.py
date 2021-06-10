import frappe

def validate(doc,method):
	for emp in frappe.get_all("Employee",{"user_id":frappe.session.user},['material_request_approver']):
		if emp.material_request_approver:
			for emp2 in frappe.get_all("Employee",{"name":emp.material_request_approver},['user_id']):
				if emp2.user_id:
					doc.approver=emp2.user_id
					doc.approver_name=frappe.db.get_value("User",emp2.user_id,"full_name")
	# if doc.approver and not doc.get("__islocal"):
	# 	docperm = frappe.new_doc("User Permission")
	# 	docperm.update({
	# 		"user": doc.approver,
	# 		"allow": 'Material Request',
	# 		"for_value": doc.name
	# 	})
	# 	docperm.save(ignore_permissions=True)
	# if doc.approver and not doc.get("__islocal"):
	# 	docperm = frappe.new_doc("DocShare")
	# 	docperm.update({
    #             "user": doc.approver,
    #             "share_doctype": 'Material Request',
    #             "share_name": doc.name ,
    #             "read": 1,
    #             "write": 1
    #         })
	# 	docperm.save(ignore_permissions=True)
	if doc.approver and not doc.is_new():
		docperm = frappe.new_doc("DocShare")
		docperm.update({
                "user": doc.approver,
                "share_doctype": 'Material Request',
                "share_name": doc.name ,
                "read": 1,
                "write": 1
            })
		docperm.save(ignore_permissions=True)

	#User Permission For Approver  
def after_insert(doc,method):
	
	# if doc.approver :
	# 	docperm = frappe.new_doc("User Permission")
	# 	docperm.update({
	# 		"user": doc.approver,
	# 		"allow": 'Material Request',
	# 		"for_value": doc.name
	# 	})
	# 	docperm.save(ignore_permissions=True)
	if doc.approver and doc.is_new():
		docperm = frappe.new_doc("DocShare")
		docperm.update({
                "user": doc.approver,
                "share_doctype": 'Material Request',
                "share_name": doc.name ,
                "read": 1,
                "write": 1
            })
		docperm.save(ignore_permissions=True)

@frappe.whitelist()
def get_approver(user):
	var = ""
	for emp in frappe.get_all("Employee",{"user_id":user},['material_request_approver']):
		if emp.material_request_approver:
		
			for emp2 in frappe.get_all("Employee",{"name":emp.material_request_approver},['user_id']):
				if emp2.user_id:
					var = emp2.user_id
					
	return var
@frappe.whitelist()
def get_approver_name(user):

	return frappe.db.get_value("User",{"email":user},"full_name")
					

