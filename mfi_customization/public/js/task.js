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