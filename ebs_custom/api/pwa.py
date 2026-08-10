# Copyright (c) 2026, Elite Business Company and contributors
# For license information, please see license.txt

import frappe

from hrms.api import (
	get_allowed_states_for_workflow,
	get_filters,
	get_workflow,
	get_workflow_state_field,
)


@frappe.whitelist()
def get_employee_advances(
	employee: str,
	approver_id: str | None = None,
	for_approval: bool = False,
	limit: int | None = None,
) -> list[dict]:
	"""PWA list API for Employee Advance (my requests + pending approvals).

	Mirrors hrms leave/expense for_approval behaviour for the Loan Approval workflow.
	"""
	if for_approval:
		approver_id = frappe.session.user
		if workflow := get_workflow("Employee Advance"):
			allowed_states = get_allowed_states_for_workflow(workflow, approver_id)
			if not allowed_states:
				return []

	filters = get_filters("Employee Advance", employee, approver_id, for_approval)
	fields = [
		"name",
		"employee",
		"employee_name",
		"status",
		"purpose",
		"advance_amount",
		"paid_amount",
		"claimed_amount",
		"return_amount",
		"posting_date",
		"currency",
		"company",
		"creation",
	]

	if workflow_state_field := get_workflow_state_field("Employee Advance"):
		fields.append(workflow_state_field)

	# Role-based workflows need ignore_permissions so ESS user-permissions on
	# Employee do not hide pending approvals from managers.
	advances = frappe.get_list(
		"Employee Advance",
		fields=fields,
		filters=filters,
		order_by="posting_date desc",
		limit=limit,
		ignore_permissions=bool(for_approval),
	)

	if workflow_state_field:
		for advance in advances:
			advance["workflow_state_field"] = workflow_state_field

	return advances
