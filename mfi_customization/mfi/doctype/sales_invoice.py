import frappe
from frappe.utils import flt,nowdate
from erpnext.stock.get_item_details import get_conversion_factor

def on_submit(doc,method):
    update_machine_reading_status(doc)

@frappe.whitelist()
def get_assets(project,company):
    data1=[]
    data2=[]
    sales_order_doc=""
    mono_per_click_rate=0
    colour_per_click_rate=0
    total_rent=0
    if frappe.db.get_value("Project",{"name":project},"sales_order"):
        sales_order_doc=frappe.get_doc("Sales Order",frappe.db.get_value("Project",{"name":project},"sales_order"))
        total_rent=sales_order_doc.get("total_rent")
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
        machine_reading_current=""
        machine_reading_last=""

        readings=get_reading(row.name)
        if readings:
            mono_current_reading=readings[0].black_and_white_reading
            colour_current_reading=readings[0].colour_reading
            machine_reading_current=readings[0].name

            mono_last_reading=readings[-1].black_and_white_reading
            colour_last_reading=readings[-1].colour_reading
            machine_reading_last=readings[-1].name

        # for i,d in enumerate(get_reading(row.name)):
        #     if i==0:
        #         mono_current_reading=d.black_and_white_reading
        #         colour_current_reading=d.colour_reading

        #     else:
        #         mono_last_reading=d.black_and_white_reading
        #         colour_last_reading=d.colour_reading

        mono_diff=(flt(mono_current_reading)- flt(mono_last_reading))
        colour_diff=(flt(colour_current_reading)-flt(colour_last_reading))
        total_mono_rate=mono_diff
        total_colour_rate=colour_diff*colour_per_click_rate


        #Comapre Reading In Printing Slabs
        mono_not_in_range=True
        colour_not_in_range=True

        if sales_order_doc.get("order_type")=="Minimum Volume":
            for i,ps in enumerate(sales_order_doc.get("printing_slabs")):
                if ps.printer_type=="Mono":
                    if mono_diff>ps.rage_from and mono_diff<ps.range_to:
                        mono_not_in_range=False
                        mono_per_click_rate=ps.rate
                        if ps.rage_from==0 and sales_order_doc.get("order_type")=="Minimum Volume":
                            total_mono_rate=(ps.range_to*ps.rate)
                        
                if ps.printer_type=="Colour":
                    if colour_diff>ps.rage_from and colour_diff<ps.range_to:
                        colour_not_in_range=False
                        colour_per_click_rate=ps.rate
                        if ps.rage_from==0 and sales_order_doc.get("order_type")=="Minimum Volume":
                            total_colour_rate=(ps.range_to*ps.rate)
            print(row.name)
            # Reading Not In Range then get Last slab rate
            if mono_not_in_range:
                for ps in sales_order_doc.get("printing_slabs"):
                    if ps.printer_type=="Mono":
                        mono_per_click_rate=ps.rate
                        total_mono_rate=(mono_diff*ps.rate)
            if colour_not_in_range:
                for ps in sales_order_doc.get("printing_slabs"):
                    if ps.printer_type=="Colour":
                        colour_per_click_rate=ps.rate
                        total_colour_rate=(colour_diff*ps.rate)

        elif sales_order_doc.get("order_type")=="Per Click":
            mono_per_click_rate=sales_order_doc.get("mono_per_click_rate")
            colour_per_click_rate=sales_order_doc.get("colour_per_click_rate")
            
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
                "total_mono_reading":mono_diff,
                "total_colour_reading":colour_diff,
                "total_mono_billing":(total_mono_rate),
                "total_colour_billing":(total_colour_rate),
                "total_rate":(total_mono_rate)+(total_colour_rate),
                "machine_reading_current":machine_reading_current,
                "machine_reading_last":machine_reading_last
            }
        )

    item_details=[]
    for d in frappe.get_all("Rental Contract Item",{"parent":"MFI Settings","company":company},["item"]):
        item=get_item_details(d.item,company)
        item_details.append(item.update(get_conversion_factor(item.item_code, item.stock_uom)))
    return data1,item_details,data2,total_rent

def get_reading(asset):
    return frappe.get_all("Machine Reading",filters={"asset":asset,"reading_type":"Billing","billing_status":""},fields=["name","colour_reading","black_and_white_reading"],order_by="reading_date desc")

def get_item_details(item,company):
    item = frappe.db.sql("""select i.name as item_code, i.stock_uom,i.item_name, i.item_group,i.description,
            i.has_batch_no, i.sample_quantity, i.has_serial_no, i.allow_alternative_item,
            id.expense_account, id.buying_cost_center,id.income_account
        from `tabItem` i LEFT JOIN `tabItem Default` id ON i.name=id.parent and id.company=%s
        where i.name=%s
            and i.disabled=0
            and (i.end_of_life is null or i.end_of_life='0000-00-00' or i.end_of_life > %s)""",
        (company,item, nowdate()), as_dict = 1)
    return item[0] if item else {}

def update_machine_reading_status(doc):
    for ai in doc.get("assets_rates_item"):
        if ai.machine_reading_current:
            mr=frappe.get_doc("Machine Reading",ai.machine_reading_current)
            mr.billing_status="Billed"
            mr.save()
        if ai.machine_reading_last:
            mr=frappe.get_doc("Machine Reading",ai.machine_reading_last)
            mr.billing_status="Billed"
            mr.save()