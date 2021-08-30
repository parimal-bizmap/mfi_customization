# Copyright (c) 2013, bizmap technologies and contributors
# For license information, please see license.txt

import frappe
monthly_date = []

def execute(filters=None):
	columns  = get_column(filters)
	data     = get_data(filters, columns)
	return columns, data

def get_column(filters = None):
	columns = [
		{
			"label":"Part Number",
			"fieldname":"part_number",
			"fieldtype":"Link",
			"options":"Item"
		},
		{
			"label":"Part Name",
			"fieldname":"part_name",
			"fieldtype":"Data"  
		},
		{
			"label":"Brand",
			"fieldname":"brand",
			"fieldtype":"Data"  
		},
		{
			"label":"For Use In Models",
			"fieldname":"for_use_in_models",
			"fieldtype":"Data"  
		}
	]
	get_prev_months_consum_columns(columns)
	avg_monthly_consump = {'label': 'Average Monthly Consumption', 'fieldname': "avg_monthly_consumption","fieldtype":"Float" }
	columns.append(avg_monthly_consump)
	get_warehouse(columns)
	get_in_transit_shipment(columns)
	get_po_name(columns)

	return columns

def get_po_name(columns):
	po_list = frappe.db.get_list("Purchase Order", {'docstatus': 1}, 'name')
	if po_list :
		for po in po_list:
			if po:
				po_row = {'label':po['name'], 'fieldname': 'po'+str(po_list.index(po)), 'fieldtype':'Data'}
				columns.append(po_row)
		total_po_row = {'label': 'Total ETA PO', 'fieldname': 'total_eta_po', 'fieldtype': 'Float'}
		columns.append(total_po_row)
		
def get_in_transit_shipment(columns):
	month_list, awb_no_list = [], []
	awb_list = frappe.db.sql("""SELECT awb_number, pickup_date from `tabShipment` where pickup_date 
	BETWEEN SUBDATE(CURDATE(), INTERVAL 3 MONTH) AND NOW()""", as_dict=1)
	for awb in awb_list:
		month_list.append(awb['pickup_date'].strftime('%B'))
	for month in month_list:
		awb_no_list = [i['awb_number'] for i in frappe.db.sql("""SELECT awb_number from `tabShipment` 
		where monthname(pickup_date)='{0}'""".format(month), as_dict=1)]
		if awb_no_list :
			for awb in awb_no_list:
				awb_row = {'label': awb, 'fieldname':'awb'+month+str(awb_no_list.index(awb)),'fieldtype': "Data" }
				if awb_row not in columns:
					columns.append(awb_row)
			total_month_row = {'label': 'Total '+ month, 'fieldname':'total_month'+str(month),'fieldtype': "Data" }
			if total_month_row not in columns:
				columns.append(total_month_row)
	
def get_prev_months_consum_columns(columns):
	from datetime import datetime
	from dateutil.relativedelta import relativedelta
	for i in range(0, 6):
		dt = datetime.now() + relativedelta(months=+i)
		dt = str(dt.month) +'/'+ dt.strftime('%y')  
		monthly_row = {'label': dt, 'fieldname':'month'+str(i),'fieldtype': "Float" }
		columns.append(monthly_row)
	
def get_warehouse(columns):
	warehouse_list = frappe.db.get_list('Warehouse', {'is_group':1}, 'name')
	for i in warehouse_list:
		warehouse_row = {'label':i['name']+' Qty' , 'fieldname':'warehouse'+str(i),'fieldtype': "Data" }
		columns.append(warehouse_row)

