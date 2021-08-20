frappe.ui.form.on('Purchase Order', {
	on_submit:function(frm){
	    frappe.model.open_mapped_doc({
			method: "mfi_customization.mfi.doctype.purchase_order.set_data_sales_order",
			frm: cur_frm
		})
	}
});

