frappe.ui.form.on('Issue', {

	serial_no:function(frm){
		if(frm.doc.serial_no){
		frm.set_value('asset','');
		frm.set_value('asset_name','');
		frm.set_value('location','');
		frm.set_value('customer','');
		
		frappe.call({
			method: "mfi_customization.mfi.doctype.issue.get_customer",
			args: {
				"serial_no":frm.doc.serial_no,
				"asset":frm.doc.asset
			},
			callback: function(r) {
			
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
		frappe.db.get_value('Asset',{'name':frm.doc.asset,'docstatus':1},['asset_name','company','serial_no'])
		.then(({ message }) => {
			frm.set_value('asset_name',message.asset_name);
			frm.set_value('company',message.company);
			frm.set_value('serial_no',message.serial_no);
		});    
	} 
		if (!frm.doc.asset){
			frm.set_value('asset_name','');
		}  
	},
	status:function(frm){
		if(frm.doc.status == 'Closed'){
			frm.set_df_property('current_reading','reqd',1);
		}
	},
	details_available:function(frm){
			if (!frm.doc.details_available){
				frm.set_df_property('asset','reqd',0);
				frm.set_df_property('serial_no','reqd',0);
				frm.set_df_property('location','reqd',0);
			}
			if(frm.doc.details_available){
				frm.set_df_property('asset','reqd',1);
				frm.set_df_property('serial_no','reqd',1);
				frm.set_df_property('location','reqd',1);
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
		frm.set_query("location", function() {
			if (frm.doc.customer) {
				return {
					query: 'mfi_customization.mfi.doctype.issue.get_location',
					filters: {
						"customer":frm.doc.customer
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
			if (frm.doc.customer && !frm.doc.location) {
				return {
					query: 'mfi_customization.mfi.doctype.issue.get_asset_on_cust',
					filters: {
						// "location":frm.doc.location,
						"customer":frm.doc.customer
					}
				};
			}
	
		});

		frm.set_query("serial_no", function() {
			if(frm.doc.location && frm.doc.asset){	
			return {
					query: 'mfi_customization.mfi.doctype.issue.get_serial_no_list',
					filters: {
						"location":frm.doc.location
						,"asset":frm.doc.asset
					}
				};}
				if (frm.doc.customer && !frm.doc.location) {
					return {
						query: 'mfi_customization.mfi.doctype.issue.get_asset_serial_on_cust',
						filters: {
							// "location":frm.doc.location,
							"customer":frm.doc.customer
						}
					};
				}
				if(frm.doc.customer &&  frm.doc.location){
					return {
						query: 'mfi_customization.mfi.doctype.issue.get_serial_on_cust_loc',
						filters: {
							"location":frm.doc.location,
							"customer":frm.doc.customer
						}
					};

				}
		});
	},
	refresh: function (frm) {
		if (!frm.doc.__islocal ){
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
	else{
		frm.remove_custom_button('Task','Make');
		frm.remove_custom_button('Task','View');
		frm.remove_custom_button('Close');

	} 
	if(frm.doc.details_available){
		frm.set_df_property('asset','reqd',1);
		frm.set_df_property('serial_no','reqd',1);
		frm.set_df_property('location','reqd',1);
	}	
	

		// frm.set_query("asset", function() {
		// 	return {
		// 		query: 'mfi_customization.mfi.doctype.issue.get_live_asset',
		// 		filters: {
		// 				"docstatus" : 1
		// 		 }
		// 	};
		// });
	
	},
	validate:function(frm){
		if(!frm.response_date_time){
			frappe.db.get_value('Task',{'issue':frm.doc.name},['attended_date_time'],(val) =>
			{
				console.log(val.attended_date_time)
				frm.set_value('response_date_time',val.attended_date_time);
			});
		if (frm.doc.customer){
				frm.set_df_property("customer","read_only",1);			}

		}
		


	},
	customer:function(frm){
		if (frm.doc.customer){
			frappe.db.get_value("Project",{'customer':frm.doc.customer},"name", function(val){
				if (val.name){
					frm.set_value("project",val.name);
				}
			})
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