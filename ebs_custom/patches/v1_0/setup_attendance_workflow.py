import frappe


def execute():
	if frappe.db.exists("Workflow", "Branch Attendance Approval Workflow"):
		return

	workflow = frappe.get_doc(
		{
			"doctype": "Workflow",
			"workflow_name": "Branch Attendance Approval Workflow",
			"document_type": "Branch Attendance Approval",
			"is_active": 1,
			"override_status": 0,
			"send_email_alert": 1,
			"workflow_state_field": "workflow_state",
			"states": [
				{
					"state": "Draft",
					"doc_status": "0",
					"allow_edit": "Branch Manager",
				},
				{
					"state": "Pending Approval",
					"doc_status": "0",
					"allow_edit": "Branch Manager",
				},
				{
					"state": "Approved",
					"doc_status": "0",
					"allow_edit": "All",
				},
				{
					"state": "Rejected",
					"doc_status": "0",
					"allow_edit": "Branch Manager",
				},
			],
			"transitions": [
				{
					"state": "Draft",
					"action": "Submit for Approval",
					"next_state": "Pending Approval",
					"allowed": "Branch Manager",
					"allow_self_approval": 1,
				},
				{
					"state": "Pending Approval",
					"action": "Approve",
					"next_state": "Approved",
					"allowed": "Branch Manager",
					"allow_self_approval": 1,
				},
				{
					"state": "Pending Approval",
					"action": "Reject",
					"next_state": "Rejected",
					"allowed": "Branch Manager",
					"allow_self_approval": 1,
				},
				{
					"state": "Rejected",
					"action": "Reset to Draft",
					"next_state": "Draft",
					"allowed": "Branch Manager",
					"allow_self_approval": 1,
				},
			],
		}
	)
	workflow.insert(ignore_permissions=True)
	frappe.db.commit()
