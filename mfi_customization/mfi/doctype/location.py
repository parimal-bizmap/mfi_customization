from __future__ import unicode_literals
import frappe


@frappe.whitelist()
def get_customer(doctype, txt, searchfield, start, page_len, filters):
 	if txt:
 		filters.update({"parent": ("like", "{0}%".format(txt))})
		
 	return frappe.get_all("Party Account",filters=filters,fields = ["parent"], as_list=1)

@frappe.whitelist()
def get_contact(doctype, txt, searchfield, start, page_len, filters):
    fltr={}
    lst=[]
 	
    if txt:
        fltr.update({"parent": ("like", "{0}%".format(txt))})
    if filters.get("customer"):
        fltr.update({"link_name":filters.get("customer")})

    fltr.update({"parenttype":"Contact"})
    for i  in frappe.get_all("Dynamic Link",fltr,["parent"], as_list=0):
        if i.parent not in lst:
            lst.append(i.parent)
    return [(d,) for d in lst]	


@frappe.whitelist()
def get_address(doctype, txt, searchfield, start, page_len, filters):
    fltr={}
    lst=[]
 	
    if txt:
        fltr.update({"parent": ("like", "{0}%".format(txt))})
    if filters.get("customer"):
        fltr.update({"link_name":filters.get("customer")})

    fltr.update({"parenttype":"Address"})
    for i  in frappe.get_all("Dynamic Link",fltr,["parent"], as_list=0):
        if i.parent not in lst:
            lst.append(i.parent)
    return [(d,) for d in lst]	
    

