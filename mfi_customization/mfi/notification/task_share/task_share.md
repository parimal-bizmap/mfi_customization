<b>Name</b>-{{doc.share_name}}<br>
<b>Subject</b>-{{ frappe.db.get_value("Task", doc.share_name, "subject") }}<br>
<b>Issue Type</b>-{{ frappe.db.get_value("Task", doc.share_name, "issue_type") }}<br>
<b>Customer</b>-{{ frappe.db.get_value("Task", doc.share_name, "customer") }}<br>
<b>Location</b>-{{ frappe.db.get_value("Task", doc.share_name, "location") }}<br>
<b>Asset</b>-{{ frappe.db.get_value("Task", doc.share_name, "asset") }}<br>
<b>Asset Name</b>-{{ frappe.db.get_value("Task", doc.share_name, "asset_name") }}<br>
<b>Serial No</b>-{{ frappe.db.get_value("Task", doc.share_name, "serial_no") }}<br>
<b>Assign Date</b>-{{ frappe.db.get_value("Task", doc.share_name, "assign_date") }}<br>
<b>Failure Date</b>-{{ frappe.db.get_value("Task", doc.share_name, "failure_date_and_time") }}<br>