import frappe

def execute():
    for i in frappe.get_all('Asset',{'docstatus':1},['location','name','serial_no']):
        if  len(frappe.get_all('Asset Serial No',{'name':i.get("serial_no")})) == 0:
                if i.get("serial_no"):
                    print("1111",i.get("serial_no"))

                    asset_srl_no = frappe.new_doc("Asset Serial No")
                    asset_srl_no.update({
                        "name": i.get("serial_no"),
                        "location": i.get("location"),
                        "asset":i.get("name"),
                        "serial_no":i.get("serial_no")
                        
                    })
                    asset_srl_no.save()
                    # doc = frappe.get_doc('Asset Serial No',{'name':x})
                    print("******",i.get("serial_no"))


#mfi_customization.mfi.patch.make_serial_no.execute