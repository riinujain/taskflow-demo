"""Business logic services for TaskFlow."""

# Shared constants that create circular dependency smell
TASK_STATUS_TODO = "todo"
TASK_STATUS_IN_PROGRESS = "in_progress"
TASK_STATUS_DONE = "done"
TASK_STATUS_BLOCKED = "blocked"

TASK_PRIORITY_LOW = "low"
TASK_PRIORITY_MEDIUM = "medium"
TASK_PRIORITY_HIGH = "high"
TASK_PRIORITY_CRITICAL = "critical"

# These constants are imported by both task_service and report_service
# creating a circular dependency smell
