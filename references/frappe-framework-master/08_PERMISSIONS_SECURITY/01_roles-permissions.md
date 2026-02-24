# Roles and Permissions

## Quick Reference
Frappe uses role-based access control. Permissions defined per DocType per role. Users assigned roles. Permission levels control field access.

## AI Prompt
```
When configuring permissions:
1. Define roles first
2. Set DocType permissions per role
3. Use permission levels for field security
4. Check permissions in code with has_permission
5. Use permission_query for row-level security
```

---

## Role Management

### Create Role
```python
role = frappe.get_doc({
    "doctype": "Role",
    "role_name": "Task Manager",
    "desk_access": 1
})
role.insert()
```

### Assign Role to User
```python
user = frappe.get_doc("User", "user@example.com")
user.append("roles", {"role": "Task Manager"})
user.save()
```

### Get User Roles
```python
roles = frappe.get_roles("user@example.com")
# Returns: ["System User", "Task Manager", ...]
```

---

## DocType Permissions

### Permission Types
| Permission | Description |
|------------|-------------|
| read | Can read documents |
| write | Can edit documents |
| create | Can create new documents |
| delete | Can delete documents |
| submit | Can submit documents |
| cancel | Can cancel documents |
| amend | Can amend submitted documents |
| print | Can print documents |
| email | Can email documents |
| import | Can import data |
| export | Can export data |

### Set Permissions
```python
# In DocType definition
"permissions": [
    {
        "role": "Task Manager",
        "read": 1,
        "write": 1,
        "create": 1,
        "delete": 1,
        "submit": 1
    },
    {
        "role": "Task User",
        "read": 1,
        "write": 1,
        "create": 1
    }
]
```

---

## Permission Levels

### Field Permission Level
```python
# In DocType field definition
{
    "fieldname": "approved_by",
    "fieldtype": "Link",
    "label": "Approved By",
    "permlevel": 1  # Only accessible at level 1
}
```

### Permission Level Assignment
```python
# In DocType permission
{
    "role": "Task Manager",
    "permlevel": 1,  # Has access to level 1 fields
    "read": 1,
    "write": 1
}
```

---

## Permission Checks

### has_permission
```python
# Check if user has permission
if frappe.has_permission("Task", "write"):
    doc.save()

# Check for specific document
if frappe.has_permission("Task", "read", "TASK-001"):
    doc = frappe.get_doc("Task", "TASK-001")
```

### Permission Error
```python
# Raise permission error
frappe.throw("No permission", frappe.PermissionError)
```

---

## Row-Level Security

### Permission Query Hook
```python
# hooks.py
permission_query_conditions = {
    "Task": "app.permissions.task_permission_query"
}

# app/permissions.py
def task_permission_query(user):
    return f"owner = '{user}'"
```

### Custom Permission Hook
```python
# hooks.py
has_permission = {
    "Task": "app.permissions.has_task_permission"
}

# app/permissions.py
def has_task_permission(doc, user, permission_type):
    if permission_type == "read":
        return True
    if permission_type == "write":
        return doc.owner == user or "Task Manager" in frappe.get_roles(user)
    return False
```

---

## Related Topics
- [User Management](./03_user-management.md)
