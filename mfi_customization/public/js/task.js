frappe.ui.form.on('Task', {
asset:function(frm){
    frappe.db.get_value('Asset',{'name':frm.doc.asset},['asset_name','location'])
    .then(({ message }) => {
        frm.set_value('asset_name',message.asset_name);
        frm.set_value('location',message.location);
    });                                                                                  
},
refresh:function(frm){
    frm.add_custom_button('Material Request', () => {
        frappe.model.open_mapped_doc({
            method: "mfi_customization.mfi.doctype.task.make_material_req",
            frm: me.frm
        })

        },
        __('Make')
        )
},
setup:function(frm){
    frm.set_query("asset", "current_reading", function() {
        return {
            filters: {
                "name": frm.doc.asset
            }
        }
    });
},
validate:function(frm){
    // Assigning time on start and on complete
    console.log(frm.doc.assign_date);
    if (frm.doc.completed_by && frm.doc.assign_date == null){
        frm.set_value("assign_date",frappe.datetime.now_datetime());
        // console.log(frm.doc.modified);
        // console.log(frm.doc.completed_by);
    };
    if (frm.doc.status == 'Working' && frm.doc.attended_date_time == null){
        frm.set_value("attended_date_time", frappe.datetime.now_datetime());
    };
    
    if (frm.doc.status == 'Completed'){
        frm.set_value("completion_date_time", frm.doc.modified);
    };
    


}
})
cur_frm.dashboard.add_transactions([
	{
		'items': [
			'Material Request'
		],
		'label': 'Others'
	},
]);

