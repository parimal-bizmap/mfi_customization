import frappe

def validate(doc,method):
    print("**")
    # if doc.is_renting_item==1:
    #     create_item("AST-",doc,1,"Copy Machines")
    #     create_item("RNT-",doc)

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

# @frappe.whitelist()
# def toner_from_mfi_setting(doctype, txt, searchfield, start, page_len, filters):
#     return frappe.get_all("Toner Group List",{"parent":"MFI Setting"},["toner_group"],as_list=1)


@frappe.whitelist()
def toner_from_mfi_setting(name):
    return frappe.get_all("Toner Group List",{"parent":"MFI Setting"},["toner_group"],as_list=1)