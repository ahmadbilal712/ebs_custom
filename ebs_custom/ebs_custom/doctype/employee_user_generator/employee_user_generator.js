// Copyright (c) 2026, EBS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee User Generator", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("Get Employees"), () => {
				get_employees(frm);
			}).addClass("btn-primary");

			frm.add_custom_button(__("Create Users"), () => {
				create_users_click(frm);
			}).addClass("btn-primary");
		} else {
			frm.dashboard.set_headline(
				__("Save the document first, then click Get Employees.")
			);
		}
	},

	company(frm) {
		if (frm.doc.employee_list && frm.doc.employee_list.length) {
			frappe.confirm(
				__("Clear current employee list because Company changed?"),
				() => {
					frm.clear_table("employee_list");
					frm.refresh_field("employee_list");
				}
			);
		}
	},
});

frappe.ui.form.on("Employee User Generator Item", {
	employee(frm, cdt, cdn) {
		const row = locals[cdt][cdn];

		if (!row.employee) {
			frappe.model.set_value(cdt, cdn, "employee_name", "");
			frappe.model.set_value(cdt, cdn, "select", 0);
			frappe.model.set_value(cdt, cdn, "status", "Pending");
			frappe.model.set_value(cdt, cdn, "message", "");
			frappe.model.set_value(cdt, cdn, "user", "");
			frappe.model.set_value(cdt, cdn, "password", "");
			return;
		}

		frappe.db.get_value(
			"Employee",
			row.employee,
			["employee_name", "user_id"],
			(r) => {
				if (!r) return;

				frappe.model.set_value(cdt, cdn, "employee_name", r.employee_name || "");

				if (r.user_id) {
					frappe.model.set_value(cdt, cdn, "select", 1);
					frappe.model.set_value(cdt, cdn, "status", "Created");
					frappe.model.set_value(cdt, cdn, "user", r.user_id);
					frappe.model.set_value(
						cdt,
						cdn,
						"message",
						__("User already linked: {0}", [r.user_id])
					);
				} else {
					frappe.model.set_value(cdt, cdn, "select", 0);
					frappe.model.set_value(cdt, cdn, "status", "Pending");
					frappe.model.set_value(cdt, cdn, "user", "");
					frappe.model.set_value(cdt, cdn, "password", "");
					frappe.model.set_value(cdt, cdn, "message", "");
				}
			}
		);
	},

	select(frm, cdt, cdn) {
		const row = locals[cdt][cdn];

		if (row.select && row.status === "Skipped" && row.user) {
			frappe.model.set_value(cdt, cdn, "select", 0);
			frappe.msgprint(
				__("User already exists for this employee. It will be skipped.")
			);
		}
	},
});

function get_employees(frm) {
	frappe.call({
		method:
			"ebs_custom.ebs_custom.doctype.employee_user_generator.employee_user_generator.get_employees",
		args: {
			docname: frm.doc.name,
		},
		freeze: true,
		freeze_message: __("Loading employees..."),
		callback(r) {
			frm.reload_doc();

			if (r.message) {
				frappe.show_alert({
					message: r.message,
					indicator: "green",
				});
			}
		},
	});
}

function create_users_click(frm) {
	const selected = (frm.doc.employee_list || []).filter(
    (r) => Number(r.select) === 1
);

	if (!selected.length) {
		frappe.msgprint(
			__("Please check at least one Pending employee, then click Create Users.")
		);
		return;
	}

	frappe.confirm(
		__("Create users for {0} selected employee(s)?", [selected.length]),
		() => {
			// IMPORTANT: pehle form save (select check DB mein jaye), phir server call
			frm.save()
				.then(() => {
					return frappe.call({
						method:
							"ebs_custom.ebs_custom.doctype.employee_user_generator.employee_user_generator.create_users",
						args: {
							name: frm.doc.name,
						},
						freeze: true,
						freeze_message: __("Creating users..."),
					});
				})
				.then((r) => {
					return frm.reload_doc().then(() => r);
				})
				.then((r) => {
					if (r && r.message) {
						frappe.msgprint(r.message);
					}
				})
				.catch(() => {
					frappe.msgprint(__("Could not create users. Please check Error Log."));
				});
		}
	);
}