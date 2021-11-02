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
                        },
                         {
                            "type": "report",
                            "name": "Response Time Technician",
                            "is_query_report": True,
                        },
                         {
                            "type": "report",
                            "name": "Call Data Monthly",
                            "is_query_report": True,
                        },
                         {
                            "type": "report",
                            "name": "Repetitive",
                            "is_query_report": True,
                        },
                        {
                            "type": "report",
                            "name": "Pending Spares",
                            "is_query_report": True,
                        },
                         {
                            "type": "report",
                            "name": "Response Time Client",
                            "doctype":"Issue",
                            "is_query_report": True,
                            
                        }
                        ]
            }

	]

	return config