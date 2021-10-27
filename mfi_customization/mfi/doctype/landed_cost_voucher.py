import frappe,json

@frappe.whitelist()
def get_receipt_shipments(doc):
	doc=json.loads(doc)
	shipments=[]
	for receipt in doc.get('purchase_receipts'):
		for receipt_item in frappe.get_all("Purchase Receipt Item",{"parent":receipt.get("receipt_document")},["purchase_order"]):
			for so in frappe.get_all("Sales Order",{"po_no":receipt_item.purchase_order},["name"]):
				for dn in frappe.get_all("Delivery Note Item",{"against_sales_order":so.name},['parent'],group_by="parent"):
					for sp in frappe.get_all("Shipment Delivery Note",{"delivery_note":dn.parent},['parent'],group_by="parent"):
						shipments.append(sp.parent)
	return shipments

@frappe.whitelist()
def calculate_cost(doc):
	doc=json.loads(doc)

	items_total=0
	for item_row in doc.get("items"):
		items_total+=item_row.get("amount")

	weight_total=0
	for parcel in doc.get("shipment_parcel"):
		weight_total+=parcel.get("weight")
		
	item_insurance={}
	component_amount={}
	component_exists={}
	for item_row in doc.get("items"):
		charges=0
		for tax_row in doc.get("taxes"):
			component_exists[tax_row.get("landed_cost_component")]=tax_row.get("landed_cost_component")
			for lc in frappe.get_all("Landed Cost Component",{"name":tax_row.get("landed_cost_component")},["type","calculation_based"]):
				if (tax_row.get("landed_cost_component")=="InsuranceAmount"):
					if (not tax_row.get("amount")):
						frappe.throw("<b>Insurance</b> Amount Missing")
					item_insurance[item_row.get("item_code")]=((item_row.get("amount")/items_total)*tax_row.get("amount"))
							
				if (lc.type=="Manual" and  lc.calculation_based=="FOB"):
					charges+=((item_row.get("amount")/items_total)*tax_row.get("amount"))

				elif (lc.type=="Manual" and lc.calculation_based=="Weight"):
					charges+=((frappe.db.get_value("Item", item_row.get("item_code"),"item_weight")/weight_total)*tax_row.get("amount"))
		
		item_row["applicable_charges"]=charges

	for tax_row in doc.get("taxes"):
		amount=0
		for item_row in doc.get("items"):
			if tax_row.get("landed_cost_component")=="Customs value air":
				if not item_insurance:
					frappe.throw("<b>Insurance</b> Not Exist For Calculate <b>{0}</b>".format(tax_row.get("landed_cost_component")))
				amount+=(item_row.get("amount")+item_insurance[item_row.get("item_code")])
				tax_row["amount"]=amount

			elif tax_row.get("landed_cost_component")=="FreightLocal":
				amount+=((frappe.db.get_value("Item", item_row.get("item_code"),"item_weight")/weight_total)*(doc.get("freight_charges")*doc.get("currency_exchange_rate")))
				tax_row["amount"]=amount
			
			elif tax_row.get("landed_cost_component")=="Customs value sea":
				if not item_insurance:
					frappe.throw("<b>Insurance</b> Not Exist For Calculate <b>{0}</b>".format(tax_row.get("landed_cost_component")))
				amount+=((item_row.get("amount")+item_insurance[item_row.get("item_code")])+((frappe.db.get_value("Item", item_row.get("item_code"),"item_weight")/weight_total)*(doc.get("freight_charges")*doc.get("currency_exchange_rate"))))
				tax_row["amount"]=amount

			elif (tax_row.get("landed_cost_component")=="RailwayLevy" or tax_row.get("landed_cost_component")=="GOK" or tax_row.get("landed_cost_component")=="Duty"):
				if not (component_exists.get("Customs value sea") or component_exists.get("Customs value air")):
					frappe.throw("<b>Customs value air OR Customs value sea</b> Not Exist For Calculate <b>{0}</b>".format(tax_row.get("landed_cost_component")))
					
		component_amount[tax_row.get("landed_cost_component")]=amount

	for tax_row in doc.get("taxes"):
		amount=0
		for item_row in doc.get("items"):
			if tax_row.get("landed_cost_component")=="RailwayLevy":
				amount+=(0.02*(component_amount.get("Customs value sea") or component_amount.get("Customs value air")))
				tax_row["amount"]=amount
			elif tax_row.get("landed_cost_component")=="GOK":
				amount+=(0.035*(component_amount.get("Customs value sea") or component_amount.get("Customs value air")))
				tax_row["amount"]=amount
			elif tax_row.get("landed_cost_component")=="Duty":
				amount+=(frappe.db.get_value("Item", item_row.get("item_code"),"duty_percentage")*(component_amount.get("Customs value sea") or component_amount.get("Customs value air")))
				tax_row["amount"]=amount
	return doc
	