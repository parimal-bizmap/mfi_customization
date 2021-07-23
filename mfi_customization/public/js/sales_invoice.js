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
                                row.description=d.description
                                row.uom=d.uom
                                    
                            });
                            frm.refresh_field("items")
                       }
                    }
            
                });
            // });
        }

	}
})

frappe.ui.form.on('Sales Invoice Item','mono_per_click_rate',function(frm,cdt,cdn){
    var d = locals[cdt][cdn];
    d.total_mono_charges=(parseFloat(d.monocurrent_reading)- parseFloat(d.mono_last_reading))*parseFloat(d.mono_per_click_rate)
    d.rate=parseFloat(d.total_mono_charges)+parseFloat(d.total_colourcharges)
    refresh_field("rate", d.name, d.parentfield);
    refresh_field("total_mono_charges", d.name, d.parentfield);
});
frappe.ui.form.on('Sales Invoice Item','colour_per_click_rate',function(frm,cdt,cdn){
    var d = locals[cdt][cdn];
    d.total_colourcharges=(parseFloat(d.colour_current_reading)- parseFloat(d.colour_last_reading))*parseFloat(d.colour_per_click_rate)
    d.rate=parseFloat(d.total_mono_charges)+parseFloat(d.total_colourcharges)
    refresh_field("rate", d.name, d.parentfield);2
    refresh_field("total_colourcharges", d.name, d.parentfield);
});