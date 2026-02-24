# Employee

## Quick Reference
Employee is the master record for all staff. Contains personal info, employment details, salary structure, and attendance tracking.

## AI Prompt
```
When managing employees:
1. Set up employment type and department
2. Configure salary structure
3. Link to user for permissions
4. Set up attendance and leave
5. Track probation and confirmation
```

---

## Employee DocType

### Key Fields
| Field | Type | Description |
|-------|------|-------------|
| employee_name | Data | Full name |
| date_of_joining | Date | Joining date |
| department | Link | Department |
| designation | Link | Job title |
| employment_type | Link | Full-time/Part-time/Contract |
| status | Select | Active/Left |
| user_id | Link | User account |

---

## Creating Employee

```python
emp = frappe.get_doc({
    "doctype": "Employee",
    "first_name": "John",
    "last_name": "Doe",
    "date_of_joining": "2024-01-15",
    "department": "Sales",
    "designation": "Sales Executive",
    "employment_type": "Full-time",
    "company_email": "john.doe@company.com",
    "cell_number": "+1234567890"
})
emp.insert()
```

---

## Employee API

### Get Active Employees
```python
employees = frappe.get_all("Employee",
    filters={"status": "Active"},
    fields=["name", "employee_name", "department", "designation"]
)
```

### Get Employee Salary
```python
salary = frappe.db.get_value("Salary Structure Assignment",
    {"employee": "EMP-001"},
    ["salary_structure", "base"],
    as_dict=True
)
```

---

## Related Topics
- [Attendance](./02_attendance.md)
- [Salary Structure](./04_salary-structure.md)
