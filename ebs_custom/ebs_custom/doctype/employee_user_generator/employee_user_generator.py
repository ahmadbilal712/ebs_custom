# Copyright (c) 2026, EBS and contributors
# For license information, please see license.txt

import random

import frappe
from frappe.model.document import Document
from frappe.utils import cint, cstr
from frappe.utils.password import update_password


SELF_SERVICE_ROLE = "Employee Self Service"


class EmployeeUserGenerator(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from ebs_custom.ebs_custom.doctype.employee_user_generator_item.employee_user_generator_item import EmployeeUserGeneratorItem
		from frappe.types import DF

		company: DF.Link | None
		employee_list: DF.Table[EmployeeUserGeneratorItem]
		naming_series: DF.Literal["EUG-.YYYY.-.MM.-.DD.-.####"]
	# end: auto-generated types

	pass


@frappe.whitelist()
def get_employees(docname):
	doc = frappe.get_doc("Employee User Generator", docname)

	filters = {"status": "Active"}
	if doc.company:
		filters["company"] = doc.company

	employees = frappe.get_all(
		"Employee",
		filters=filters,
		fields=["name", "employee_name", "user_id"],
		order_by="name asc",
	)

	doc.set("employee_list", [])

	for emp in employees:
		last = frappe.get_all(
			"Employee User Generator Item",
			filters={"employee": emp.name},
			fields=["status", "user", "password", "message"],
			order_by="creation desc",
			limit=1,
		)

		last = last[0] if last else {}

		doc.append(
			"employee_list",
			{
				"employee": emp.name,
				"employee_name": emp.employee_name,
				"select": 0,
				"status": last.get("status") or ("Created" if emp.user_id else "Pending"),
				"user": last.get("user") or emp.user_id or "",
				"password": last.get("password") or "",
				"message": last.get("message") or "",
			},
		)

	doc.save(ignore_permissions=True)
	frappe.db.commit()

	return "Employees loaded successfully."

@frappe.whitelist()
def create_users(name):
	_check_permission()

	doc = frappe.get_doc("Employee User Generator", name)

	if not doc.employee_list:
		frappe.throw("No employees in the list. Click Get Employees, then Save.")

	used_codes = set()
	created = skipped = failed = 0

	for row in doc.employee_list:
		# Check field kabhi 0/1, kabhi True/False hota hai
		if not cint(row.select):
			continue

		try:
			emp = frappe.get_doc("Employee", row.employee)

			if emp.user_id:
				row.status = "Skipped"
				row.user = emp.user_id
				row.message = f"Already linked to user {emp.user_id}"
				row.select = 0
				skipped += 1
				continue

			if cstr(row.status) in ["Created", "Skipped"]:
				row.select = 0
				skipped += 1
				continue

			email = (emp.company_email or emp.prefered_email or "").strip()
			if not email:
				email = f"{emp.name.lower()}@ebc.com"

			if frappe.db.exists("User", email):
				row.status = "Skipped"
				row.message = f"User already exists: {email}"
				row.select = 0
				skipped += 1
				continue

			password = _make_password(emp.name, used_codes)

			user = frappe.get_doc(
				{
					"doctype": "User",
					"email": email,
					"first_name": emp.first_name or emp.employee_name or emp.name,
					"last_name": emp.last_name or "",
					"username": emp.name,
					"send_welcome_email": 0,
					"user_type": "System User",
				}
			)
			# 1. Create User
			user.insert(ignore_permissions=True)
			frappe.clear_messages()

			# 2. Link Employee with User
			emp.db_set("user_id", user.name)

			# 3. Set Password (Official Frappe API)
			update_password(user.name, password)

			# 4. Add Employee Self Service role AFTER Employee mapping
			user.add_roles(SELF_SERVICE_ROLE)

			row.status = "Created"
			row.user = user.name
			row.password = password
			row.message = "Created successfully"
			row.select = 1
			created += 1

		except Exception as e:
			row.status = "Failed"
			row.message = cstr(e)[:140]
			row.select = 0
			failed += 1
			frappe.log_error(frappe.get_traceback(), "Employee User Generator")

	doc.summary = f"Created: {created}, Skipped: {skipped}, Failed: {failed}"
	doc.save(ignore_permissions=True)
	frappe.db.commit()

	return doc.summary


def _make_password(employee_id, used_codes):
	# Ab sab users ka default password fixed hai
	return "User@123"


def _check_permission():
	roles = frappe.get_roles()
	if "System Manager" not in roles and "HR Manager" not in roles:
		frappe.throw("Only HR Manager / System Manager can create employee users.")