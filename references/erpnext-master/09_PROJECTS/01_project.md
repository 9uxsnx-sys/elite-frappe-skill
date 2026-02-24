# Project

## Quick Reference
Project manages project timeline, tasks, and billing. Tracks progress, milestones, and costs. Links to timesheets for time tracking.

## AI Prompt
```
When managing projects:
1. Define clear milestones
2. Link tasks to project
3. Track time via timesheets
4. Monitor budget vs actual
5. Bill based on progress
```

---

## Project DocType

### Key Fields
| Field | Type | Description |
|-------|------|-------------|
| project_name | Data | Project name |
| customer | Link | Customer reference |
| status | Select | Open/Completed/Cancelled |
| expected_start_date | Date | Start date |
| expected_end_date | Date | End date |
| tasks | Table | Project tasks |

---

## Creating Project

```python
project = frappe.get_doc({
    "doctype": "Project",
    "project_name": "Website Development",
    "customer": "ABC Corp",
    "expected_start_date": "2024-01-15",
    "expected_end_date": "2024-03-15",
    "tasks": [
        {"subject": "Design", "description": "UI/UX Design"},
        {"subject": "Development", "description": "Backend & Frontend"},
        {"subject": "Testing", "description": "QA Testing"}
    ]
})
project.insert()
```

---

## Project Billing

### Create Sales Invoice
```python
from erpnext.projects.doctype.project.project import make_sales_invoice

si = make_sales_invoice("PRJ-001")
si.insert()
si.submit()
```

---

## Related Topics
- [Task](./02_task.md)
- [Timesheet](./03_timesheet.md)
