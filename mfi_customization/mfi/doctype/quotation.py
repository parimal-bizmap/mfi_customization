from re import I
import frappe,json,numpy
import numpy_financial as npf

from frappe.utils import data
def validate(doc,method):
	calculation(doc)
	set_parent_values(doc)

def calculation(doc):
	service_charge=0
	for itm in doc.get('asset_quotation_selection'):
		# service_charge+=calculate_service_charge(doc,itm)
		service_charge+=itm.rate

	total_mono_per_click=0
	total_colour_per_click=0
	for itm in doc.get('asset_quotation_selection'):
		itm_rate=get_rate_from_item_price(doc,itm.asset)
		if doc.order_type=="Per Click" and  (itm.asset in [d.compatible_with for d in doc.get("compatible_toner_list")] or (itm.asset in [d.compatible_with for d in doc.get("compatible_accessories_list")])):
			per_click_calculation(doc,itm,itm_rate)
		elif doc.order_type=="Minimum Volume" and (itm.asset in [d.compatible_with for d in doc.get("compatible_toner_list")] or (itm.asset in [d.compatible_with for d in doc.get("compatible_accessories_list")])):
			minimum_volume_calculation(doc,itm,service_charge,itm_rate)
		total_mono_per_click+=itm.mono_net_rate_per_click
		total_colour_per_click+=itm.colour_net_rate_per_click

	doc.mono_per_click_net_rate=total_mono_per_click
	doc.mono_per_click_rate=(doc.mono_per_click_net_rate+(doc.margin_on_mono_per_click_rate_ or 0 ))

	doc.colour_per_click__net_rate_=total_colour_per_click
	doc.colour_per_click_rate=(doc.colour_per_click__net_rate_+(doc.margin_on_colour_per_click_ or 0))


def per_click_calculation(doc,itm,itm_rate):
	acc_monorate=0
	acc_colourrate=0
	acc_monoyeild=0
	acc_colouryeild=0
	
	if doc.get("compatible_accessories_list"):
		for acc in doc.get("compatible_accessories_list"):
			accessory_type=frappe.db.get_value("Item",{"name":acc.accessory},"accessory_type")
			if acc.get('compatible_with')==itm.asset and accessory_type:
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
			if tn.get('compatible_with')==itm.asset and toner_type:
				if toner_type=="Black":
					tn_monorate+=get_rate_from_item_price(doc,tn.toner)
					tn_monoyeild+=tn.yeild
				else:
					tn_colourrate+=get_rate_from_item_price(doc,tn.toner)
					tn_colouryeild+=tn.yeild
	total_cost=(itm_rate+acc_monorate+acc_colourrate)
	# P = ((220000 * (0.0475/12)) / (1 - ((1 + (0.0475/12))^(-1 * 30 * 12))))
	# P =  (  Pv   *     R      ) / (1 - ( 1 +       R    )^(     -n     )
	insurance=total_cost*(doc.insurance/100)

	# google
	interest=((total_cost*doc.interest_rate) / (1 - (pow((1 + doc.interest_rate), (-1 * doc.lease_period)))))

	
	"""	numpy.pmt(rate, nper, pv, fv, when = ‘end’)	
	Parameters :
	rate : [scalar or (M, )array] Rate of interest as decimal (not per cent) per period
	nper : [scalar or (M, )array] total compounding periods
	fv : [scalar or (M, )array] Future value
	pv : [scalar or (M, )array] present value
	when : at the beginning (when = {‘begin’, 1}) or the end (when = {‘end’, 0}) of each period.Default is {‘end’, 0}"""

	# interest=numpy.pmt(doc.interest_rate,doc.lease_period,total_cost,000)


	print("*********************Interest************************")
	print(interest)
	# total contract cost = totalcost + total insurance + total interest

	# total contract with contingency = total contract cost % contingency value

	# NET rent of item = total contract with contingency / LP
	total_contract_cost=total_cost+insurance+interest
	total_contract_with_contingency = total_contract_cost * (doc.contingency/100)
	itm.net_rent=total_contract_with_contingency/doc.lease_period

	# total_cost=(itm_rate+acc_monorate+acc_colourrate)++(itm_rate*(doc.contingency/100))

	# if doc.interest_rate and doc.interest_rate>0.0:
	# 	total_cost=((itm_rate+acc_monorate+acc_colourrate)/doc.interest_rate)+(itm_rate+acc_monorate+acc_colourrate)

		
	# itm.net_rent=monthly_costing
	itm.base_rate=itm.net_rent+itm.margin_on_rent
	itm.base_net_rate=itm.net_rent+itm.margin_on_rent
	itm.base_amount=(itm.net_rent+itm.margin_on_rent)*itm.qty
	itm.base_net_amount=itm.net_rent+itm.margin_on_rent*itm.qty
	itm.rate=itm.net_rent+itm.margin_on_rent
	itm.net_rate=itm.net_rent+itm.margin_on_rent
	itm.amount=itm.net_rent+itm.margin_on_rent*itm.qty
	itm.net_amount=itm.net_rent+itm.margin_on_rent*itm.qty


	#per copy rate
	itm.mono_net_rate_per_click=(acc_monorate+tn_monorate)/(acc_monoyeild+tn_monoyeild)
	itm.colour_net_rate_per_click=(acc_monorate+tn_monorate+acc_colourrate+tn_colourrate)/(acc_monoyeild+tn_monoyeild+acc_colouryeild+tn_colouryeild)
	# itm.mono_per_click_rate=(itm.mono_net_rate_per_click+itm.mono_per_click_margin)
	# itm.colour_per_click_rate=(itm.colour_net_rate_per_click+itm.colour_per_click_margin)
	
