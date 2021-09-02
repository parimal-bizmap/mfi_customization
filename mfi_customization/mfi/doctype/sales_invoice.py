import frappe
from frappe.utils import flt,nowdate
from erpnext.stock.get_item_details import get_conversion_factor

def on_submit(doc,method):
	update_machine_reading_status(doc)

def on_cancel(doc,method):
	cancel_billing_machine_reading_status(doc)

@frappe.whitelist()
def get_assets(project,company):
	data1=[]
	data2=[]
	sales_order_doc=""
	mono_per_click_rate=0
	colour_per_click_rate=0
	total_rent=0
	total_mono_reading_diff=0
	total_colour_reading_diff=0
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

		mono_diff=(flt(mono_current_reading)- flt(mono_last_reading))
		colour_diff=(flt(colour_current_reading)-flt(colour_last_reading))
		total_mono_rate=mono_diff
		total_colour_rate=colour_diff*colour_per_click_rate

		total_mono_reading_diff+=mono_diff
		total_colour_reading_diff+=colour_diff
			
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

	
	if sales_order_doc.get("mono_per_click_rate")>0:
		for d in frappe.get_all("Mono Billing Item",{"parent":"MFI Settings","company":company,'parentfield': 'mono_billing_item'},["item"]):
			mono_slabs=[ps for ps in sales_order_doc.get("printing_slabs") if ps.printer_type=="Mono"]
			if sales_order_doc.get("order_type")=="Minimum Volume":
				updated_diff=total_mono_reading_diff
				not_in_first_slab=True
				for i,ps in enumerate(mono_slabs):
					item=get_item_details(d.item,company)
					if ps.range_from==0 and total_mono_reading_diff<=ps.range_to:
						not_in_first_slab=False
					if not_in_first_slab:
						if updated_diff!=0:
							if i==0:
								slab_diff=ps.range_to
							else:
								slab_diff=ps.range_to-((mono_slabs[0]).range_to)

							if updated_diff>=slab_diff:
								updated_diff-=slab_diff
								qty=slab_diff
							else:
								qty=updated_diff
							item.update({
								"actual_quantity":qty,
								"qty":qty,
								"rate":ps.rate,
								"amount":flt(qty*ps.rate),
								"uom":item.stock_uom,
								"description":"{0} Billing of Slab Range From {1} To {2}".format(ps.printer_type,ps.range_from,ps.range_to)
							})
							item_details.append(item.update(get_conversion_factor(item.item_code, item.stock_uom)))
					else:
						item.update({
								"actual_quantity":total_mono_reading_diff,
								"qty":ps.range_to,
								"rate":ps.rate,
								"amount":flt(ps.range_to*ps.rate),
								"uom":item.stock_uom,
								"description":"{0} Billing of Slab Range From {1} To {2}".format(ps.printer_type,ps.range_from,ps.range_to)
							})
						item_details.append(item.update(get_conversion_factor(item.item_code, item.stock_uom)))
							
			
			elif sales_order_doc.get("order_type")=="Per Click":
				item=get_item_details(d.item,company)
				mono_per_click_rate=sales_order_doc.get("mono_per_click_rate")
				item.update(
								{
									"actual_quantity":total_mono_reading_diff,
									"rate":mono_per_click_rate,
									"amount":total_mono_reading_diff*mono_per_click_rate,
									"uom":item.stock_uom,
									"qty":total_mono_reading_diff,
								}
							)
				item_details.append(item.update(get_conversion_factor(item.item_code, item.stock_uom)))

	if sales_order_doc.get("colour_per_click_rate")>0:
		for d in frappe.get_all("Colour Billing Item",{"parent":"MFI Settings","company":company},["item"]):
			colour_slabs=[ps for ps in sales_order_doc.get("printing_slabs") if ps.printer_type=="Colour"]
			if sales_order_doc.get("order_type")=="Minimum Volume":
				updated_diff=total_colour_reading_diff
				not_in_first_slab=True
				for i,ps in enumerate(colour_slabs):
					item=get_item_details(d.item,company)
					if ps.range_from==0 and total_colour_reading_diff<=ps.range_to:
						not_in_first_slab=False
					if not_in_first_slab:
						if updated_diff!=0:
							if i==0:
								slab_diff=ps.range_to
							else:
								slab_diff=ps.range_to-((colour_slabs[0]).range_to)

							if updated_diff>=slab_diff:
								updated_diff-=slab_diff
								qty=slab_diff
							else:
								qty=updated_diff
							item.update({
								"actual_quantity":qty,
								"qty":qty,
								"rate":ps.rate,
								"amount":flt(qty*ps.rate),
								"uom":item.stock_uom,
								"description":"{0} Billing of Slab Range From {1} To {2}".format(ps.printer_type,ps.range_from,ps.range_to)
							})
							item_details.append(item.update(get_conversion_factor(item.item_code, item.stock_uom)))
					else:
						item.update({
								"actual_quantity":total_colour_reading_diff,
								"qty":ps.range_to,
								"rate":ps.rate,
								"amount":flt(ps.range_to*ps.rate),
								"uom":item.stock_uom,
								"description":"{0} Billing of Slab Range From {1} To  {2}".format(ps.printer_type,ps.range_from,ps.range_to)
							})
						item_details.append(item.update(get_conversion_factor(item.item_code, item.stock_uom)))
							
			
			elif sales_order_doc.get("order_type")=="Per Click":
				colour_per_click_rate=sales_order_doc.get("colour_per_click_rate")
				item=get_item_details(d.item,company)
				item.update(
								{
									"actual_quantity":total_colour_reading_diff,
									"rate":colour_per_click_rate,
									"amount":total_colour_reading_diff*colour_current_reading,
									"uom":item.stock_uom,
									"qty":total_colour_reading_diff
								}
							)
				item_details.append(item.update(get_conversion_factor(item.item_code, item.stock_uom)))

	if sales_order_doc.get("order_type")=="Per Click":
		for d in frappe.get_all("Rental Contract Item",{"parent":"MFI Settings","company":company},["item"]):
			item=get_item_details(d.item,company)
			item.update(
							{
								"rate":total_rent,
								"amount":total_rent*1,
								"uom":item.stock_uom,
								"qty":1
							}
						)
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
		if ai.machine_reading_last:
			mr=frappe.get_doc("Machine Reading",ai.machine_reading_last)
			mr.billing_status="Billed"
			mr.save()

