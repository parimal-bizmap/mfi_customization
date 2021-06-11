frappe.listview_settings['Material Request'] = {
	onload: function(listview) {
       if (frappe.user.has_role("Morocco ATM")){
        frappe.route_options = {
            "approver": ["=", frappe.session.user]
        };
    }
		
    }
};
