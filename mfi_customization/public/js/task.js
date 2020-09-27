frappe.ui.form.on('Task', {
asset:function(frm){
    frappe.db.get_value('Asset',{'name':frm.doc.asset},['asset_name','location'])
    .then(({ message }) => {
        frm.set_value('asset_name',message.asset_name);
        frm.set_value('location',message.location);
    });                                                                                  
}
})