def cancel_billing_machine_reading_status(doc):
	for ai in doc.get("assets_rates_item"):
		if ai.machine_reading_last:
			mr=frappe.get_doc("Machine Reading",ai.machine_reading_last)
			mr.billing_status=""
			mr.save()

# def get_mono_rate_calculation(sales_order_doc,diff):
# 	mono_not_in_range=True
# 	mono_per_click_rate=0
# 	total_mono_rate=0
# 	qty=0
# 	for i,ps in enumerate(sales_order_doc.get("printing_slabs")):
# 		if ps.printer_type=="Mono":
# 			if diff>ps.range_from and diff<ps.range_to:
# 				mono_not_in_range=False
# 				mono_per_click_rate=ps.rate
# 				if ps.range_from==0:
# 					total_mono_rate=(ps.range_to*ps.rate)

# 	# Reading Not In Range then get Last slab rate
# 	if mono_not_in_range:
# 		for ps in sales_order_doc.get("printing_slabs"):
# 			if ps.printer_type=="Mono":
# 				mono_per_click_rate=ps.rate
# 				total_mono_rate=(diff*ps.rate)

# 	return mono_per_click_rate,total_mono_rate

# def get_colour_rate_calculation(sales_order_doc,diff):
# 	colour_not_in_range=True
# 	colour_per_click_rate=0
# 	total_colour_rate=0
# 	if sales_order_doc.get("order_type")=="Minimum Volume":
# 		for i,ps in enumerate(sales_order_doc.get("printing_slabs")):     
# 			if ps.printer_type=="Colour":
# 				if diff>ps.range_from and diff<ps.range_to:
# 					colour_not_in_range=False
# 					colour_per_click_rate=ps.rate
# 					if ps.range_from==0 and sales_order_doc.get("order_type")=="Minimum Volume":
# 						total_colour_rate=(ps.range_to*ps.rate)
	
# 		# Reading Not In Range then get Last slab rate
# 		if colour_not_in_range:
# 			for ps in sales_order_doc.get("printing_slabs"):
# 				if ps.printer_type=="Colour":
# 					colour_per_click_rate=ps.rate
# 					total_colour_rate=(diff*ps.rate)

# 	elif sales_order_doc.get("order_type")=="Per Click":
# 		colour_per_click_rate=sales_order_doc.get("colour_per_click_rate")
# 		total_colour_rate=(diff*colour_per_click_rate)
	
# 	return colour_per_click_rate,total_colour_rate