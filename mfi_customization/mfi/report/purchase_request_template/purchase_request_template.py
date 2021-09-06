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
    get_prev_months_consum_columns(columns, filters)
    avg_monthly_consump = {'label': 'Average Monthly Consumption', 'fieldname': "avg_monthly_consumption","fieldtype":"Float" }
    columns.append(avg_monthly_consump)
    get_warehouse(columns, filters)
    get_purchase_receipt_qty(columns, filters)
    get_in_transit_shipment(columns, filters)
    get_po_name(columns, filters)
    total_transit = {'label':'Total Transit Qty', 'fieldname':'total_transit_qty', 'fieldtype': 'Int'}
    life_stock_transit = {'label':'Life-Stock on hand plus Transit', 'fieldname':'life_stock_transit', 'fieldtype': 'Float'}
    columns.append(total_transit)
    columns.append(life_stock_transit)

    return columns
    
def get_purchase_receipt_qty(columns, filters):
    pr_qty_row = [{"label":"Qty < 90 Days","fieldname":"qty_less_than_90_days", "fieldtype":"Int" },
    {"label":"Qty > 91 Days and < 180 Days","fieldname":"qty_bet_91_180_days", "fieldtype":"Int"},
    {"label":"Qty > 181 Days and < 365 Days","fieldname":"qty_bet_181_365_days", "fieldtype":"Int"},
    {"label":"Qty > 365 Days","fieldname":".", "fieldtype":"Int"},
    {"label":"In Stock Qty","fieldname":"in_stock_qty", "fieldtype":"Int"},
    {"label":"Life-Stock on hand","fieldname":"life_stock_on_hand", "fieldtype":"Float"}]
    [columns.append(i) for i in pr_qty_row]

def get_po_name(columns, filters):
    po_list = frappe.db.get_list("Purchase Order", {'docstatus': 1, 'company':filters.get('company')}, 'name')
    if po_list :
        for po in po_list:
            po_row = {'label':po['name'], 'fieldname': 'po'+str(po_list.index(po)), 'fieldtype':'Data'}
            columns.append(po_row)
        total_po_row = {'label': 'Total ETA PO', 'fieldname': 'total_eta_po', 'fieldtype': 'Float'}
        columns.append(total_po_row)
        
def get_in_transit_shipment(columns, filters):
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
    
def get_prev_months_consum_columns(columns, filters):
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    for i in range(0, 6):
        dt = datetime.now() + relativedelta(months=+i)
        dt = str(dt.month) +'/'+ dt.strftime('%y')  
        monthly_row = {'label': dt, 'fieldname':'month'+str(i),'fieldtype': "Float" }
        columns.append(monthly_row)
    
def get_warehouse(columns, filters):
    warehouse_list =[i['name']  for i in frappe.db.get_list('Warehouse', {'is_group':1, 'company':filters.get('company')}, 'name')]
    # for i in warehouse_list:
    warehouse_row = {'label':warehouse_list[0]+' Qty' , 'fieldname':'warehouse','fieldtype': "Data" }
    columns.append(warehouse_row)

