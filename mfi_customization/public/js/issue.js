frappe.ui.form.on('Issue', {
	// serial_no:function(frm){
	// 	if (frm.doc.serial_no){
	// 	frm.set_value('asset','');
	// 	frm.set_value('asset_name','');
	// 	frm.set_value('location','');
	// 	frappe.db.get_value('Asset Serial No',{'name':frm.doc.serial_no},['asset','location'])
	// 	.then(({ message }) => {
	// 		if (!frm.doc.asset){
	// 		frm.set_value('asset',message.asset);
	// 		}
	// 		if (!frm.doc.location){
	// 		frm.set_value('location',message.location);
	// 		}
	// 	}); 
	// }                                                                                 
	// },
	serial_no:function(frm){
		if(frm.doc.serial_no){
		frm.set_value('asset','');
		frm.set_value('asset_name','');
		frm.set_value('location','');
		frm.set_value('customer','');
		
		// frappe.db.get_value('Asset',{'serial_no':frm.doc.serial_no},['customer'])
		// .then(({ message }) => {
			
		// 	if (!frm.doc.customer){
		// 		console.log("********")
		// 		frm.set_value('customer',message.customer);
		// 		}
			
		// });
		frappe.call({
			method: "mfi_customization.mfi.doctype.issue.get_customer",
			args: {
				"serial_no":frm.doc.serial_no,
				"asset":frm.doc.asset
			},
			callback: function(r) {
			
					console.log(r.message);
					frm.set_value('customer',r.message);				
				}
	
			
	});
		frappe.db.get_value('Asset Serial No',{'name':frm.doc.serial_no},['asset','location'])
		.then(({ message }) => {
			
			if (!frm.doc.asset){
					frm.set_value('asset',message.asset);
				}

			if (!frm.doc.location){
					frm.set_value('location',message.location);
				}
		});                                                                                  
	}},
	asset:function(frm){
		if (frm.doc.asset){
		frappe.db.get_value('Asset',{'name':frm.doc.asset},['asset_name','company'])
		.then(({ message }) => {
			frm.set_value('asset_name',message.asset_name);
			frm.set_value('company',message.company);
		});    
	} 
		if (!frm.doc.asset){
			frm.set_value('asset_name','');
		}  
	},
	location:function(frm){
		if (frm.doc.location){
			frappe.db.get_value('Location',{'name':frm.doc.location},['company'])
			.then(({ message }) => {
				frm.set_value('company',message.company);
			});    
		} 
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
						"location":frm.doc.location
					}
				};
			}
		});
		frm.set_query("asset", function() {
			if (frm.doc.customer && frm.doc.location) {
				return {
					query: 'mfi_customization.mfi.doctype.issue.get_asset_in_issue',
					filters: {
						"location":frm.doc.location,
						"customer":frm.doc.customer
					}
				};
			}
		});
		frm.set_query("serial_no", function() {
				return {
					query: 'mfi_customization.mfi.doctype.issue.get_serial_no_list',
					filters: {
						"location":frm.doc.location
						,"asset":frm.doc.asset
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
	},validate:function(frm){
		console.log(frm.doc.asset)
		if(!frm.response_date_time){
			frappe.db.get_value('Task',{'issue':frm.doc.name},['attended_date_time'],(val) =>
			{
				console.log(val.attended_date_time)
				frm.set_value('response_date_time',val.attended_date_time);
			});
			

		}


	}
	// validate:function(frm){
	// 	if(!frm.doc.project){
	// 		frappe.throw("Please Enter Project in Reference")
		
	// 	}
	// 	frappe.call({
	// 		method:
	// 		"mfi_customization.mfi.doctype.task.set_readings",
	// 		args: {
	// 			project: frm.doc.project,
	// 			asset:frm.doc.asset
	// 		},
	// 		callback: (r) => {
	// 			if(r.message) {
	   
	// 				cur_frm.clear_table("last_readings");
	// 				r.message.forEach(function(element) {
	// 				var c = cur_frm.add_child("last_readings");
	// 				c.date = element.date;
	// 				c.type = element.type;
	// 				c.asset = element.asset;
	// 				c.reading = element.black_white;
	// 				c.reading_2 = element.colour;
	// 			});
	// 			refresh_field("last_readings"); 
	// }}
	// 	})
		
	
	
	// }


})

frappe.ui.form.on("Asset Readings", "type", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	if (d.type=='Black & White'){
	$("div[data-idx='"+d.idx+"']").find("input[data-fieldname='reading_2']").css('pointer-events','none')
	}
	refresh_field("asset", d.name, d.parentfield);
});