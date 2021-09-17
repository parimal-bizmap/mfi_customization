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
        if (frm.doc.docstatus==1) {
             frm.add_custom_button(__('Create PO'), function () {
                get_items_from_MR(frm);
            }, __("Get Items From"));
        }

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
        }

    
     var get_items_from_MR = function(frm) {
            var me = this;
            let selected_project = '';
            const dialog = new frappe.ui.Dialog({
                title: __('Get items from MR'),
                fields: [
                    // {
                    //     fieldname:"material_request",
                    //     label: __("Material Request"),
                    //     fieldtype: "Link",
                    //     options: "Material Request",
                    //     reqd: true
                    // },
                    { fieldtype: 'Section Break'    },
                    { fieldtype: 'HTML', fieldname: 'results_area' }
                ]
            });
            var $wrapper;
            var $results;
            var $placeholder;
            dialog.$wrapper.find('.modal-content').css("width", "800px");
            $wrapper = dialog.fields_dict.results_area.$wrapper.append(`<div class="results"
                style="border: 1px solid #d1d8dd; border-radius: 3px; height: 300px; overflow: auto;"></div>`);
            $results = $wrapper.find('.results');
            $placeholder = $(`<div class="multiselect-empty-state">
                        <span class="text-center" style="margin-top: -40px;">
                            <i class="fa fa-2x fa-heartbeat text-extra-muted"></i>
                            <p class="text-extra-muted">No items found</p>
                        </span>
                    </div>`);
            // dialog.fields_dict["material_request"].df.onchange = () => {
                // var material_request = dialog.fields_dict.material_request.input.value;
                // if(material_request){
                    // selected_project = project;
                    var method = "mfi_customization.mfi.doctype.material_request.get_material_request";
                    // var args = {material_request: material_request};
                    var columns = (['name', 'schedule_date', 'status']);
                    get_material_request_items(frm, true, $results, $placeholder, method, columns);
                // }
                // else if(!material_request){
                    // selected_project = '';
                    // $results.empty();
                    // $results.append($placeholder);
                // }
            // }
            
            $results.on('click', '.list-item--head :checkbox', (e) => {
                $results.find('.list-item-container .list-row-check')
                    .prop("checked", ($(e.target).is(':checked')));
            });
            set_primary_action(frm, dialog, $results, true);
            dialog.show();
        };

var set_primary_action= function(frm, dialog, $results, project_tasks) {
    var me = this;
    dialog.set_primary_action(__('Create PO'), function() {
        let checked_values = get_checked_values($results);
        if(checked_values.length > 0){
            make_po(frm, checked_values, project_tasks);
            dialog.hide();
        }
        else{
                frappe.msgprint(__("Please select material request"));
        }
    });
};
        // $(".modal-content .btn btn-secondary btn-sm btn-modal-secondary").css("width", "800px");
        
    
var get_material_request_items = function(frm, project_tasks, $results, $placeholder, method, columns) {
    var me = this;
    $results.empty();

    frappe.call({
        method: method,
        callback: function(data) {
            if(data.message){
                $results.append(make_list_row(columns, project_tasks));
                for(let i=0; i<data.message.length; i++){
                    $results.append(make_list_row(columns, project_tasks, data.message[i]));
                }
            }else {
                $results.append($placeholder);
            }
        }
    });
};

var make_list_row= function(columns, project_tasks, result={}) {
            var me = this;
            // Make a head row by default (if result not passed)
            let head = Object.keys(result).length === 0;
            let contents = ``;
            columns.forEach(function(column) {
                contents += `<div class="list-item__content ellipsis">
                    ${
                        head ? `<span class="ellipsis">${__(frappe.model.unscrub(column))}</span>`

                        :(column !== "name" ? `<span class="ellipsis">${__(result[column])}</span>`
                            : `<a class="list-id ellipsis">
                                ${__(result[column])}</a>`)
                    }
                </div>`;
            })

            let $row = $(`<div class="list-item">
                <div class="list-item__content" style="flex: 0 0 10px;">
                    <input type="checkbox" class="list-row-check" ${result.checked ? 'checked' : ''}>
                </div>
                ${contents}
            </div>`);

            $row = list_row_data_items(head, $row, result, project_tasks);
            return $row;
        };

    var list_row_data_items = function(head, $row, result, project_tasks) {
        if(project_tasks){
            head ? $row.addClass('list-item--head')
                : $row = $(`<div class="list-item-container"
                    data-name = "${result.name}"
                    data-scheduled_date = "${result.scheduled_date}"
                    data-status = "${result.status}"
                    </div>`).append($row);
        }
        return $row
    };
    var get_checked_values= function($results) {
        return $results.find('.list-item-container').map(function() {
            let checked_values = {};
            if ($(this).find('.list-row-check:checkbox:checked').length > 0 ) {
                checked_values['name'] = $(this).attr('data-name');
                
                if($(this).attr('data-scheduled_date') != 'undefined'){
                    checked_values['scheduled_date'] = $(this).attr('data-scheduled_date');
                }
                else{
                    checked_values['scheduled_date'] = false;
                }
                if($(this).attr('data-status') != 'undefined'){
                    checked_values['status'] = $(this).attr('data-status');
                }
                else{
                    checked_values['status'] = false;
                }
                
                return checked_values;
            }
        }).get();
    };

    var make_po = function(frm, checked_values, project_tasks){
        print("///////make_po project_tasks", project_tasks)
        // if(project_tasks){
            frappe.call({
                method: "custom_app.custom_app.custom_script.project.project.set_project_tasks",
                args:{
                    doc: frm.doc,
                    checked_values: checked_values
                },
                callback: function(r) {
                    // r.message.forEach(function(element) {
                    //     var c = frappe.model.add_child(frm.doc, "Project Task","tasks");
                    //     c.task = element.task;
                    //     c.subject = element.subject;
                    //     c.start_date = element.start_date;
                    //     c.end_date = element.end_date;
                    //     c.duration_in_days = element.duration_in_days;
                    // });
                    // frm.refresh_field('tasks');
                }
            });
        // }
    };

}
});

   