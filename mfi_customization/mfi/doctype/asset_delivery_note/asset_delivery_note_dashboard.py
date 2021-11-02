from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'asset_delivery_note',
		'transactions': [
            {
				'label': _('Asset'),
				'items': ['Asset','Asset Installation Note']
			},
		]
	}
