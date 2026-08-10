# Copyright (c) 2026, Elite Business Company and contributors
# For license information, please see license.txt

"""Share existing pending Employee Advances with current-stage approver roles."""

import frappe

from ebs_custom.hr_requests.events.employee_advance import (
	ADVANCE_STATE_APPROVER_ROLE,
	_share_with_users,
)
from ebs_custom.hr_requests.utils.notifications import get_users_by_roles


def execute():
	if not frappe.db.exists("DocType", "Employee Advance"):
		return
	if not frappe.db.has_column("Employee Advance", "workflow_state"):
		return

	pending_states = list(ADVANCE_STATE_APPROVER_ROLE.keys())
	advances = frappe.get_all(
		"Employee Advance",
		filters={
			"docstatus": 0,
			"workflow_state": ("in", pending_states),
		},
		fields=["name", "workflow_state", "employee"],
	)

	for row in advances:
		role = ADVANCE_STATE_APPROVER_ROLE.get(row.workflow_state)
		if not role:
			continue
		users = get_users_by_roles([role])
		doc = frappe.get_doc("Employee Advance", row.name)
		_share_with_users(doc, users)
