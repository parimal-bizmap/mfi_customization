# -*- coding: utf-8 -*-
# Copyright (c) 2020, bizmap technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
#mfi_customization.mfi.patch.assign_to_issue.execute

def execute():
    lst = []
    for i in frappe.get_all("Task",['completed_by','name','assign_date','issue']):
        if i.get("name") not in lst:
            print(lst)
            if i.get("issue") :
                issue = frappe.get_doc("Issue",{"name":i.get("issue")})
                
                if i.get("completed_by"):
                    issue.assign_to = i.get("completed_by")
                if i.get("assign_date"):
                    issue.assign_date = i.get("assign_date")
            print("***",i.get("issue"),"***",i.get("completed_by"),i.get("assign_date"))
            lst.append(i.get("name"))
            issue.save()
