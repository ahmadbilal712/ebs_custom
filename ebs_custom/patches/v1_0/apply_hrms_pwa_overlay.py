import os
import re
import shutil
import subprocess

import frappe


def execute():
	apply_hrms_pwa_overlay()


def apply_hrms_pwa_overlay():
	"""Copy HRMS PWA customizations from ebs_custom into the hrms app."""
	if "hrms" not in frappe.get_installed_apps():
		frappe.logger().info("ebs_custom: hrms not installed, skipping PWA overlay")
		return False

	overlay_root = os.path.join(frappe.get_app_path("ebs_custom"), "hrms_overlay")
	if not os.path.isdir(overlay_root):
		frappe.logger().warning("ebs_custom: hrms_overlay folder missing")
		return False

	hrms_root = frappe.get_app_path("hrms", "..")

	_copy_overlay_files(overlay_root, hrms_root)
	_patch_router_index(hrms_root)
	_patch_home_vue(hrms_root)
	_patch_hooks(hrms_root)

	frappe.logger().info("ebs_custom: HRMS PWA overlay applied from ebs_custom/hrms_overlay")
	return True


def build_hrms_pwa():
	"""Try to build HRMS frontend after overlay. Returns True on success."""
	hrms_root = frappe.get_app_path("hrms", "..")
	frontend_dir = os.path.join(hrms_root, "frontend")
	bench_path = frappe.utils.get_bench_path()

	if not os.path.isdir(frontend_dir):
		return False

	yarn = shutil.which("yarn")
	if not yarn:
		frappe.logger().warning("ebs_custom: yarn not found — skip auto PWA build")
		return False

	try:
		if os.path.isfile(os.path.join(frontend_dir, "package.json")):
			subprocess.run(
				[yarn, "install", "--frozen-lockfile"],
				cwd=frontend_dir,
				check=True,
				capture_output=True,
				text=True,
				timeout=600,
			)
			subprocess.run(
				[yarn, "build"],
				cwd=frontend_dir,
				check=True,
				capture_output=True,
				text=True,
				timeout=900,
			)

		bench_cmd = os.path.join(bench_path, "env", "bin", "bench")
		if not os.path.isfile(bench_cmd):
			bench_cmd = shutil.which("bench") or "bench"

		subprocess.run(
			[bench_cmd, "build", "--app", "hrms"],
			cwd=bench_path,
			check=True,
			capture_output=True,
			text=True,
			timeout=600,
		)
		return True
	except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as exc:
		frappe.logger().warning(f"ebs_custom: auto PWA build failed: {exc}")
		return False


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
