import os
import re
import shutil

import frappe


OVERLAY_MARKER = "ebs_custom PWA overlay"


def execute():
	apply_hrms_pwa_overlay()


def apply_hrms_pwa_overlay():
	"""Copy HRMS PWA customizations from ebs_custom into the hrms app."""
	if "hrms" not in frappe.get_installed_apps():
		frappe.logger().info("ebs_custom: hrms not installed, skipping PWA overlay")
		return

	overlay_root = os.path.join(frappe.get_app_path("ebs_custom"), "hrms_overlay")
	if not os.path.isdir(overlay_root):
		return

	hrms_root = frappe.get_app_path("hrms", "..")

	_copy_overlay_files(overlay_root, hrms_root)
	_patch_router_index(hrms_root)
	_patch_home_vue(hrms_root)
	_patch_hooks(hrms_root)

	frappe.logger().info(
		"ebs_custom: HRMS PWA overlay applied. Run: cd apps/hrms/frontend && yarn build && bench build --app hrms"
	)


def _copy_overlay_files(overlay_root, hrms_root):
	skip_names = {"apply_hrms_pwa_overlay.py", "README.md"}

	for root, _dirs, files in os.walk(overlay_root):
		for filename in files:
			if filename in skip_names:
				continue

			src = os.path.join(root, filename)
			rel = os.path.relpath(src, overlay_root)
			if rel.startswith("merge_patches" + os.sep):
				continue

			dst = os.path.join(hrms_root, rel.replace("/", os.sep))
			os.makedirs(os.path.dirname(dst), exist_ok=True)
			shutil.copy2(src, dst)


def _patch_router_index(hrms_root):
	path = os.path.join(hrms_root, "frontend", "src", "router", "index.js")
	if not os.path.isfile(path):
		return

	with open(path, encoding="utf-8") as handle:
		content = handle.read()

	if "ebs_custom.js" in content:
		return

	content = content.replace(
		'import salarySlipRoutes from "./salary_slips"\n',
		'import salarySlipRoutes from "./salary_slips"\nimport ebsCustomRoutes from "./ebs_custom"\n',
	)
	content = content.replace(
		"\t...salarySlipRoutes,\n]",
		"\t...salarySlipRoutes,\n\t...ebsCustomRoutes,\n]",
	)

	with open(path, "w", encoding="utf-8") as handle:
		handle.write(content)


def _patch_home_vue(hrms_root):
	path = os.path.join(hrms_root, "frontend", "src", "views", "Home.vue")
	if not os.path.isfile(path):
		return

	with open(path, encoding="utf-8") as handle:
		content = handle.read()

	if "SalaryAdjustmentFormView" in content:
		return

	quick_links = """
	{
		icon: markRaw(SalaryIcon),
		title: __("Salary Adjustment"),
		route: "SalaryAdjustmentFormView",
	},
	{
		icon: markRaw(LeaveIcon),
		title: __("Promotion Request"),
		route: "PromotionRequestFormView",
	},
	{
		icon: markRaw(AttendanceIcon),
		title: __("Branch Attendance Approval"),
		route: "BranchAttendanceApprovalFormView",
	},
]"""

	content = content.replace(
		'\t\troute: "SalarySlipsDashboard",\n\t},\n]',
		'\t\troute: "SalarySlipsDashboard",\n\t},' + quick_links,
	)

	with open(path, "w", encoding="utf-8") as handle:
		handle.write(content)


def _patch_hooks(hrms_root):
	path = os.path.join(hrms_root, "hooks.py")
	if not os.path.isfile(path):
		return

	with open(path, encoding="utf-8") as handle:
		content = handle.read()

	content = re.sub(r'app_title\s*=\s*"[^"]*"', 'app_title = "BOT HR"', content)
	content = re.sub(
		r'("title":\s*)"Frappe HR"',
		r'\1"BOT HR"',
		content,
	)

	with open(path, "w", encoding="utf-8") as handle:
		handle.write(content)
