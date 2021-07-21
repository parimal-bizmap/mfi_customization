frappe.ui.form.on('Sales Invoice', {
	get_assets
    :function(frm){
        if (frm.doc.project){
            // frm.add_custom_button('Get Assets', function() {
                frappe.call({
                    method: "mfi_customization.mfi.doctype.Asset.get_assets",
                    args: {
                        "project": frm.doc.project
                    },
                    callback: function(r) {
                       if (r.message){
                            frm.clear_table("items");
                            $.each(r.message || [], function(i, d) {
                                var row=frm.add_child("items")
                                row.item_code=d.item_code
                                row.item_name=d.item_name
                                row.location=d.location
                                row.asset=d.name
                                row.serial_no=d.serial_no
                                row.mono_per_click_rate=d.mono_per_click_rate
                                row.colour_per_click_rate=d.colour_per_click_rate
                                row.mono_per_click_rate=d.mono_per_click_rate
                                row.colour_per_click_rate=d.colour_per_click_rate
                                row.total_mono_charges=d.total_mono_charges
                                row.total_colourcharges=d.total_colourcharges
                                row.monocurrent_reading=d.monocurrent_reading
                                row.mono_last_reading=d.mono_last_reading
                                row.colour_current_reading=d.colour_current_reading
                                row.colour_last_reading=d.colour_last_reading
                                row.rate=d.rate
                                row.qty=1
                                    
                            });
                            frm.refresh_field("items")
                       }
                    }
            
                });
            // });
        }

	}
})