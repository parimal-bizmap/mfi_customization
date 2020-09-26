frappe.ui.form.on('Issue', {
	asset:function(frm){
		frappe.db.get_value('Asset',{'name':frm.doc.asset},['asset_name'])
		.then(({ message }) => {
			frm.set_value('asset_name',message.asset_name);
		});                                                                                  
	},
	setup:function(frm){
		frm.set_query("asset", "current_reading", function() {
			return {
				filters: {
					"name": frm.doc.asset
				}
			}
		});
		frm.set_query("asset", function() {
			if (frm.doc.project) {
				return {
					query: 'mfi_customization.mfi.doctype.issue.get_asset_list',
					filters: {
						"project": frm.doc.project
					}
				};
			}
		});
	},
	refresh: function (frm) {
		if (frm.doc.status !== "Closed" && frm.doc.agreement_fulfilled === "Ongoing") {
			frm.remove_custom_button("Task", 'Make')
			frm.add_custom_button(__("Task"), function () {
				frappe.model.open_mapped_doc({
					method: "mfi_customization.mfi.doctype.issue.make_task",
					frm: frm
				});
			}, __("Make"));
		}
	}
})

frappe.ui.form.on("Asset Readings", "date", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	d.asset=frm.doc.asset
	refresh_field("asset", d.name, d.parentfield);
});