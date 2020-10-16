frappe.ui.form.on('Issue', {
	asset:function(frm){
		frappe.db.get_value('Asset',{'name':frm.doc.asset},['asset_name','location','serial_no'])
		.then(({ message }) => {
			frm.set_value('asset_name',message.asset_name);
			frm.set_value('location',message.location);
			frm.set_value('serial_no',message.serial_no);
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
						"project": frm.doc.project,
						"location":frm.doc.location
					}
				};
			}
		});
		frm.set_query("serial_no", function() {
				return {
					query: 'mfi_customization.mfi.doctype.issue.get_serial_no_list',
					filters: {
						"location":frm.doc.location,
						"asset":frm.doc.asset
					}
				};
		});
	},
	refresh: function (frm) {
		$("[data-doctype='Task']").hide();
		frm.add_custom_button(__('Task'), function() {
			frappe.set_route('List', 'Task', {issue: frm.doc.name});
		},__("View"));
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

frappe.ui.form.on("Asset Readings", "type", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	if (d.type=='Black & White'){
	$("div[data-idx='"+d.idx+"']").find("input[data-fieldname='reading_2']").css('pointer-events','none')
	}
	refresh_field("asset", d.name, d.parentfield);
});