def minimum_volume_calculation(doc,itm,service_charge,itm_rate):
	# itm_rate=get_rate_from_item_price(doc,itm.item_code)
	mono=doc.mono_volume*doc.lease_period
	colour=doc.colour_volume*doc.lease_period
	mono_service_charge=((mono/(mono+colour))*service_charge)
	colour_service_charge=((colour/(mono+colour))*service_charge)
	cost_of_monotoner=0
	cost_of_colourtoner=0
	if doc.get("compatible_toner_list"):
		for tn in doc.get("compatible_toner_list"):
			toner_type=frappe.db.get_value("Item",{"name":tn.toner},"toner_type")
			if tn.get('compatible_with')==itm.asset and toner_type:
				if toner_type=="Black":
					cost_of_monotoner+=((colour+mono)/tn.yeild)*get_rate_from_item_price(doc,tn.toner) if ((colour+mono)/tn.yeild)>0 else 0
					cost_of_monotoner+=((colour+mono)/tn.yeild)*get_rate_from_item_price(doc,tn.toner) if ((colour+mono)/tn.yeild)>0 else 0
				else:
					cost_of_colourtoner+=((colour)/tn.yeild)*get_rate_from_item_price(doc,tn.toner) if ((colour)/tn.yeild)>0 else 0

	cost_of_monoaccessory=0
	cost_of_colouraccessory=0		
	cost_of_accessory=0
	if doc.get("compatible_accessories_list"):
		for acc in doc.get("compatible_accessories_list"):
			accessory_type=frappe.db.get_value("Item",{"name":acc.accessory},"accessory_type")
			landed_cost_if_not_yeild=0
			if acc.get('compatible_with')==itm.asset and accessory_type:
				if acc.yeild<1:
					landed_cost_if_not_yeild+=get_rate_from_item_price(doc,acc.accessory)
				if accessory_type=="Mono":
					cost_of_monoaccessory+=(((colour+mono)/acc.yeild)-1)*get_rate_from_item_price(doc,acc.accessory) if (((colour+mono)/acc.yeild)-1)>0 else 0
					if frappe.db.get_value("Item",{"name":acc.accessory},"item_group") not in [d.accessory_group for d in frappe.get_all("Default Accessories Item",{"parent":"MFI Settings"},['accessory_group'])]:
						cost_of_accessory+=cost_of_monoaccessory
				else:
					cost_of_colouraccessory+=(((colour)/acc.yeild)-1)*get_rate_from_item_price(doc,acc.accessory) if (((colour)/acc.yeild)-1)>0 else 0
					if frappe.db.get_value("Item",{"name":acc.accessory},"item_group") not in [d.accessory_group for d in frappe.get_all("Default Accessories Item",{"parent":"MFI Settings"},['accessory_group'])]:
						cost_of_accessory+=cost_of_monoaccessory
				

	total_cost=(itm_rate+cost_of_accessory)
	insurance=(total_cost*(doc.insurance/100))
	# interest=((total_cost*((doc.interest_rate/100)/12)) / (1 - (pow((1 + ((doc.interest_rate/100)/12)), (-1 * doc.lease_period)))))
	interest=(-(((npf.pmt((doc.interest_rate/100)/12,doc.lease_period,total_cost,000))*doc.lease_period)+total_cost))
	print("Interest is:{0}".format(interest))
	print("Total Cost is:{0}".format(total_cost))
	print("insurance is:{0}".format(insurance))
	frappe.msgprint("Interest is:{0}".format(interest))
	frappe.msgprint("Total Cost is:{0}".format(total_cost))
	frappe.msgprint("insurance is:{0}".format(insurance))
	# print(total_cost,insurance,-((interest*doc.lease_period)+total_cost))
	contingency_amount_mono =cost_of_monotoner +cost_of_monoaccessory+total_cost+interest+insurance
	total_cost_of_contract = contingency_amount_mono*(doc.contingency/100)

	itm.mono_net_rate_per_click=total_cost_of_contract/ mono

	contingency_amount_colour =cost_of_monotoner+cost_of_colourtoner+cost_of_monoaccessory+cost_of_colouraccessory+total_cost+interest+insurance
	total_cost_of_contract_colour = contingency_amount_colour*(doc.contingency/100)

	itm.colour_net_rate_per_click=total_cost_of_contract_colour/colour



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

def set_parent_values(doc):
	total_rent=0
	for itm in doc.get('asset_quotation_selection'):
		total_rent+=(itm.net_rent+itm.margin_on_rent)
	doc.total_rent=total_rent