frappe.ui.form.on('Price List', {
    setup:function(frm){
		frm.fields_dict['countries'].grid.get_field('address').get_query = function(doc, cdt, cdn) {
            var child = locals[cdt][cdn];
            return {
				filters: {
					'link_doctype': 'Customer',
					'link_name': child.customer
				}
			}
        }
	}
})