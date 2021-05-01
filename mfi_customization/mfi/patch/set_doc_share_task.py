from __future__ import unicode_literals
import frappe

def execute():
    for tk in  frappe.get_all('Task',['name','completed_by']):
        if len(frappe.get_all('DocShare',{'user':tk.get('completed_by'),"share_doctype": 'Task',"share_name": tk.get('name')})) == 0: 
            docshare = frappe.new_doc("DocShare")
            docshare.update({
                "user": tk.get('completed_by'),
                "share_doctype": 'Task',
                "share_name": tk.get('name'),
                "read": 1,
                "write": 1
            })
            
            docshare.save(ignore_permissions=True)
            print(tk.get('name')+" "+tk.get('completed_by')+" "+docshare.get('user'))

#mfi_customization.mfi.patch.set_doc_share_task.execute