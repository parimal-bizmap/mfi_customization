from __future__ import unicode_literals
import frappe

def execute():
    for a in frappe.get_all('Asset',fields=['serial_no','name']):
        for sr in frappe.get_all('Asset Serial No',filters={'name':a.get('serial_no')}):
            frappe.db.set_value('Asset Serial No',sr.name,'asset',a.name)