# Copyright (c) 2023, Sudharsanan Ashok and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.docstatus import DocStatus

class LibraryTransaction(Document):
	def before_submit(self):
		if(self.type == "Issue"):
			self.validate_membership() 
			self.validate_maxlimit()
			article = frappe.get_doc("Article", self.article)

			if article.status == "Issued":
				frappe.throw("This article is already issued by another member")
			else:
				article.status = "Issued"
				article.save()
			
		elif(self.type == "Return"):
			article = frappe.get_doc("Article", self.article)

			if article.status == "Available":
				frappe.throw("Article cannot be returned without being issued")
			else:
				article.status = "Available"
				article.save()

	def validate_maxlimit(self):
		max_articles = frappe.db.get_single_value("Library Settings", "max_articles")
		count = frappe.db.count(
			"Library Transaction",
			{
				"library_member": self.library_member,
				"type": "Issue",
				"docstatus": DocStatus.submitted()
			}
		)
		if (count >= max_articles):
			frappe.throw("Maximum limit reached for issuing article")
			
	def validate_membership(self):
		exists = frappe.db.exists(
			"Library Membership",
			{
				"library_member": self.library_member,
				"docstatus": DocStatus.submitted(),
				"from_date": ("<", self.date),
				"to_date": (">", self.date)
			}
		)
		if not exists: frappe.throw("This member is not a valid member")
