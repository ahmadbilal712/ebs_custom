from ebs_custom.patches.v1_0.setup_attendance_approval import execute as setup_custom_fields
from ebs_custom.patches.v1_0.setup_attendance_workflow import execute as setup_attendance_workflow
from ebs_custom.patches.v1_0.setup_hr_request_workflows import execute as setup_hr_workflows
from ebs_custom.patches.v1_0.apply_hrms_pwa_overlay import execute as apply_hrms_pwa_overlay


def after_migrate():
	setup_custom_fields()
	setup_attendance_workflow()
	setup_hr_workflows()
	apply_hrms_pwa_overlay()
