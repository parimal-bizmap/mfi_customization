# -*- coding: utf-8 -*-
# Copyright (c) 2021, bizmap technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document
from frappe.utils import flt

class MachineReading(Document):
	def validate(self):
		self.total=(flt(self.black_and_white_reading)+flt(self.colour_reading))
