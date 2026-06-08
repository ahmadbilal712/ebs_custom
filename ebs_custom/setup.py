from ebs_custom.patches.v1_0.setup_attendance_approval import execute as setup_custom_fields
from ebs_custom.patches.v1_0.setup_attendance_workflow import execute as setup_workflow


def after_migrate():
	setup_custom_fields()
	setup_workflow()
