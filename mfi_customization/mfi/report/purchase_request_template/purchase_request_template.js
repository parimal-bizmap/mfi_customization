// Copyright (c) 2016, bizmap technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Purchase Request Template"] = {
	"filters": [
		{
			"label":"Part Number",
			"fieldname":"part_number",
			"fieldtype":"Link",
			"options":"Item"	
		}

	]
};
