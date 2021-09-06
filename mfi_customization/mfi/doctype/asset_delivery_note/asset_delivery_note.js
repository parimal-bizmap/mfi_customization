// Copyright (c) 2021, bizmap technologies and contributors
// For license information, please see license.txt
frappe.ui.form.on('Asset Delivery Note', {
	refresh: function(frm) {
		if (!frm.doc.__islocal){
			frm.add_custom_button(__('Asset'), function() {
				frappe.call({
					method: "mfi_customization.mfi.doctype.asset_delivery_note.asset_delivery_note.create_assets",
					args:{"doc":frm.doc}
				})
			},__("Create"));
		}
		let item = '';
		(frm.doc.asset_models).forEach(i =>{
			item = item+"\n"+i.asset_model      
			})
		frm.set_df_property('select_item','options', item); 
	},
	insert_records:function(frm){
		var args={};
		if (frm.doc.select_item){
			args["item_code"]=frm.doc.select_item
			args["asset_models"]=frm.doc.asset_models
		}
		// if (frm.doc.batch){
		// 	args["batch"]=frm.doc.batch
		// }
		// if (frm.doc.warehouse){
		// 	args["warehouse"]=frm.doc.warehouse
		// }
		frappe.call({
            method: "mfi_customization.mfi.doctype.asset_delivery_note.asset_delivery_note.get_serial_nos",
            args:{"filters":args},
            callback: function(r) {
				frm.clear_table("model_serial_nos");
				(r.message).forEach(element => {
				var c = frm.add_child("model_serial_nos")
				c.serial_no=element.name
				c.asset_model=element.item_code
				c.model_name=element.item_name
				c.warehouse=element.warehouse
				c.batch=element.batch_no
				})
				frm.refresh_field("model_serial_nos")
			}
		})
	},
	setup:function(frm){
		frm.set_query('stock_adjustment_account', function(doc) {
			return {
				filters: {
					"company":frm.doc.company
				}
			};
		});
		frm.set_query('fixed_asset_account', function(doc) {
			return {
				filters: {
					"company":frm.doc.company
				}
			};
		});
		frm.set_query('client_location', "model_serial_nos" ,function(doc) {
			return {
				filters: {
					"company":frm.doc.company
				}
			};
		});
		frm.set_query('serial_no', "model_serial_nos" ,function(doc) {
			return {
				filters: {
					"status":"Active"
				}
			};
		});
		frm.set_query('location', "location_wise_technician" ,function(doc) {
			return {
				filters: {
					"company":frm.doc.company
				}
			};
		});
		frm.set_query('technician_name', "location_wise_technician" ,function(doc) {
			return {
				query:"mfi_customization.mfi.doctype.asset_delivery_note.asset_delivery_note.get_company_users",
				filters: {
					"company":frm.doc.company
				}
			};
		});
		frm.set_query('batch', function(doc) {
			return {
				filters: {
					"item":frm.doc.select_item
				}
			};
		});
		frm.set_query('warehouse', function(doc) {
			return {
				filters: {
					"company":frm.doc.company
				}
			};
		});
	},
});

frappe.ui.form.on('Asset Models Item','asset_model',function(frm){
			
	let item = '';
	(frm.doc.asset_models).forEach(i =>{
		   item = item+"\n"+i.asset_model      
		})
	frm.set_df_property('select_item','options', item); 

	
});