def get_data(filters, columns):
    data = []
    # fltr = {}
    from datetime import date
    from dateutil.relativedelta import relativedelta
    for itm in frappe.get_all('Item',filters,['item_code','item_name']):
        total_qty, avg_monthly_consumption = 0, 0
        row = {'part_number': itm.item_code,
               'part_name': itm.item_name}
        se_data = frappe.db.sql("""SELECT SI.qty, S.posting_date, SI.item_code 
            from `tabStock Entry` as S inner join `tabStock Entry Detail` as SI 
            on S.name= SI.parent where SI.item_code = '{0}' 
            and S.stock_entry_type='Material Issue' 
            and S.company = '{1}'""".format(itm.item_code, filters.get('company')), as_dict=1)
        if se_data :
            se_month = check_month_label(se_data, columns) 
            if se_month:
                total_qty += se_data[0]['qty'] 
                row[se_month] = total_qty
        dn_data = frappe.db.sql("""SELECT D.name, DI.qty, DI.item_code, D.posting_date 
            from `tabDelivery Note` as D inner join `tabDelivery Note Item` as DI 
            on D.name= DI.parent where D.docstatus=1 and  DI.item_code = '{0}'
            and company = '{1}'""".format(itm.item_code, filters.get('company')), as_dict=1)  
        #in transit shipment calculations
        total_month_qty = 0
        if dn_data :
            dn_qty, total_dn_qty = 0,0
            month_list, awb_no_list = [], []
            for dn in dn_data:
                shipment_data = frappe.db.sql("""SELECT S.awb_number , S.pickup_date
                from `tabShipment` as S inner join  `tabShipment Delivery Note` as SI 
                on S.name=SI.parent where SI.delivery_note = '{0}' """.format(dn['name'] ), as_dict=1)
                awb_number = [i['awb_number'] for i in shipment_data]
                for awb in shipment_data:
                    month_list.append(awb['pickup_date'].strftime('%B'))
                if awb_number :
                    dn_qty += dn['qty']
                    if columns :
                        awb_fieldname = [i['fieldname'] for i in columns if i['label'] == awb_number[0]]
                        if awb_fieldname:
                            awb = {str(awb_fieldname[0]) : dn_qty}
                        else:
                            awb = {str(awb_fieldname[0]) : 0}
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
                                total_month_qty += total_dn_qty
                        else:
                            total_month_row = {str(total_fieldname[0]) : 0}
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
        


        #calculate warehouse quantity
        warehouse = [w.get('name') for w in frappe.db.get_list('Warehouse', {'is_group':1, 'company':filters.get('company')}, 'name')]
        total_warehouse_qty, life_stock_on_hand_qty = 0,0
        child_warehouse = [w.get('name') for w in frappe.db.get_all("Warehouse", {'parent_warehouse':warehouse[0]}, 'name')]
        if child_warehouse:
            for child_w in child_warehouse:
                warehouse_qty = frappe.db.sql("""SELECT sum(actual_qty) as qty from tabBin 
                    where item_code='{0}' and warehouse = '{1}' """.format(itm.item_code,child_w), as_dict=1)
                total_warehouse_qty += warehouse_qty[0]['qty'] if warehouse_qty[0]['qty'] else 0
            warehouse_qty_row = {'warehouse': total_warehouse_qty}
            row.update(warehouse_qty_row)
            in_stock_qty= {'in_stock_qty': total_warehouse_qty}
            row.update(in_stock_qty)
            if row['avg_monthly_consumption']:
                life_stock_on_hand_qty = total_warehouse_qty/row['avg_monthly_consumption']
            life_stock_on_hand = {'life_stock_on_hand': life_stock_on_hand_qty}
            row.update(life_stock_on_hand)
        
        #calculate po qty and total qty
        po_list = frappe.db.sql("""SELECT P.name, PI.qty from `tabPurchase Order` as P inner join 
        `tabPurchase Order Item` as PI on P.name=PI.parent where P.docstatus=1 and PI.item_code= '{0}'
        and P.company = '{1}'""".format(itm.item_code, filters.get('company')), as_dict=1)
        total_po_qty = 0
        if po_list:
            for po in po_list:
                fieldname = [i['fieldname'] for i in columns if i['label'] == po['name']]
                if fieldname:
                    total_po_qty += po['qty']
                    po = {str(fieldname[0]) : po['qty']}
                else:
                    po = {str(fieldname[0]) : 0}
                row.update(po)
        else:
            print("/////po list ")
        total_po = {'total_eta_po' : total_po_qty}
        row.update(total_po)


        total_transit_qty = row.get('total_eta_po') + total_month_qty
        row['total_transit_qty'] = total_transit_qty 
        life_stock_transit = 0 
        if row['avg_monthly_consumption'] > 0:
            life_stock_transit = (row['in_stock_qty']+row['total_transit_qty'])/row['avg_monthly_consumption']
        row['life_stock_transit'] = life_stock_transit

        #calculate purchase receipt quantity
        pr_qty_data = frappe.db.sql("""SELECT SUM(CASE WHEN DATEDIFF(CURDATE(), P.posting_date) BETWEEN  0 AND 90 THEN 1 ELSE 0 END) D90,
                    SUM(CASE WHEN DATEDIFF(CURDATE(), P.posting_date) BETWEEN 91 AND 180 THEN 1 ELSE 0 END) D180,
                    SUM(CASE WHEN DATEDIFF(CURDATE(), P.posting_date) BETWEEN 181 AND 365 THEN 1 ELSE 0 END) D365,
                    SUM(CASE WHEN DATEDIFF(CURDATE(), P.posting_date) > 365 THEN 1 ELSE 0 END) D366
                    FROM `tabPurchase Receipt` as P inner join `tabPurchase Receipt Item` as PI on P.name=PI.parent
                    WHERE P.docstatus=1 and PI.item_code= '{0}' and P.company = '{1}'""".format(itm.item_code, filters.get('company')), as_dict=1)
        for pr_qty in pr_qty_data:
            
            if pr_qty.get('D90'):
                row.update({'qty_less_than_90_days' : pr_qty.get('D90')}) 
            else:
                row.update({'qty_less_than_90_days' : 0}) 
            if pr_qty.get('D180'):   
                row.update({'qty_bet_91_180_days' : pr_qty.get('D180')}) 
            else:
                row.update({'qty_bet_91_180_days' : 0}) 
            if pr_qty.get('D365'):   
                row.update({'qty_bet_181_365_days' : pr_qty.get('D365')}) 
            else:
                row.update({'qty_bet_181_365_days' : 0}) 
            if pr_qty.get('D366'):
                row.update({'qty_great_than_365_days' : pr_qty.get('D366')})
            else:
                row.update({'qty_great_than_365_days' : 0}) 
       

        data.append(row)
    return data

def check_month_label(data, columns):
    posting_date = str(data[0]['posting_date'].month) +'/'+ (data[0]['posting_date']).strftime('%y')
    if columns :
        fieldname = [i['fieldname'] for i in columns if i['label'] == posting_date]

    return fieldname[0] if fieldname else ''
