import { createResource } from "frappe-ui"
import { employeeResource } from "./employee"

const transformAdvanceData = (data) => {
	return data.map((claim) => {
		claim.doctype = "Employee Advance"
		return claim
	})
}

export const advanceBalance = createResource({
	url: "hrms.api.get_employee_advance_balance",
	auto: true,
	cache: "hrms:employee_advance_balance",
	transform(data) {
		return transformAdvanceData(data)
	},
})

export const myAdvances = createResource({
	url: "ebs_custom.api.pwa.get_employee_advances",
	params: {
		employee: employeeResource.data.name,
		limit: 10,
	},
	auto: true,
	cache: "hrms:my_advances",
	transform(data) {
		return transformAdvanceData(data)
	},
	onSuccess() {
		advanceBalance.reload()
	},
})

export const teamAdvances = createResource({
	url: "ebs_custom.api.pwa.get_employee_advances",
	params: {
		employee: employeeResource.data.name,
		approver_id: employeeResource.data.user_id,
		for_approval: 1,
		limit: 10,
	},
	auto: true,
	cache: "hrms:team_advances",
	transform(data) {
		return transformAdvanceData(data)
	},
})
