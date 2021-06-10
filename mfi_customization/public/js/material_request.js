frappe.ui.form.on('Issue', {
	onload: function ( frm ) {
        frappe.call({
            method: "mfi_customization.mfi.doctype.material_request.get_approver",
            args: {
                "user": frappe.session.user
            },
            callback: function(r) {
            
                    frm.set_value('approver',r.message);				
                }
    
            
    });
    frappe.call({
        method: "mfi_customization.mfi.doctype.material_request.get_approver_name",
        args: {
            "user": frappe.session.user
        },
        callback: function(r) {
        
                frm.set_value('approver_name',r.message);				
            }

        
});

    
    }
});