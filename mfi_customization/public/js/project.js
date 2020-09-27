cur_frm.dashboard.add_transactions([
	{
		'items': [
			'Asset',
			'Asset Maintenance',
			'Asset Maintenance Log',
			'Asset Repair'
		],
		'label': 'Others'
	},
]);



frappe.ui.form.on('Project', {
	setup:function(frm){
		frm.set_query("asset", "machine_readings", function() {
			var asset_list=[]
			cur_frm.doc.asset_list.map((value) => {
				asset_list.push(value.asset)
			})
			return {
				filters: {
					"name": ['in',asset_list]
				}
			}
		});
	},
	maintenance_team(frm){
		frm.set_value('maintainance_manager','')
		frm.set_value('manager_name','')
		frm.set_value('maintenance_team_member',[])
		frappe.call({
			method:"mfi_customization.mfi.doctype.project.fetch_asset_maintenance_team",
			args: {
				maintenance_team:frm.doc.maintenance_team
			},
				callback: function (data) {
					frm.set_value('maintainance_manager',data.message.manager)
					frm.set_value('manager_name',data.message.name)
					$.each(data.message.team_members_list || [], function (i, list) {
						var d = frm.add_child("maintenance_team_member");
						d['team_member']=list['member']
						d['maintenance_role']=list['role']
						d['full_name']=list['name']
					})
					cur_frm.refresh_field("maintenance_team_member")
				}
			})
	}
})

frappe.ui.form.on("Asset List", "asset", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	frappe.db.get_value("Asset", {"name":d.asset},["asset_name","location"], function(r){
		d.asset_name=r.asset_name
		d.location=r.location
		refresh_field("asset_list");
	})
});

frappe.ui.form.on("Asset Readings", "asset", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	frappe.db.get_value("Asset", {"name":d.asset},["asset_name"], function(r){
		d.asset_name=r.asset_name
		refresh_field("asset_list");
	})
});
