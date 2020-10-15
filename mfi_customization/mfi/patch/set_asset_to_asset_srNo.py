from __future__ import unicode_literals
import frappe

def execute():
    # bench execute mfi_customization.mfi.patch.set_asset_to_asset_srNo.execte
    
    for a in frappe.get_all('Asset',fields=['serial_no','name','location']):
        for sr in frappe.get_all('Asset Serial No',filters={'name':a.get('serial_no')}):
            frappe.db.set_value('Asset Serial No',sr.name,'asset',a.name)
            frappe.db.set_value('Asset Serial No',sr.name,'location',a.location)