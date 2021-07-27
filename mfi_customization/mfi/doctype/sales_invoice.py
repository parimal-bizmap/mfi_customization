import frappe
from frappe.utils import flt

@frappe.whitelist()
def get_assets(project):
    data1=[]
    data2=[]
    sales_order_doc=""
    mono_per_click_rate=0
    colour_per_click_rate=0
    if frappe.db.get_value("Project",{"name":project},"sales_order"):
        sales_order_doc=frappe.get_doc("Sales Order",frappe.db.get_value("Project",{"name":project},"sales_order"))
        mono_per_click_rate=sales_order_doc.mono_per_click_rate
        colour_per_click_rate=sales_order_doc.colour_per_click_rate
        for d in sales_order_doc.get("printing_slabs"):
            data2.append({
                "range_from":d.rage_from,
                "range_to":d.range_to,
                "printer_type":d.printer_type,
                "rate":d.rate
            })
    for row in frappe.get_all("Asset",{"project":project},["item_code","location","name","serial_no","item_name","asset_name"]):
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
        data1.append(
            {
                "location":row.location,
                "asset":row.name,
                "asset_name":row.asset_name,
                "serial_no":row.serial_no,
                "mono_click_rate":mono_per_click_rate,
                "colour_click_rate":colour_per_click_rate,
                "mono_current_reading":mono_current_reading,
                "mono_last_reading":mono_last_reading,
                "colour_current_reading":colour_current_reading,
                "colour_last_reading":colour_last_reading,
                "total_mono_reading":(flt(mono_current_reading)- flt(mono_last_reading))*mono_per_click_rate,
                "total_colour_reading":(flt(colour_current_reading)-flt(colour_last_reading))*colour_per_click_rate,
                "total_rate":((flt(mono_current_reading) - flt(mono_last_reading))*mono_per_click_rate)+((flt(colour_current_reading)-flt(colour_last_reading))*colour_per_click_rate),
            }
        )
    
    return data1,data2

def get_reading(asset):
    return frappe.get_all("Machine Reading",filters={"asset":asset,"reading_type":"Billing"},fields=["colour_reading","black_and_white_reading"],order_by="reading_date desc",limit=2)