import frappe
from frappe.utils import flt

def after_insert(doc,method):
    if frappe.db.exists('Asset Serial No', doc.serial_no):
        frappe.throw("serial number already exist")
        
    asn = frappe.new_doc('Asset Serial No')
    asn.subject = doc.serial_no
    asn.serial_no = doc.serial_no
    asn.asset = doc.name
    asn.location = doc.location
    asn.save()

def on_cancel(doc,method):
    #removing serial number on serial number
	frappe.db.delete('Asset Serial No', {'name':doc.serial_no})
    
    
def on_update(doc, method):
    #updating location in Serial No doctype with Asset location change.
 	frappe.db.set_value('Asset Serial No',doc.serial_no,'location',doc.location)


@frappe.whitelist()
def get_assets(project):
    data=[]
    sales_order_doc=""
    mono_per_click_rate=0
    colour_per_click_rate=0
    if frappe.db.get_value("Project",{"name":project},"sales_order"):
        sales_order_doc=frappe.get_doc("Sales Order",frappe.db.get_value("Project",{"name":project},"sales_order"))
        mono_per_click_rate=sales_order_doc.mono_per_click_rate
        colour_per_click_rate=sales_order_doc.colour_per_click_rate
    for row in frappe.get_all("Asset",{"project":project},["item_code","location","name","serial_no","item_name"]):
        mono_current_reading=0
        colour_current_reading=0
        mono_last_reading=0
        colour_last_reading=0
        for i,d in enumerate(get_reading(row.name)):
            if i==0:
                mono_current_reading=d.black_and_white_reading
                colour_current_reading=d.colour_reading

            else:
                mono_last_reading=d.black_and_white_reading
                colour_last_reading=d.colour_reading
        data.append(
            {
                "item_code":row.item_code,
                "location":row.location,
                "name":row.name,
                "serial_no":row.serial_no,
                "item_name":row.item_name,
                "mono_per_click_rate":mono_per_click_rate,
                "colour_per_click_rate":colour_per_click_rate,
                "monocurrent_reading":mono_current_reading,
                "mono_last_reading":mono_last_reading,
                "colour_current_reading":colour_current_reading,
                "colour_last_reading":colour_last_reading,
                "total_mono_charges":(flt(mono_current_reading)- flt(mono_last_reading))*mono_per_click_rate,
                "total_colourcharges":(flt(colour_current_reading)-flt(colour_last_reading))*colour_per_click_rate,
                "rate":((flt(mono_current_reading) - flt(mono_last_reading))*mono_per_click_rate)+((flt(colour_current_reading)-flt(colour_last_reading))*colour_per_click_rate)
            }
        )
    
    return data

def get_reading(asset):
    return frappe.get_all("Machine Reading",filters={"asset":asset,"reading_type":"Billing"},fields=["colour_reading","black_and_white_reading"],limit=2)
