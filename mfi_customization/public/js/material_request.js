{% include 'erpnext/public/js/controllers/buying.js' %};

frappe.ui.form.on('Material Request', {
    schedule_date:function(frm){
        frm.set_query("item_code", "items", function() {
			return {
				query: "mfi_customization.mfi.doctype.material_request.item_query",
				filters:{
					"item_group":["IN",["Consumable","Spares"]]
				}
			}
		});
    },
	onload: function ( frm ) {
        frm.set_value("material_request_type","Material Issue")
        frm.set_query("item_code", "items", function(doc, cdt, cdn) {
			return {
				query: "erpnext.controllers.queries.item_query"
			}
		});
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
