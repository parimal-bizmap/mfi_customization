// Copyright (c) 2021, bizmap technologies and contributors
// For license information, please see license.txt
frappe.ui.form.on('Machine Reading Tool', {
	refresh:function(frm){
		frm.set_value("project",'')
		frm.disable_save();
		frm.page.clear_indicator();
		frm.set_value("reading_date",frappe.datetime.get_today())
		frm.set_value("reading_type",'Black & White')
	},
	project: function(frm) {
		frm.doc.show_submit = false;
		if(frm.doc.project) {
			frappe.call({
				method: "mfi_customization.mfi.doctype.machine_reading_tool.machine_reading_tool.get_machine_reading",
				args: {
					"project": frm.doc.project,
					"reading_date":frm.doc.reading_date,
					"reading_type":frm.doc.reading_type
				},
				callback: function(r) {
					if (r.message) {
						frm.events.render_table(frm, r.message);
						for (let value of r.message) {
							if (!value.docstatus) {
								frm.doc.show_submit = true;
								break;
							}
						}
						frm.events.submit_result(frm);
					}
				}
			});
		}
	},

	render_table: function(frm,asset_list) {
		$(frm.fields_dict.reading_items.wrapper).empty();
		frm.events.get_marks(frm,asset_list);
	},

	get_marks: function(frm,asset_list) {
		var result_table = $(frappe.render_template('machine_reading_tool', {
			frm: frm,
			assets: asset_list,
		}));
		result_table.appendTo(frm.fields_dict.reading_items.wrapper);
		console.log(result_table)
		result_table.on('change', 'input', function(e) {
			let $input = $(e.target);
			let asset = $input.data().asset;
			let max_score = $input.data().maxScore;
			let value = $input.val();
			if(value < 0) {
				$input.val(0);
			} else if(value > max_score) {
				$input.val(max_score);
			}
			let total_score = 0;
			let asset_readings = {};
	
			asset_readings["reading_details"] = {}
			asset_readings["reading_details"]["asset"] = asset;
			result_table.find(`[data-asset=${asset}].result-bw-reading`).each(function(el, input){
				asset_readings["reading_details"]["bw_reading"] = $(input).val();
			});
			result_table.find(`[data-asset=${asset}].result-colour-reading`).each(function(el, input){
				asset_readings["reading_details"]["colour"] = $(input).val();
			});
			result_table.find(`[data-asset=${asset}].result-reading_date`).each(function(el, input){
				asset_readings["reading_details"]["reading_date"] = $(input).val();
			});
			result_table.find(`[data-asset=${asset}].result-reading_type`).each(function(el, input){
				asset_readings["reading_details"]["reading_type"] = $(input).val();
			});
			result_table.find(`[data-asset=${asset}].result-total_reading`).each(function(el, input){
				asset_readings["reading_details"]["total_reading"] = $(input).val();
			});
			frappe.call({
				method: "mfi_customization.mfi.doctype.machine_reading_tool.machine_reading_tool.create_machine_reading",
				args: {
					"readings": asset_readings
				},
				callback: function(r) {
					console.log(r.message)
					// let assessment_result = r.message;
					// if (!frm.doc.show_submit) {
					// 	frm.doc.show_submit = true;
					// 	frm.events.submit_result;
					// }
					// for (var criteria of Object.keys(assessment_result.details)) {
					// 	result_table.find(`[data-criteria=${criteria}][data-asset=${assessment_result
					// 		.asset}].asset-result-grade`).each(function(e1, input) {
					// 			$(input).html(assessment_result.details[criteria]);
					// 	});
					// }
					// result_table.find(`span[data-asset=${assessment_result.asset}].total-score-grade`).html(assessment_result.grade);
					// let link_span = result_table.find(`span[data-asset=${assessment_result.asset}].total-result-link`);
					// $(link_span).css("display", "block");
					// $(link_span).find("a").attr("href", "/app/assessment-result/"+assessment_result.name);
				}
			});
			// if (Object.keys(asset_readings["reading_details"]).length === criteria_list.length) {
			// 	asset_readings["asset"] = asset;
			// 	asset_readings["total_score"] = total_score;


			// 	result_table.find(`[data-asset=${asset}].result-comment`)
			// 		.each(function(el, input){
			// 		asset_readings["comment"] = $(input).val();
			// 	});
			// 	console.log(asset_readings)
			// 	frappe.call({
			// 		method: "erpnext.education.api.mark_assessment_result",
			// 		args: {
			// 			"assessment_plan": frm.doc.assessment_plan,
			// 			"scores": asset_readings
			// 		},
			// 		callback: function(r) {
			// 			let assessment_result = r.message;
			// 			if (!frm.doc.show_submit) {
			// 				frm.doc.show_submit = true;
			// 				frm.events.submit_result;
			// 			}
			// 			for (var criteria of Object.keys(assessment_result.details)) {
			// 				result_table.find(`[data-criteria=${criteria}][data-asset=${assessment_result
			// 					.asset}].asset-result-grade`).each(function(e1, input) {
			// 						$(input).html(assessment_result.details[criteria]);
			// 				});
			// 			}
			// 			result_table.find(`span[data-asset=${assessment_result.asset}].total-score-grade`).html(assessment_result.grade);
			// 			let link_span = result_table.find(`span[data-asset=${assessment_result.asset}].total-result-link`);
			// 			$(link_span).css("display", "block");
			// 			$(link_span).find("a").attr("href", "/app/assessment-result/"+assessment_result.name);
			// 		}
			// 	});
			// }
		});
	},

	submit_result: function(frm) {
		if (frm.doc.show_submit) {
			console.log("******************")
			frm.page.set_primary_action(__("Submit"), function() {
				frappe.call({
					method: "mfi_customization.mfi.doctype.machine_reading_tool.machine_reading_tool.create_machine_reading",
					args: {
						"readings": asset_readings
					},
					callback: function(r) {
						if (r.message) {
							frappe.msgprint(__("{0} Result submittted", [r.message]));
						} else {
							frappe.msgprint(__("No Result to submit"));
						}
						frm.events.project(frm);
					}
				});
			});
		}
		else {
			frm.page.clear_primary_action();
		}
	}
});

