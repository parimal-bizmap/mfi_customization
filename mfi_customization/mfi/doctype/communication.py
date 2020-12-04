import frappe

def after_insert(doc,method):
    domain_rule=email_rules_true_for_domain(doc.sender)
    email_rule=email_rules_true_for_emails_table(doc.sender)
    if (domain_rule.get('is_true') or email_rule.get('is_true')) and doc.sent_or_received=='Received':
        issue=frappe.new_doc("Issue")
        issue.subject=doc.subject
        issue.description=doc.content
        issue.raised_by=doc.sender
        issue.customer=domain_rule.get('customer') if domain_rule.get('is_true') else  email_rule.get('customer')
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

def email_rules_true_for_domain(sender):
    resp={'is_ture':False,'customer':''}
    for d in frappe.get_all('Email Rules for Issue',{'group_by':'Domain'},['name','domain','customer']):
        if '@' in sender and d.get('domain').lower() in sender.split('@')[1]:
            resp.update({'is_true':True,'customer':d.customer})
            return resp
    return resp

def email_rules_true_for_emails_table(sender):
    resp={'is_ture':False,'customer':''}
    for d in frappe.get_all('Email Rules for Issue',{'group_by':'Emails'}):
        rules=frappe.get_doc('Email Rules for Issue',d.name)
        emails=[]
        for tb in rules.get('email_list_for_issue'):
            emails.append(tb.get('email'))
        if sender in emails:
            resp.update({'is_true':True,'customer':d.customer})
            return resp
    return resp


