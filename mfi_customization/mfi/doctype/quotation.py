from re import I
import frappe,json

from frappe.utils import data
def validate(doc,method):
	calculation(doc)

def calculation(doc):
	service_charge=0
	for itm in doc.get('items'):
		service_charge+=calculate_service_charge(doc,itm)

	for itm in doc.get('items'):
		itm_rate=get_rate_from_item_price(doc,itm.item_code)
		if doc.order_type=="Per Click" and  (itm.item_code in [d.compatible_with for d in doc.get("compatible_toner_list")] or (itm.item_code in [d.compatible_with for d in doc.get("compatible_accessories_list")])):
			per_click_calculation(doc,itm,itm_rate)
		elif doc.order_type=="Minimum Volume" and (itm.item_code in [d.compatible_with for d in doc.get("compatible_toner_list")] or (itm.item_code in [d.compatible_with for d in doc.get("compatible_accessories_list")])):
			minimum_volume_calculation(doc,itm,service_charge)

def per_click_calculation(doc,itm,itm_rate):
	acc_monorate=0
	acc_colourrate=0
	acc_monoyeild=0
	acc_colouryeild=0
	
	if doc.get("compatible_accessories_list"):
		for acc in doc.get("compatible_accessories_list"):
			accessory_type=frappe.db.get_value("Item",{"name":acc.accessory},"accessory_type")
			if acc.get('compatible_with')==itm.item_code and accessory_type:
				if accessory_type=="Mono":
					acc_monorate+=get_rate_from_item_price(doc,acc.accessory)
					acc_monoyeild+=acc.yeild
				else:
					acc_colourrate+=get_rate_from_item_price(doc,acc.accessory)
					acc_colouryeild+=acc.yeild
	tn_monorate=0
	tn_colourrate=0
	tn_monoyeild=0
	tn_colouryeild=0
	
	if doc.get("compatible_toner_list"):
		for tn in doc.get("compatible_toner_list"):
			toner_type=frappe.db.get_value("Item",{"name":tn.toner},"toner_type")
			if tn.get('compatible_with')==itm.item_code and toner_type:
				if toner_type=="Black":
					tn_monorate+=get_rate_from_item_price(doc,tn.toner)
					tn_monoyeild+=tn.yeild
				else:
					tn_colourrate+=get_rate_from_item_price(doc,tn.toner)
					tn_colouryeild+=tn.yeild
				
	total_cost=(itm_rate+acc_monorate+acc_colourrate)
	if doc.interest_rate and doc.interest_rate>0.0:
		total_cost=((itm_rate+acc_monorate+acc_colourrate)/doc.interest_rate)+(itm_rate+acc_monorate+acc_colourrate)

	monthly_costing=total_cost
	if doc.interest_rate and doc.lease_period>0.0:
		monthly_costing=total_cost/doc.lease_period
		
	itm.net_rent=monthly_costing
	itm.base_rate=monthly_costing+itm.margin_on_rent
	itm.base_net_rate=monthly_costing+itm.margin_on_rent
	itm.base_amount=(monthly_costing+itm.margin_on_rent)*itm.qty
	itm.base_net_amount=monthly_costing+itm.margin_on_rent*itm.qty
	itm.rate=monthly_costing+itm.margin_on_rent
	itm.net_rate=monthly_costing+itm.margin_on_rent
	itm.amount=monthly_costing+itm.margin_on_rent*itm.qty
	itm.net_amount=monthly_costing+itm.margin_on_rent*itm.qty


	#per copy rate
	itm.mono_net_rate_per_click=(acc_monoyeild+tn_monoyeild)/(acc_monorate+tn_monorate)
	itm.colour_net_rate_per_click=(acc_monoyeild+tn_monoyeild+acc_colouryeild+tn_colouryeild)/(acc_monorate+tn_monorate+acc_colourrate+tn_colourrate)
	itm.mono_per_click_rate=(itm.mono_net_rate_per_click+itm.mono_per_click_margin)
	itm.colour_per_click_rate=(itm.colour_net_rate_per_click+itm.colour_per_click_margin)
	
def minimum_volume_calculation(doc,itm,service_charge):
	mono_service_charge=((doc.mono_volume/(doc.mono_volume+doc.colour_volume))*service_charge)
	colour_service_charge=((doc.colour_volume/(doc.mono_volume+doc.colour_volume))*service_charge)
	cost_of_monotoner=0
	cost_of_colourtoner=0
	if doc.get("compatible_toner_list"):
		for tn in doc.get("compatible_toner_list"):
			toner_type=frappe.db.get_value("Item",{"name":tn.toner},"toner_type")
			if tn.get('compatible_with')==itm.item_code and toner_type:
				if toner_type=="Black":
					cost_of_monotoner+=((doc.colour_volume+doc.mono_volume)/tn.yeild)*get_rate_from_item_price(doc,tn.toner)
				else:
					cost_of_colourtoner+=((doc.colour_volume)/tn.yeild)*get_rate_from_item_price(doc,tn.toner)

	cost_of_monoaccessory=0
	cost_of_colouraccessory=0		
	if doc.get("compatible_accessories_list"):
		for acc in doc.get("compatible_accessories_list"):
			accessory_type=frappe.db.get_value("Item",{"name":acc.accessory},"accessory_type")
			if acc.get('compatible_with')==itm.item_code and accessory_type:
				if accessory_type=="Mono":
					cost_of_monoaccessory+=(((doc.colour_volume+doc.mono_volume)/acc.yeild)-1)*get_rate_from_item_price(doc,acc.accessory)
				else:
					cost_of_colouraccessory+=(((doc.colour_volume)/acc.yeild)-1)*get_rate_from_item_price(doc,acc.accessory)

	itm.mono_net_rate_per_click=(cost_of_monotoner+cost_of_monoaccessory+mono_service_charge)/doc.mono_volume
	itm.mono_per_click_rate=(itm.mono_net_rate_per_click+itm.mono_per_click_margin)
	itm.colour_net_rate_per_click=(cost_of_colourtoner+cost_of_colouraccessory+colour_service_charge)/doc.colour_volume
	itm.colour_per_click_rate=(itm.colour_net_rate_per_click+itm.colour_per_click_margin)
	

def get_rate_from_item_price(doc,item):
	dlcpi=frappe.get_value("Default Landed Cost Price Item",{"parent":"MFI Settings","company":doc.company},["price_list"])
	rate=0
	if dlcpi:
		rate=frappe.db.get_value("Item Price",{"item_code":item,"price_list":dlcpi},["price_list_rate"]) or 0
	
	return rate 

def calculate_service_charge(doc,item):
	for sig in frappe.get_all("Service Item Group",{"parent":"MFI Settings","item_group":frappe.db.get_value("Item",{"name":item.item_code},"item_group")},["price_list"]):
		return frappe.db.get_value("Item Price",{"item_code":item.item_code,"price_list":sig.price_list},"price_list_rate") or 0
	return 0

@frappe.whitelist()
def get_accessories_items(item):
	data=[]
	for d in frappe.get_all("Compatible Accessories Item",{"parent":item},["accessory","accessory_name"]):
		data.append(d.update({"yeild":frappe.db.get_value("Item",d.toner,"yeild")}))
	return data

@frappe.whitelist()
def get_toner_items(item):
	data=[]
	for d in frappe.get_all("Compatible Toner Item",{"parent":item},["toner","toner_name"]):
		data.append(d.update({"yeild":frappe.db.get_value("Item",d.toner,"yeild")}))
	return data