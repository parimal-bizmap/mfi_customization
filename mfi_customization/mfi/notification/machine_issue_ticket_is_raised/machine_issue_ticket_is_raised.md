hello,<br>
New Machine issue has been recorded details given below,<br>
issue:{{doc.name}}<br>
Subject:{{doc.subject}}<br>
Location:{{doc.location}}<br>
Asset:{{doc.asset}}<br>
Serial No:{{doc.serial_no}}<br>
Error Code:{{doc.error_code}}<br>
Failure Date:{{doc.failure_date_and_time}}<br>
Description:{{doc.description}}<br>
click below to check<br>
{{ frappe.utils.get_url_to_form(doc.doctype, doc.name) }}