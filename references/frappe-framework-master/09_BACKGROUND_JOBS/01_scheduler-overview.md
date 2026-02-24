# Scheduler Overview

## Quick Reference
Frappe scheduler runs periodic tasks. Define in hooks.py under scheduler_events. Uses Redis queues. Monitor via bench schedule.

## AI Prompt
```
When using scheduler:
1. Define tasks in hooks.py
2. Use correct frequency (hourly, daily, etc.)
3. Handle exceptions in task code
4. Use frappe.enqueue for async tasks
5. Monitor via bench schedule command
```

---

## Scheduler Events

### Define in hooks.py
```python
scheduler_events = {
    "hourly": [
        "app.tasks.hourly_cleanup",
        "app.tasks.send_reminders"
    ],
    "daily": [
        "app.tasks.daily_report",
        "app.tasks.cleanup_logs"
    ],
    "weekly": [
        "app.tasks.weekly_summary"
    ],
    "monthly": [
        "app.tasks.monthly_billing"
    ],
    "cron": {
        "0 9 * * *": ["app.tasks.morning_greeting"],
        "0 17 * * 1-5": ["app.tasks.eod_report"]
    }
}
```

---

## Creating Scheduled Tasks

### Task Function
```python
# app/tasks.py
import frappe

def daily_report():
    """Generate daily report"""
    tasks = frappe.get_all("Task",
        filters={"status": "Open"},
        fields=["name", "subject"]
    )
    
    # Send email
    frappe.sendmail(
        recipients="admin@example.com",
        subject="Daily Task Report",
        message=f"Open tasks: {len(tasks)}"
    )
```

### Task with Exception Handling
```python
def safe_task():
    try:
        # Task logic
        process_data()
    except Exception as e:
        frappe.log_error(e, "Task Error")
        # Don't re-raise - scheduler will continue
```

---

## Background Jobs

### Enqueue Job
```python
# Simple enqueue
frappe.enqueue("app.tasks.process_task", task_id="TASK-001")

# With parameters
frappe.enqueue("app.tasks.process_task",
    task_id="TASK-001",
    priority="high"
)

# With queue
frappe.enqueue("app.tasks.long_task",
    queue="long",
    ti
