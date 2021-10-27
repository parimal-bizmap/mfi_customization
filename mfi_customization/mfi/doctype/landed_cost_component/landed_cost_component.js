// Copyright (c) 2021, bizmap technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Landed Cost Component', {
	setup: function(frm) {
		frm.fields_dict['landed_cost_component_account'].grid.get_field('account').get_query = function(doc, cdt, cdn) {
            var child = locals[cdt][cdn];
            return {    
                filters:{
					"account_type": ['in', ["Tax", "Chargeable", "Income Account", "Expenses Included In Valuation", "Expenses Included In Asset Valuation"]],
					"company":child.company
				}
            }
        }
	}
});