def get_data(filters, columns):
	data = []
	fltr = {}
	from datetime import date
	from dateutil.relativedelta import relativedelta
	for itm in frappe.get_all('Item',fltr,['item_code','item_name']):
		total_qty, avg_monthly_consumption = 0, 0
		row = {'part_number': itm.item_code,
			   'part_name': itm.item_name}
		se_data = frappe.db.sql("""SELECT SI.qty, S.posting_date, SI.item_code 
			from `tabStock Entry` as S inner join `tabStock Entry Detail` as SI 
			on S.name= SI.parent where SI.item_code = '{0}' 
			and S.stock_entry_type='Material Issue'""".format(itm.item_code), as_dict=1)
		if se_data :
			se_month = check_month_label(se_data, columns) 
			if se_month:
				total_qty += se_data[0]['qty'] 
				row[se_month] = total_qty
		dn_data = frappe.db.sql("""SELECT D.name, DI.qty, DI.item_code, D.posting_date 
			from `tabDelivery Note` as D inner join `tabDelivery Note Item` as DI 
			on D.name= DI.parent where D.docstatus=1 
			and  DI.item_code = '{0}'""".format(itm.item_code), as_dict=1)  
		#in transit shipment calculations
		if dn_data :
			dn_qty, total_dn_qty = 0,0
			month_list, awb_no_list = [], []
			for dn in dn_data:
				shipment_data = frappe.db.sql("""SELECT S.awb_number , S.pickup_date
				from `tabShipment` as S inner join  `tabShipment Delivery Note` as SI 
				on S.name=SI.parent where SI.delivery_note = '{0}'""".format(dn['name']), as_dict=1)
				awb_number = [i['awb_number'] for i in shipment_data]
				for awb in shipment_data:
					month_list.append(awb['pickup_date'].strftime('%B'))
				if awb_number :
					dn_qty += dn['qty']
					if columns :
						awb_fieldname = [i['fieldname'] for i in columns if i['label'] == awb_number[0]]
						if awb_fieldname:
							awb = {str(awb_fieldname[0]) : dn_qty}
							row.update(awb)
					for month in month_list:
						total_fieldname = [i['fieldname'] for i in columns if i['label'] == 'Total '+ month]
						total_month_list = [i['awb_number'] for i in frappe.db.sql("""SELECT awb_number from `tabShipment` 
						where monthname(pickup_date)='{0}'""".format(month), as_dict=1)] 
						if total_fieldname:
							for awb_month in total_month_list:
								if awb_number[0]== awb_month:
									total_dn_qty += dn_qty
									total_month_row = {str(total_fieldname[0]) : total_dn_qty}
									row.update(total_month_row)

			dn_month = check_month_label(dn_data, columns)
			if dn_month:
				total_qty += dn_data[0]['qty'] if dn_month else 0
				row[dn_month] = total_qty
		if 'month0' in row.keys():
			avg_monthly_consumption += row['month0']
		if 'month1' in row.keys():
			avg_monthly_consumption += row['month1']
		if 'month2' in row.keys():
			avg_monthly_consumption += row['month2']
		if 'month3' in row.keys():
			avg_monthly_consumption += row['month3']
		if 'month4' in row.keys():
			avg_monthly_consumption += row['month4']
		if 'month5' in row.keys():
			avg_monthly_consumption += row['month5']
		row['avg_monthly_consumption'] = avg_monthly_consumption / 6
		#calculate po qty and total qty
		po_list = frappe.db.sql("""SELECT P.name, PI.qty from `tabPurchase Order` as P inner join 
		`tabPurchase Order Item` as PI on P.name=PI.parent where PI.item_code= '{0}'""".format(itm.item_code), as_dict=1)
		if po_list:
			total_po_qty = 0
			for po in po_list:
				if po and columns:
					fieldname = [i['fieldname'] for i in columns if i['label'] == po['name']]
					if fieldname:
						total_po_qty += po['qty']
						po = {str(fieldname[0]) : po['qty']}
						row.update(po)
		total_po = {'total_eta_po' : total_po_qty}
		row.update(total_po)
		data.append(row)
	return data

def check_month_label(data, columns):
	posting_date = str(data[0]['posting_date'].month) +'/'+ (data[0]['posting_date']).strftime('%y')
	if columns :
		fieldname = [i['fieldname'] for i in columns if i['label'] == posting_date]

	return fieldname[0] if fieldname else ''
