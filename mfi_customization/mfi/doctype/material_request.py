import frappe
from frappe.desk.reportview import get_match_cond, get_filters_cond
from frappe.utils import nowdate, getdate, flt
from frappe import msgprint, _
from frappe.model.mapper import get_mapped_doc
 


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


# def update_item(obj, target, source_parent):
#     target.conversion_factor = obj.conversion_factor
#     target.qty = flt(flt(obj.stock_qty) - flt(obj.ordered_qty))/ target.conversion_factor
#     target.stock_qty = (target.qty * target.conversion_factor)
#     if getdate(target.schedule_date) < getdate(nowdate()):
#         target.schedule_date = None

# def set_missing_values(source, target_doc):
#     if target_doc.doctype == "Purchase Order" and getdate(target_doc.schedule_date) <  getdate(nowdate()):
#         target_doc.schedule_date = None
#     target_doc.run_method("set_missing_values")

# @frappe.whitelist()
# def make_purchase_order_based_on_supplier(source_name, target_doc=None, args=None):
#     mr = source_name

#     # supplier_items = get_items_based_on_default_supplier(args.get("supplier"))
#     def select_item(d):
#         return d.ordered_qty < d.stock_qty

#     def postprocess(source, target_doc):
#         # target_doc.supplier = args.get("supplier")
#         if getdate(target_doc.schedule_date) < getdate(nowdate()):
#             target_doc.schedule_date = None
#         print("......target_doc.get('items')",target_doc.get("items"))
#         target_doc.set("items", [d for d in target_doc.get("items")
#              if d.get("qty") > 0])

#         set_missing_values(source, target_doc)

#     target_doc = get_mapped_doc("Material Request", mr, {
#         "Material Request": {
#             "doctype": "Purchase Order",
#         },
#         "Material Request Item": {
#             "doctype": "Purchase Order Item",
#             "field_map": [
#                 ["name", "material_request_item"],
#                 ["parent", "material_request"],
#                 ["uom", "stock_uom"],
#                 ["uom", "uom"]
#             ],
#             # "postprocess": update_item,
#             "condition": select_item
#         }
#     }, target_doc, postprocess)

#     return target_doc

# @frappe.whitelist()
# @frappe.validate_and_sanitize_search_inputs
# def get_material_requests_based_on_supplier(doctype, txt, searchfield, start, page_len, filters):
#     conditions = ""
#     if txt:
#         conditions += "and mr.name like '%%"+txt+"%%' "

#     if filters.get("transaction_date"):
#         date = filters.get("transaction_date")[1]
#         conditions += "and mr.transaction_date between '{0}' and '{1}' ".format(date[0], date[1])

#     # supplier = filters.get("supplier")
#     # supplier_items = get_items_based_on_default_supplier(supplier)
#     supplier_items = []
#     # if not supplier_items:
#     #   frappe.throw(_("{0} is not the default supplier for any items.").format(supplier))

#     material_requests = frappe.db.sql("""select distinct mr.name, transaction_date,company
#         from `tabMaterial Request` mr, `tabMaterial Request Item` mr_item
#         where mr.name = mr_item.parent
            
#             and mr.material_request_type = 'Purchase'
#             and mr.per_ordered < 99.99
#             and mr.docstatus = 1
#             and mr.status != 'Stopped'
#             and mr.company = '{0}'
#             {1}
#         order by mr_item.item_code ASC
#         limit {2} offset {3} """ \
#         .format(filters.get("company"), conditions, page_len, start), as_dict=1)

#     return material_requests

# @frappe.whitelist()
# def get_items_based_on_default_supplier(supplier):
#     supplier_items = [d.parent for d in frappe.db.get_all("Item Default",
#         {"default_supplier": supplier, "parenttype": "Item"}, 'parent')]

#     return supplier_items