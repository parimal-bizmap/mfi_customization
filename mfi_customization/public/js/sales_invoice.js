
frappe.ui.form.on('Sales Invoice', {
    project:function(frm){
        (frm.doc.items).forEach(element => {
            if(frm.doc.project){
                element.project = frm.doc.project;
            }
            
        });
    },
    cost_center:function(frm){
        (frm.doc.items).forEach(element => {
            if(frm.doc.cost_center){
                element.cost_center = frm.doc.cost_center;
            }
            
        });
    }


});

frappe.ui.form.on("Sales Invoice Item", "item_code", function(frm, cdt, cdn) {
    var d = locals[cdt][cdn];
    
    if(frm.doc.project){
        
        d.project= frm.doc.project; 
        refresh_field("project", d.name, d.parentfield);
       
      }
      
    if(frm.doc.cost_center){
        
        d.cost_center= frm.doc.cost_center; 
        refresh_field("cost_center", d.name, d.parentfield);
       
      }
      
});
