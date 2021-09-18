{% include 'erpnext/public/js/controllers/buying.js' %};

frappe.ui.form.on('Material Request', {
    schedule_date:function(frm){
        frm.set_query("item_code", "items", function() {
			return {
				query: "mfi_customization.mfi.doctype.material_request.item_query",
				filters:{
					"item_group":["IN",["Consumable","Spares"]]
				}
			}
		});
    },
	onload: function ( frm ) {
        frm.set_value("material_request_type","Material Issue")
        frm.set_query("item_code", "items", function(doc, cdt, cdn) {
			return {
				query: "erpnext.controllers.queries.item_query"
			}
		});
        if (frm.doc.__islocal) {
            frappe.call({
                method: "mfi_customization.mfi.doctype.material_request.get_approver",
                args: {
                    "user": frappe.session.user
                },
                callback: function(r) {
                    frm.set_value('approver',r.message["approver"]);	
                    frm.set_value('approver_name',r.message["approver_name"]);				
                }
        
        });
        frappe.call({
            method: 'mfi_customization.mfi.doctype.material_request.run',
            type: 'GET',
            args: {
                report_name: frm.doc.report_name,
                filters: frm.doc.filters,
            },
            callback: function(r) {
                frm.events.render_table(frm, r.message);
            } 
        });
        }

    },
    get_items:function(frm){
        Object.keys(cur_frm.doc.items).forEach(d => {
            var row=frm.add_child("item_shipment");
            row.item=cur_frm.doc.items[d].item_code
            row.qty=cur_frm.doc.items[d].qty
        });
        frm.refresh_field("item_shipment")
    },
    render_table: function(frm,response) {
		$(frm.fields_dict.requisition_analysis_html.wrapper).empty();
		frm.events.get_table(frm,response);
	},
    get_table: function(frm,response) {
		var result_table = $(frappe.render_template('material_request_table', {
			frm: frm,
			columns: response.columns,
            result: response.result,
            price_list:response.price_list,
            item_details:response.item_details,
            doc:frm.doc
		}));
		result_table.appendTo(frm.fields_dict.requisition_analysis_html.wrapper);
    },
    update_items:function(frm){
        frm.set_value('items',[]);
        frm.set_value('item_shipment',[]);
        let html_values=frm.fields_dict.requisition_analysis_html.wrapper;
        frappe.call({
            method: 'mfi_customization.mfi.doctype.material_request.run',
            type: 'GET',
            args: {
                report_name: frm.doc.report_name,
                filters: frm.doc.filters,
            },
            callback: function(r) {
                if(r.message){
                    var qty_field_mapping={"Courier":"courier_qty","AIR":"air_qty","SEA":"sea_qty"};
                    ((r.message).result).forEach(resp => {
                        var item_qty=0;
                        var uom="";
                        // $(html_values).find(`[data-item_code="${resp.part_number}"].result-carton_qty`).each(function(el, input){
                        // })
                        $(html_values).find(`[data-item_code="${resp.part_number}"].result-uom`).each(function(el, input){
                            uom=$(input).val()
                        })
                        Object.keys(qty_field_mapping).forEach(shipment_type=>{
                            $(html_values).find(`[data-item_code="${resp.part_number}"].result-${qty_field_mapping[shipment_type]}`).each(function(el, input){
                                if ($(input).val()>0){
                                    var row=frm.add_child("item_shipment");
                                    row.item=resp.part_number
                                    row.shipment_type=shipment_type
                                    row.qty=$(input).val()
                                    row.uom=uom;
                                    item_qty+=parseFloat($(input).val())
                                }
                            });
                            frm.refresh_field("item_shipment");
                        });
                        if (item_qty>0){
                            var item_row=frm.add_child("items");
                            item_row.item_code=resp.part_number
                            item_row.item_name=resp.part_name
                            item_row.qty=item_qty
                            item_row.uom=uom
                            
                        }
                    }) 
                    frm.refresh_field("items");
                }
            } 
        });
    }
});
