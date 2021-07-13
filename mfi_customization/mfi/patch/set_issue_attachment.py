import frappe

def execute():
    for d in frappe.get_all("Task"):
        task=frappe.get_doc("Task",d.name)
        task.save()