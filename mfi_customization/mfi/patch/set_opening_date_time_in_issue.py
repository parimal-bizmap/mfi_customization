import frappe

# bench execute mfi_customization.mfi.patch.set_opening_date_time_in_issue.execute
def execute():
    for d in frappe.get_all("Issue",["name","opening_time","opening_date"]):
        import datetime
        dt=(datetime.datetime.min +d.opening_time).time()
        from datetime import datetime
        frappe.db.set_value("Issue",d.name,"opening_date_time",datetime.combine(d.opening_date, dt))