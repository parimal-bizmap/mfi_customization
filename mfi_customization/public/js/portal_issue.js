frappe.web_form.on('location', (field, value) => { 
    if (frappe.web_form.get_field('location').value){ 
        filterAsset(frappe.web_form.get_field('location').value,`api/resource/Asset?filters=[["Asset","location","=","${frappe.web_form.get_field('location').value}"]]`); 
        filterSrNo(frappe.web_form.get_field('location').value,`api/resource/Asset%20Serial%20No?filters=[["Asset%20Serial%20No","location","=","${frappe.web_form.get_field('location').value}"]]`); 
        } 
    else{ 
        filterAsset(frappe.web_form.get_field('location').value,`api/resource/Asset`); 
        filterSrNo(frappe.web_form.get_field('location').value,`api/resource/Asset%20Serial%20No`); 
        } }) 

function filterAsset(location,url) { 
        $.ajax({ url:url, success: function(result) 
        { 
            var options = [] 
            for (var i = 0; i < result.data.length; i++) 
            { 
                options.push({ 'label': result.data[i].name, 'value': result.data[i].name }) 
            } 
            var field = frappe.web_form.get_field('asset'); 
            field._data = options; field.refresh();
        } }); 
    } 
    
function filterSrNo(location,url) 
    { 
        $.ajax({ url:url, success: function(result) 
        { 
            var options = [] 
            for (var i = 0; i < result.data.length; i++) 
            { 
                options.push({ 'label': result.data[i].name, 'value': result.data[i].name }) 
            } 
            var field = frappe.web_form.get_field('serial_no'); 
            field._data = options; field.refresh(); 
        } }); 
    } 
frappe.web_form.on('asset', (field, value) => { 
    getsrno(frappe.web_form.get_field('asset').value) 
    }) 
    
function getsrno(asset) { 
    $.ajax({ url:`api/resource/Asset%20Serial%20No?filters=[["Asset%20Serial%20No","asset","=","${asset}"]]`, success: function(result) { 
        if (result.data){ 
            frappe.web_form.set_value(['serial_no'], result.data[0].name) 
        } } }); 
    }
    