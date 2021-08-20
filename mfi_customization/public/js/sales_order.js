// frappe.ui.form.on('Sales Order', {
// 	purchase_order: function(frm) {
// 		if(frm.doc.purchase_order){
// 			frappe.call({
// 				method: "frappe.client.get_value",
// 				args: {
// 					doctype: "Purchase Order",
// 					filters: {"name": frm.doc.purchase_order},
// 					fieldname: "company"
// 				},
// 				callback: function(r){
// 					if(r.message.company){
// 						var company = r.message.company 
// 						// alert("???????????????????company",company)
// 						frm.set_value('company', 'MFI International FZE')
// 						frm.set_query('customer', function(doc) {
// 							return {
// 								filters: [["Customer", "represents_company", "=", company]]
// 							};
// 						});
// 					}
// 				}
// 			});
// 		}
// 	}
// });