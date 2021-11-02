
frappe.ui.form.on('Purchase Order', {
    address:function(frm){
        frm.set_value('address_detail', "");
		if (frm.doc.address!=undefined){
            frappe.call({
                method: "frappe.contacts.doctype.address.address.get_address_display",
                args: {"address_dict": frm.doc.address},
                callback: function(r) {
                    if(r.message) {
                        frm.set_value('address_detail', r.message);
                    }
                }
            });
        }
    }
})