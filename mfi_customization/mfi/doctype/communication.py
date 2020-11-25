import frappe

def after_insert(doc,method):
    issue=frappe.new_doc("Issue")
    issue.subject=doc.subject
    issue.description=doc.content
    issue.flags.ignore_mandatory=True
    issue.save()

def after_insert_file(doc,method):
    if doc.attached_to_doctype=="Communication":
        file_doc = frappe.new_doc("File")
        file_doc.file_name = doc.file_name
        file_doc.file_size = doc.file_size
        file_doc.folder = doc.folder
        file_doc.is_private = doc.is_private
        file_doc.file_url = doc.file_url
        file_doc.attached_to_doctype = "Issue"
        issue_list=frappe.get_all('Issue',order_by='name desc', limit=1)
        if issue_list:
            file_doc.attached_to_name=issue_list[0].get('name')
            file_doc.save()