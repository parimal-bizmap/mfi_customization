frappe.ui.form.on('Sales Invoice', {
	get_assets
    :function(frm){
        if (frm.doc.project){
                frappe.call({
                    method: "mfi_customization.mfi.doctype.sales_invoice.get_assets",
                    args: {
                        "project": frm.doc.project
                    },
                    callback: function(r) {
                       if (r.message){
                            frm.clear_table("assets_rates_item");
                            var total_mono=0;
                            var total_colour=0;
                            var per_click_mono=0;
                            var per_click_colour=0;
                            $.each(r.message[0] || [], function(i, d) {
                                var row=frm.add_child("assets_rates_item")
                                row.asset=d.asset
                                row.asset_name=d.asset_name
                                row.serial_no=d.serial_no
                                row.colour_click_rate=d.colour_click_rate
                                row.mono_click_rate=d.mono_click_rate
                                row.total_mono_reading=d.total_mono_reading
                                row.total_colour_reading=d.total_colour_reading
                                row.mono_current_reading=d.mono_current_reading
                                row.mono_last_reading=d.mono_last_reading
                                row.colour_current_reading=d.colour_current_reading
                                row.colour_last_reading=d.colour_last_reading
                                row.total_rate=d.total_rate
                                total_mono+=d.total_mono_reading
                                total_colour+=d.total_colour_reading
                                per_click_mono=d.mono_click_rate
                                per_click_colour=d.colour_click_rate
                                    
                            });
                            $.each(r.message[1] || [], function(i, d) {
                                var row=frm.add_child("printing_slabs")
                                row.rage_from=d.range_from
                                row.range_to=d.range_to
                                row.printer_type=d.printer_type
                                row.no_of_copies=parseFloat(d.range_to)-parseFloat(d.range_from)
                                row.rate=d.rate
                                row.total_amount=parseFloat(row.no_of_copies)*d.rate
                            });
                            frm.set_value("total_billable_assets",(r.message).length);
                            frm.set_value("total_mono_reading",total_mono);
                            frm.set_value("total_color_reading",total_colour);
                            frm.set_value("mono_click_rate",per_click_mono);
                            frm.set_value("colour_click_rate",per_click_colour);
                            frm.refresh_field("assets_rates_item")
                            frm.refresh_field("printing_slabs")
                       }
                    }
            
                });
        }

	}
})

frappe.ui.form.on('Assets Rates Item','mono_click_rate',function(frm,cdt,cdn){
    var d = locals[cdt][cdn];
    d.total_mono_reading=(parseFloat(d.mono_current_reading)- parseFloat(d.mono_last_reading))*parseFloat(d.mono_click_rate)
    d.total_rate=parseFloat(d.total_mono_reading)+parseFloat(d.total_colour_reading)
    refresh_field("total_rate", d.name, d.parentfield);
    refresh_field("total_mono_reading", d.name, d.parentfield);
    var total_mono=0;
    var total_colour=0;
    var per_click_mono=0;
    var per_click_colour=0;
    $.each(frm.doc.assets_rates_item || [], function(i, d) {
        total_mono+=d.total_mono_reading
        total_colour+=d.total_colour_reading
        per_click_mono=d.mono_click_rate
        per_click_colour=d.colour_click_rate
    })
    frm.set_value("total_mono_reading",total_mono);
    frm.set_value("total_color_reading",total_colour);
    frm.set_value("mono_click_rate",per_click_mono);
    frm.set_value("colour_click_rate",per_click_colour);
});
frappe.ui.form.on('Assets Rates Item','colour_click_rate',function(frm,cdt,cdn){
    var d = locals[cdt][cdn];
    d.total_colour_reading=(parseFloat(d.colour_current_reading)- parseFloat(d.colour_last_reading))*parseFloat(d.colour_click_rate)
    d.total_rate=parseFloat(d.total_mono_reading)+parseFloat(d.total_colour_reading)
    refresh_field("total_rate", d.name, d.parentfield);
    refresh_field("total_colour_reading", d.name, d.parentfield);
    var total_mono=0;
    var total_colour=0;
    var per_click_mono=0;
    var per_click_colour=0;
    $.each(frm.doc.assets_rates_item || [], function(i, d) {
        total_mono+=d.total_mono_reading
        total_colour+=d.total_colour_reading
        per_click_mono=d.mono_click_rate
        per_click_colour=d.colour_click_rate
    })
    frm.set_value("total_mono_reading",total_mono);
    frm.set_value("total_color_reading",total_colour);
    frm.set_value("mono_click_rate",per_click_mono);
    frm.set_value("colour_click_rate",per_click_colour);
});