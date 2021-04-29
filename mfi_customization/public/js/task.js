frappe.ui.form.on('Task', {
asset:function(frm){
    frappe.db.get_value('Asset',{'name':frm.doc.asset},['asset_name','location'])
    .then(({ message }) => {
        frm.set_value('asset_name',message.asset_name);
        frm.set_value('location',message.location);
    });                                                                                  
},
refresh:function(frm){
    frm.add_custom_button('Material Request', () => {
        frappe.model.open_mapped_doc({
            method: "mfi_customization.mfi.doctype.task.make_material_req",
            frm: me.frm
        })

        },
        __('Make')
        )
        frm.set_query("completed_by", function() {
            console.log("**************888");
            
                return {
                    query: 'mfi_customization.mfi.doctype.task.get_tech',
                    filters: {
                        "user":frappe.session.user
                    }
                };
            
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
  
},

validate:function(frm){
    // Assigning time on start and on complete
    
    if (frm.doc.completed_by && frm.doc.assign_date == null){
        frm.set_value("assign_date",frappe.datetime.now_datetime());
       
    };
    if (frm.doc.status == 'Working' && frm.doc.attended_date_time == null){
        frm.set_value("attended_date_time", frappe.datetime.now_datetime());
    };
    
    if (frm.doc.status == 'Completed'){
        frm.set_value("completion_date_time", frm.doc.modified);
    };
    // Validation for working and completion time
    if(!frm.doc.attended_date_time && frm.doc.status == 'Completed'){
        frm.set_value("completion_date_time","");
        frappe.throw("Status Cannot be complete before working")
    }

    

    frappe.call({
        method:
        "mfi_customization.mfi.doctype.task.set_readings",
        args: {
            project: frm.doc.project,
            asset : frm.doc.asset
        },
        callback: (r) => {
            if(r.message) {
   
                cur_frm.clear_table("last_readings");
                r.message.forEach(function(element) {
                var c = cur_frm.add_child("last_readings");
                c.date = element.date;
                c.type = element.type;
                c.asset = element.asset;
                c.reading = element.black_white;
                c.reading_2 = element.colour;
            });
            refresh_field("last_readings"); 
}}
    })
    


}
})
cur_frm.dashboard.add_transactions([
	{
		'items': [
			'Material Request'
		],
		'label': 'Others'
	},
]);

