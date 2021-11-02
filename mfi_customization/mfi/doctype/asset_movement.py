# -*- coding: utf-8 -*-
# Copyright (c) 2020, bizmap technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


@frappe.whitelist()
def get_asset_filter(doctype, txt, searchfield, start, page_len, filters):
    lst = []
    for i in frappe.get_all('Task',{"name":filters.get("task")},['asset']):
        lst.append(i.get("asset"))
    return [(d,) for d in lst]