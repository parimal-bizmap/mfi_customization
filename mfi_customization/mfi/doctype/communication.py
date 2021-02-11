import frappe

def after_insert_file(doc,method):
    if doc.attached_to_doctype=="Communication":
        if len(frappe.get_all('Issue',{'communication':doc.attached_to_name}))==0:
            cmm_doc=frappe.get_doc("Communication",doc.attached_to_name)
            domain_rule=email_rules_true_for_domain(cmm_doc.sender)
            email_rule=email_rules_true_for_emails_table(cmm_doc.sender)
            if (domain_rule.get('is_true') or email_rule.get('is_true')) and cmm_doc.sent_or_received=='Received':
                issue=frappe.new_doc("Issue")
                issue.subject=cmm_doc.subject
                issue.description=cmm_doc.content
                issue.raised_by=cmm_doc.sender
                issue.customer=domain_rule.get('customer') if domain_rule.get('is_true') else  email_rule.get('customer')
                issue.flags.ignore_mandatory=True
                issue.company=domain_rule.get('company') if domain_rule.get('is_true') else  email_rule.get('company')
                issue.save()
                file_doc = frappe.new_doc("File")
                file_doc.file_name = doc.file_name
                file_doc.file_size = doc.file_size
                file_doc.folder = doc.folder
                file_doc.is_private = doc.is_private
                file_doc.file_url = doc.file_url
                file_doc.attached_to_doctype = "Issue"
                file_doc.attached_to_name=issue.get('name')
                file_doc.save()
        else:
            for d in frappe.get_all('Issue',{'communication':doc.attached_to_name},['name']):
                file_doc = frappe.new_doc("File")
                file_doc.file_name = doc.file_name
                file_doc.file_size = doc.file_size
                file_doc.folder = doc.folder
                file_doc.is_private = doc.is_private
                file_doc.file_url = doc.file_url
                file_doc.attached_to_doctype = "Issue"
                file_doc.attached_to_name=d.get('name')
                file_doc.save()

def email_rules_true_for_domain(sender):
    resp={'is_ture':False,'customer':'','company':''}
    for d in frappe.get_all('Email Rules for Issue',{'group_by':'Domain'},['name','domain_name','customer']):
        if '@' in sender and d.get('domain_name').lower() in sender.split('@')[1]:
            customer=frappe.get_doc('Customer',d.customer)
            resp.update({'is_true':True,'customer':d.customer})
            for cu in customer.get('accounts'):
                resp.update({'company':cu.company})
            return resp
    return resp

def email_rules_true_for_emails_table(sender):
    resp={'is_ture':False,'customer':'','company':''}
    for d in frappe.get_all('Email Rules for Issue',{'group_by':'Emails'},['name','customer']):
        rules=frappe.get_doc('Email Rules for Issue',d.name)
        emails=[]
        for tb in rules.get('email_list_for_issue'):
            emails.append(tb.get('email'))
        if sender in emails:
            customer=frappe.get_doc('Customer',d.customer)
            resp.update({'is_true':True,'customer':d.customer})
            for cu in customer.get('accounts'):
                resp.update({'company':cu.company})
            return resp
    return resp


