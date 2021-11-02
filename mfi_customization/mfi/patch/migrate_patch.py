import frappe
import os
import json
import sys


#   bench execute mfi_customization.mfi.patch.migrate_patch.get_custom_role_permission
def get_custom_role_permission(site=None):
    if sys.argv[2]=='--site':
        os.system("bench --site {0} export-fixtures".format(sys.argv[3]))
    else:
        os.system("bench export-fixtures")

#   bench execute mfi_customization.mfi.patch.migrate_patch.set_custom_role_permission
def set_custom_role_permission():
    with open(frappe.get_app_path("mfi_customization","fixtures","custom_docperm.json")) as f:
        for d in json.load(f):
            if len(frappe.get_all('Custom DocPerm',{'parent':d.get('parent'),'role':d.get('role')}))==0:
                role=frappe.new_doc('Custom DocPerm')
                for k in d.keys():
                    role.set(k,d.get(k))
                role.save()

