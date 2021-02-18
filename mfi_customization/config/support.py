from __future__ import unicode_literals
import frappe
from frappe import _

def get_data():
	config =  [
            {
                "label": _("Reports"),
                "icon": "fa fa-list",
                "items": [
                        {
                            "type": "report",
                            "name": "Issue Timelines",
                            "is_query_report": True,
                        },
                        {
                            "type": "report",
                            "name": "Customer Issue Status",
                            "is_query_report": True,
                        }
                        ]
            }

	]

	return config