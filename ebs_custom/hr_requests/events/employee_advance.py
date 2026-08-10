# Copyright (c) 2026, Elite Business Company and contributors
# For license information, please see license.txt

"""PWA notifications + docshare for Employee Advance (Loan Approval Multi Level)."""

from __future__ import annotations

import frappe
from frappe import bold

from ebs_custom.hr_requests.utils.notifications import get_users_by_roles

# Role that must act when the document is IN this workflow state
ADVANCE_STATE_APPROVER_ROLE = {
	"Pending Line Manager": "Line Manager",
	"Pending HR Officer": "HR Officer",
	"Pending HR Manager": "HR Manager",
	"Pending Finance Manager": "Finance Manger",  # matches workflow fixture spelling
	"Pending Accounts Officer": "Accounts User",
	"Pending CEO": "CEO",
}

FINAL_APPROVED_STATES = {"Approved By Account Officer"}
FINAL_REJECTED_STATES = {"Rejected By Accounts Officer"}


def on_employee_advance_update(doc, method=None):
	if doc.is_new():
		return

	if not doc.has_value_changed("workflow_state"):
		return

	current_state = doc.get("workflow_state")
	if not current_state:
		return

	if current_state in FINAL_APPROVED_STATES or current_state in FINAL_REJECTED_STATES:
		_notify_employee_of_decision(doc, current_state)
		return

	role = ADVANCE_STATE_APPROVER_ROLE.get(current_state)
	if not role:
		return

	users = get_users_by_roles([role])
	_share_with_users(doc, users)
	_notify_approvers(doc, users, current_state)


def _share_with_users(doc, users: list[str]):
	"""Share so ESS managers can open/approve the doc from PWA despite Employee user-permissions."""
	employee_user = frappe.db.get_value("Employee", doc.employee, "user_id", cache=True)
	for user in users:
		if not user or user in ("Guest", "Administrator", employee_user):
			continue
		try:
			frappe.share.add_docshare(
				doc.doctype,
				doc.name,
				user,
				read=1,
				write=1,
				submit=1,
				flags={"ignore_share_permission": True},
			)
		except Exception:
			frappe.log_error(title=f"Employee Advance share failed: {doc.name} -> {user}")


def _notify_approvers(doc, users: list[str], current_state: str):
	from_user = frappe.db.get_value("Employee", doc.employee, "user_id", cache=True) or frappe.session.user
	employee_label = doc.get("employee_name") or doc.employee
	message = (
		f"{bold(employee_label)} raised a new {bold('Employee Advance')} for approval: "
		f"{doc.name} ({bold(current_state)})"
	)

	for user in users:
		if not user or user == from_user:
			continue
		_create_pwa_notification(
			from_user=from_user,
			to_user=user,
			message=message,
			doc=doc,
		)


def _notify_employee_of_decision(doc, current_state: str):
	to_user = frappe.db.get_value("Employee", doc.employee, "user_id", cache=True)
	if not to_user:
		return

	from_user = frappe.session.user
	if from_user == to_user:
		return

	from_user_name = frappe.db.get_value("User", from_user, "full_name", cache=True) or from_user
	status_label = "Approved" if current_state in FINAL_APPROVED_STATES else "Rejected"
	message = (
		f"{bold('Your')} {bold('Employee Advance')} {doc.name} has been "
		f"{bold(status_label)} by {bold(from_user_name)}"
	)
	_create_pwa_notification(
		from_user=from_user,
		to_user=to_user,
		message=message,
		doc=doc,
	)


def _create_pwa_notification(from_user: str, to_user: str, message: str, doc):
	if not frappe.db.exists("DocType", "PWA Notification"):
		return

	try:
		notification = frappe.new_doc("PWA Notification")
		notification.from_user = from_user
		notification.to_user = to_user
		notification.message = message
		notification.reference_document_type = doc.doctype
		notification.reference_document_name = doc.name
		notification.insert(ignore_permissions=True)
	except Exception:
		frappe.log_error(title=f"Employee Advance PWA Notification: {doc.name}")
