import frappe

def validate(doc,method):
    if doc.is_renting_item==1:
        create_item("AST-",doc,1,"Copy Machines")
        create_item("RNT-",doc)

def create_item(prefix,doc,fixed_asset=0,asset_category=""):
    new_item=frappe.new_doc("Item")
    field_list=frappe.get_meta("Item").get("fields")
    for d in field_list:
        new_item.set(d.fieldname,doc.get(d.fieldname))
    new_item.item_code=prefix+doc.item_code
    new_item.is_renting_item=0
    new_item.is_stock_item=0
    new_item.is_fixed_asset=fixed_asset
    new_item.asset_category=asset_category
    if len(frappe.get_all("Item",{"item_code":prefix+doc.item_code}))==0:
        new_item.save()

@frappe.whitelist()
def toner_from_mfi_setting(doctype, txt, searchfield, start, page_len, filters):
    data=[]
    item_group=[]
    for d in frappe.get_all("Default Toner group Item",{"parent":"MFI Settings"},["toner_group"]):
        item_group.append(d.toner_group)
    for it in frappe.get_all("Item",{"item_group":["IN",item_group]},["name","item_name","description","item_group","customer_code"],as_list=1):
        data.append(it)
    return data

@frappe.whitelist()
def accessory_from_mfi_setting(doctype, txt, searchfield, start, page_len, filters):
    data=[]
    item_group=[]
    for d in frappe.get_all("Default Accessories Item",{"parent":"MFI Settings"},["accessory_group"]):
        item_group.append(d.accessory_group)
    for it in frappe.get_all("Item",{"item_group":["IN",item_group]},["name","item_name","description","item_group","customer_code"],as_list=1):
        data.append(it)
    return data
