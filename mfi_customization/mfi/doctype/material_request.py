import frappe
from frappe.desk.reportview import get_match_cond, get_filters_cond
from frappe.utils import nowdate, getdate, flt
from frappe import msgprint, _
from frappe.model.mapper import get_mapped_doc
import json


def validate(doc,method):
    for emp in frappe.get_all("Employee",{"user_id":frappe.session.user},['material_request_approver']):
        if emp.material_request_approver:
            for emp2 in frappe.get_all("Employee",{"name":emp.material_request_approver},['user_id']):
                if emp2.user_id:
                    doc.approver=emp2.user_id
                    doc.approver_name=frappe.db.get_value("User",emp2.user_id,"full_name")
    # if doc.approver and not doc.get("__islocal"):
    #   docperm = frappe.new_doc("User Permission")
    #   docperm.update({
    #       "user": doc.approver,
    #       "allow": 'Material Request',
    #       "for_value": doc.name
    #   })
    #   docperm.save(ignore_permissions=True)
    # if doc.approver and not doc.get("__islocal"):
    #   docperm = frappe.new_doc("DocShare")
    #   docperm.update({
    #             "user": doc.approver,
    #             "share_doctype": 'Material Request',
    #             "share_name": doc.name ,
    #             "read": 1,
    #             "write": 1
    #         })
    #   docperm.save(ignore_permissions=True)
    # if doc.approver and not doc.is_new():
    #   docperm = frappe.new_doc("DocShare")
    #   docperm.update({
    #             "user": doc.approver,
    #             "share_doctype": 'Material Request',
    #             "share_name": doc.name ,
    #             "read": 1,
    #             "write": 1
    #         })
    #   docperm.save(ignore_permissions=True)

    #User Permission For Approver  
# def after_insert(doc,method):
    
    # if doc.approver :
    #   docperm = frappe.new_doc("User Permission")
    #   docperm.update({
    #       "user": doc.approver,
    #       "allow": 'Material Request',
    #       "for_value": doc.name
    #   })
    #   docperm.save(ignore_permissions=True)
    # if doc.approver and doc.is_new():
    # docperm = frappe.new_doc("DocShare")
    # docperm.update({
    #       "user": doc.approver,
    #       "share_doctype": 'Material Request',
    #       "share_name": doc.name ,
    #       "read": 1,
    #       "write": 1
    #   })
    # docperm.save(ignore_permissions=True)

@frappe.whitelist()
def get_approver(user):
    id = ""
    approver_name=""
    for emp in frappe.get_all("Employee",{"user_id":user},['material_request_approver']):
        if emp.material_request_approver:
            for emp2 in frappe.get_all("Employee",{"name":emp.material_request_approver},['user_id']):
                if emp2.user_id:
                    id = emp2.user_id
                    approver_name=frappe.db.get_value("User",emp2.user_id,"full_name")
                    
    return {"approver":id,"approver_name":approver_name}
    
@frappe.whitelist()
def get_approver_name(user):

    return frappe.db.get_value("User",{"email":user},"full_name")


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def item_query(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
    conditions = []

    #Get searchfields from meta and use in Item Link field query
    meta = frappe.get_meta("Item", cached=True)
    searchfields = meta.get_search_fields()

    if "description" in searchfields:
        searchfields.remove("description")

    columns = ''
    extra_searchfields = [field for field in searchfields
        if not field in ["name", "item_group", "description"]]

    if extra_searchfields:
        columns = ", " + ", ".join(extra_searchfields)

    searchfields = searchfields + [field for field in[searchfield or "name", "item_code", "item_group", "item_name"]
        if not field in searchfields]
    searchfields = " or ".join([field + " like %(txt)s" for field in searchfields])
    item_group_list=''
    if filters.get("item_group"):
        item_group_list=",".join(['"'+d.name+'"' for d in frappe.get_all("Item Group",{"parent_item_group":filters.get("item_group")})])
    custom_condition=''
    if item_group_list:
        custom_condition=(" and `tabItem`.item_group IN ("+item_group_list+")")

    description_cond = ''
    if frappe.db.count('Item', cache=True) < 50000:
        # scan description only if items are less than 50000
        description_cond = 'or tabItem.description LIKE %(txt)s'

    return frappe.db.sql("""select tabItem.name,
        if(length(tabItem.item_name) > 40,
            concat(substr(tabItem.item_name, 1, 40), "..."), item_name) as item_name,
        tabItem.item_group,
        if(length(tabItem.description) > 40, \
            concat(substr(tabItem.description, 1, 40), "..."), description) as description
        {columns}
        from tabItem
        where tabItem.docstatus < 2
            and tabItem.has_variants=0
            and tabItem.disabled=0
            and (tabItem.end_of_life > %(today)s or ifnull(tabItem.end_of_life, '0000-00-00')='0000-00-00')
            and ({scond} or tabItem.item_code IN (select parent from `tabItem Barcode` where barcode LIKE %(txt)s)
                {description_cond})
             {mcond} {custom_condition}
        order by
            if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
            if(locate(%(_txt)s, item_name), locate(%(_txt)s, item_name), 99999),
            idx desc,
            name, item_name
        limit %(start)s, %(page_len)s """.format(
            columns=columns,
            scond=searchfields,
            mcond=get_match_cond(doctype).replace('%', '%%'),
            custom_condition=custom_condition,
            description_cond = description_cond),
            {
                "today": nowdate(),
                "txt": "%%%s%%" % txt,
                "_txt": txt.replace("%", ""),
                "start": start,
                "page_len": page_len
            }, as_dict=as_dict)


def set_item_from_material_req(doc,method):
    if doc.get('task_') and doc.status=="Issued":
        task=frappe.get_doc('Task',doc.get('task_'))
        items=[]
        for t in task.get('refilled__items'):
            items.append(t.item)
        for d in doc.get('items'):
            if d.get('item_code') not in items:
                task.append("refilled__items", {
                            "item": d.get('item_code'),
                            "warehouse": d.get('warehouse'),
                            "qty": d.get('qty')
                        })
        task.material_request=doc.name
        task.save()   


@frappe.whitelist() 
def get_material_request():
    print("@@@@@@@func")
    fields = ['name', 'schedule_date', 'status']
    MR_list = frappe.db.get_all("Material Request", filters={'docstatus': 1}, fields=fields)
    print("///////MR_list", MR_list)
    return MR_list

@frappe.whitelist() 
def make_po(doc, checked_values):
    checked_values = json.loads(checked_values)
    doc = json.loads(doc)
    print("########## checked_values", checked_values)
    for mr in checked_values:
        mr_doc = frappe.get_all('Material Request', mr.get('name'))
        for ship_item in mr_doc.item_shipment:
            print("/////// ship_item",ship_item)
            if ship_item.get('price_list') and frappe.db.get_value("Price List",{'name': ship_item.get('price_list')}, 'default_supplier')=='MFI INTERNATIONAL':
                


        

