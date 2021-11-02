# -*- coding: utf-8 -*-
# Copyright (c) 2020, bizmap technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import getdate,today
from frappe.model.mapper import get_mapped_doc


def execute():
    for tk in  frappe.get_all('Task',['name','completed_by']):
        if len(frappe.get_all('User Permission',{'user':tk.get('completed_by'),"allow": 'Task','for_value':tk.get("name")})) == 0: 
            docperm = frappe.new_doc("User Permission")
            docperm.update({
            "user": tk.get("completed_by"),
            "allow": 'Task',
            "for_value": tk.get("name")
            })
            docperm.save(ignore_permissions=True)
            print(tk.get('name')+" "+tk.get('completed_by')+" "+docperm.get('user'))

#mfi_customization.mfi.patch.task_user_perm.execute