frappe.ui.form.on('Quotation', {
    refresh:function(frm){
        if(frm.doc.items){
			let parent = '';
  			(frm.doc.items).forEach(i =>{
       		parent = parent+"\n"+i.item_code      
   		 })
    		frm.set_df_property('select_item','options', parent); 

		}
        frm.fields_dict['compatible_accessories_list'].grid.add_custom_button('Add Mutiple Accessories', () => {
            frm.trigger("set_accessories_dialog");
        })
        frm.fields_dict['compatible_toner_list'].grid.add_custom_button('Add Mutiple Toner', () => {
            frm.trigger("set_toner_dialog");
        })
    },
    set_accessories_dialog:function(frm){
        frappe.call({
            method: "mfi_customization.mfi.doctype.quotation.get_accessories_items",
            args:{
                "item":frm.doc.select_item,
            },
            callback: function(r) {
                if(r.message) {
                    let table_values = [];
                    $.each(r.message || [], function(i, row) {
                        table_values.push(row)
                    });
                    var d = new frappe.ui.Dialog({
                        'fields': [
                            {fieldname:'accessories_item',label:'Default Accessories Item',fieldtype:'Table',
                                fields: [
                                    {
                                        fieldtype:'Link',
                                        fieldname:'accessory',
                                        label: __('Accessory'),
                                        options:'Item',
                                        in_list_view:1,
                                    },
                                    {
                                        fieldtype:'Data',
                                        fieldname:'accessory_name',
                                        label: __('Accessory Name'),
                                        in_list_view:1,
                                    }
                                ],
                                data: table_values,
                                in_place_edit: true,
                                get_data: function() {
                                    return table_values;
                                }
                            },
                        ],
                        primary_action: function(){
                            d.hide();
                            (d.get_values()['accessories_item']).forEach(element => {
                                var c = frm.add_child("compatible_accessories_list")
                                c.accessory=element.accessory
                                c.accessory_name=element.accessory_name
                                c.qty=1
                                c.yeild=element.yeild
                                c.compatible_with=frm.doc.select_item
                            })
                            frm.refresh_field("compatible_accessories_list")
                        },
                        primary_action_label: __('Insert')
                    
                    });
                    d.show();
                }
            }
    })
    },
    set_toner_dialog:function(frm){
        frappe.call({
            method: "mfi_customization.mfi.doctype.quotation.get_toner_items",
            args:{
                "item":frm.doc.select_item,
            },
            callback: function(r) {
                if(r.message) {
                    let table_values = [];
                    $.each(r.message || [], function(i, row) {
                        table_values.push(row)
                    });
                    var d = new frappe.ui.Dialog({
                        'fields': [
                            {fieldname:'toner_item',label:'Compatible Toner Item',fieldtype:'Table',
                                fields: [
                                    {
                                        fieldtype:'Link',
                                        fieldname:'toner',
                                        label: __('Toner'),
                                        options:'Item',
                                        in_list_view:1,
                                    },
                                    {
                                        fieldtype:'Data',
                                        fieldname:'toner_name',
                                        label: __('Toner Name'),
                                        in_list_view:1,
                                    }
                                ],
                                data: table_values,
                                in_place_edit: true,
                                get_data: function() {
                                    return table_values;
                                }
                            },
                        ],
                        primary_action: function(){
                            d.hide();
                            (d.get_values()['toner_item']).forEach(element => {
                                var c = frm.add_child("compatible_toner_list")
                                c.toner=element.toner
                                c.toner_name=element.toner_name
                                c.qty=1
                                c.yeild=element.yeild
                                c.compatible_with=frm.doc.select_item
                            })
                            frm.refresh_field("compatible_toner_list")
                        },
                        primary_action_label: __('Insert')
                    
                    });
                    d.show();
                }
            }
    })
    }
})

frappe.ui.form.on('Quotation Item','item_code',function(frm){
			
        let parent = '';
        (frm.doc.items).forEach(i =>{
       		parent = parent+"\n"+i.item_code      
   		 })
    	frm.set_df_property('select_item','options', parent); 

		
});