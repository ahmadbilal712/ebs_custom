from ebs_custom.patches.v1_0.setup_attendance_approval import execute as setup_custom_fields
from ebs_custom.patches.v1_0.setup_attendance_workflow import execute as setup_attendance_workflow
from ebs_custom.patches.v1_0.setup_hr_request_workflows import execute as setup_hr_workflows


def after_migrate():
	setup_custom_fields()
	setup_attendance_workflow()
	setup_hr_workflows()
