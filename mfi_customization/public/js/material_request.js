frappe.ui.form.on('Material Request', {
	onload: function ( frm ) {
        if (frm.doc.__islocal) {
            frappe.call({
                method: "mfi_customization.mfi.doctype.material_request.get_approver",
                args: {
                    "user": frappe.session.user
                },
                callback: function(r) {
                    frm.set_value('approver',r.message["approver"]);	
                    frm.set_value('approver_name',r.message["approver_name"]);				
                }
        
        });
        }

    }
});