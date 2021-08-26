// Copyright (c) 2021, bizmap technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Machine Reading Tool', {
	project: function(frm) {
		console.log("@@@@@@@@@@frm.doc.project", frm.doc.project)
		frm.doc.show_submit = false;
		if(frm.doc.project) {
			console.log("@@@@@@@@@@frm.doc.project", frm.doc.project)
			// if (!frm.doc.student_group)
			// 	return
			frappe.call({
				method: "mfi_customization.mfi.doctype.machine_reading_tool.machine_reading_tool.get_machine_reading",
				args: {
					"project": frm.doc.project
				},
				callback: function(r) {
					if (r.message) {
						console.log("!!!!!!!!!!!!!!!!! r.message", r.message)
						// frm.doc.students = r.message;
						frm.events.render_table(frm, r.message);
						for (let value of r.message) {
							if (!value.docstatus) {
								frm.doc.show_submit = true;
								break;
							}
						}
						// frm.events.submit_result(frm);
					}
				}
			});
		}
	},
	render_table: function(frm, result) {
		console.log("@@@@@@@@@@result ", result)
		$(frm.fields_dict.reading_items.wrapper).empty();
		let project = frm.doc.project;
		frm.events.get_reading(frm, result);



		// frappe.call({
		// 	method: "erpnext.education.api.get_assessment_details",
		// 	args: {
		// 		project: project
		// 	},
		// 	callback: function(r) {
		// 		frm.events.get_marks(frm, r.message);
		// 	}
		// });
	},
	get_reading: function(frm, result_list) {
		console.log("////////////result_list", result_list)
		let max_total = 0;
		result_list.forEach(function(c) {
			max_total += c.total
		});
		var result_table = $(frappe.render_template('machine_reading_tool', {
			frm: frm,
			project: frm.doc.project,
			machine_reading_list: result_list,
			max_total: max_total
		}));
		result_table.appendTo(frm.fields_dict.reading_items.wrapper);

		result_table.on('change', 'input', function(e) {
			let $input = $(e.target);
			// let reading = $input.data();
			let asset = $input.data().asset;
			// let max_score = $input.data().maxScore;
			let value = $input.val();
			if(value < 0) {
				$input.val(0);
			}
			 // else if(value > max_score) {
			// 	$input.val(max_score);
			// }
			let total_reading = 0;
			let machine_reading = {};
			machine_reading["asset_reading"] = {};
			result_table.find(`input[data-asset=${asset}].asset-result-data`)
				.each(function(el, input) {
					debugger;
					console.log("#333el ", el)
					let $input = $(input);
					console.log("$input.data()",$input.data())
					console.log($input[0].dataset['asset']);
					let reading = $input.data().machine_reading_list;
					// let machine_type = $input.data().machine_type;
					// let value = parseFloat($input.val());
					// let colour_reading = $input.data().colour_reading;
					console.log("!!!!!!!!!!! reading", reading)

					// let black_and_white_reading = $input.data().black_and_white_reading;
					// console.log("!!!!!!!!!!! black_and_white_reading", black_and_white_reading)
					
					let value = parseFloat($input.val());
                    console.log("!!!!!!!!!!! value", value)
					if (!Number.isNaN(value)) {
						machine_reading["asset_reading"][reading] = value;
						// machine_reading["asset_reading"][colour_reading] = value.colour_reading;
					}
					total_reading += value.total;
			});
			console.log("asset_reading", machine_reading["asset_reading"])
			if(!Number.isNaN(total_reading)) {
				result_table.find(`span[data-asset=${asset}].total-reading`).html(total_reading);
			    console.log("!!!!!!!!!!!! total_reading",total_reading)
			}console.log("result_list.length", result_list.length)
			console.log("asset_reading_length", Object.keys(machine_reading["asset_reading"]).length)
			if (Object.keys(machine_reading["asset_reading"]).length > 1) {
				// machine_reading["readings"] = readings;
				machine_reading["total_reading"] = total_reading;
				result_table.find(`[data-asset=${asset}].result-black_and_white_reading`)
					.each(function(el, input){
					machine_reading["asset_reading"][black_and_white_reading] = $(input).val();
				});
				result_table.find(`[data-asset=${asset}].result-colour_reading`)
					.each(function(el, input){
					machine_reading["asset_reading"][colour_reading] = $(input).val();
				});
				result_table.find(`[data-asset=${asset}].result-comment`)
					.each(function(el, input){
					machine_reading["comment"] = $(input).val();
				});
				console.log('!!!!!!!!!!!!!!machine_reading', machine_reading)
				frappe.call({
					method: "mfi_customization.mfi.doctype.machine_reading_tool.machine_reading_tool.mark_machine_reading",
					args: {
						"project": frm.doc.project,
						"machine_reading": machine_reading
					},
					callback: function(r) {
						let reading_result = r.message;
						console.log("@@@@@@@ reading_result",reading_result)
						if (!frm.doc.show_submit) {
							frm.doc.show_submit = true;
							frm.events.submit_result;
						}
						for (var criteria of Object.keys(reading_result.details)) {
							result_table.find(`[data-criteria=${criteria}][data-readings=${reading_result
								.readings}].readings-result-grade`).each(function(e1, input) {
									$(input).html(reading_result.details[criteria]);
							});
						}
						result_table.find(`span[data-readings=${reading_result.readings}].total-score-grade`).html(reading_result.grade);
						let link_span = result_table.find(`span[data-readings=${reading_result.student}].total-result-link`);
						$(link_span).css("display", "block");
						$(link_span).find("a").attr("href", "/app/assessment-result/"+reading_result.name);
					}
				});
			}
		});
	}



});
