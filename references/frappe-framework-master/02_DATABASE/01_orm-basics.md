# ORM Basics

## Quick Reference
Frappe ORM (Object-Relational Mapping) handles all database operations. Use frappe.get_doc(), frappe.get_all(), frappe.db methods. Never write raw SQL unless necessary.

## AI Prompt
```
When using Frappe ORM:
1. Use get_doc for single document
2. Use get_all/get_list for queries
3. Use db methods for specific operations
4. Always handle exceptions
5. Use transactions for related operations
```

---

## Document Operations

### Create
```python
# Method 1: Using get_doc with dict
doc = frappe.get_doc({
    "doctype": "Task",
    "subject": "New Task",
    "description": "Task description"
})
doc.insert()

# Method 2: Using new_doc
doc = frappe.new_doc("Task")
doc.subject = "New Task"
doc.insert()

# Insert with ignore
doc.insert(ignore_permissions=True)
doc.insert(ignore_if_duplicate=True)
```

### Read
```python
# Get single document
doc = frappe.get_doc("Task", "TASK-001")

# Get with filters
doc = frappe.get_doc("Task", {"subject": "My Task"})

# Get cached (faster for repeated access)
doc = frappe.get_cached_doc("Task", "TASK-001")

# Get field value
subject = frappe.db.get_value("Task", "TASK-001", "subject")

# Get multiple fields
data = frappe.db.get_value("Task", "TASK-001", 
    ["subject", "status", "due_date"], as_dict=True)
```

### Update
```python
# Full update (triggers hooks)
doc = frappe.get_doc("Task", "TASK-001")
doc.status = "Completed"
doc.save()

# Direct update (no hooks)
frappe.db.set_value("Task", "TASK-001", "status", "Completed")

# Update multiple fields
frappe.db.set_value("Task", "TASK-001", {
    "status": "Completed",
    "completed_date": frappe.utils.today()
})
```

### Delete
```python
# Delete with hooks
doc = frappe.get_doc("Task", "TASK-001")
doc.delete()

# Delete without hooks
frappe.delete_doc("Task", "TASK-001")

# Delete with filters
frappe.db.delete("Task", {"status": "Cancelled"})
```

---

## Query Operations

### get_all
```python
# Get all documents
tasks = frappe.get_all("Task",
    fields=["name", "subject", "status"],
    filters={"status": "Open"},
    order_by="creation desc",
    limit=10
)

# With complex filters
tasks = frappe.get_all("Task",
    filters={
        "status": "Open",
        "due_date": [">", "2024-01-01"],
        "priority": ["in", ["High", "Urgent"]]
    }
)
```

### get_list (with permissions)
```python
# Respects user permissions
tasks = frappe.get_list("Task",
    fields=["name", "subject"],
    filters={"status": "Open"}
)
```

### get_value
```python
# Single value
subject = frappe.db.get_value("Task", "TASK-001", "subject")

# Multiple fields as dict
data = frappe.db.get_value("Task", "TASK-001", 
    ["subject", "status"], as_dict=True)

# Multiple fields as tuple
subject, status = frappe.db.get_value("Task", "TASK-001", 
    ["subject", "status"])
```

---

## SQL Queries

### Raw SQL
```python
# Select
results = frappe.db.sql("""
    SELECT name, subject, status 
    FROM tabTask 
    WHERE status = %s
    ORDER BY creation DESC
""", ("Open",), as_dict=True)

# With multiple parameters
results = frappe.db.sql("""
    SELECT * FROM tabTask 
    WHERE status = %s AND priority = %s
""", ("Open", "High"), as_dict=True)

# Count
count = frappe.db.sql("""
    SELECT COUNT(*) FROM tabTask WHERE status = %s
""", ("Open",))[0][0]
```

### Query Builder
```python
from frappe.query_builder import DocType

Task = DocType("Task")

query = (
    frappe.qb.from_(Task)
    .select(Task.name, Task.subject, Task.status)
    .where(Task.status == "Open")
    .orderby(Task.creation, order=frappe.qb.desc)
    .limit(10)
)

results = query.run(as_dict=True)
```

---

## Transactions

### Commit
```python
# Explicit commit (normally auto)
frappe.db.commit()

# Transaction block
try:
    doc1.insert()
    doc2.insert()
    frappe.db.commit()
except:
    frappe.db.rollback()
```

### Rollback
```python
try:
    # Operations
    doc.insert()
    raise Exception("Something went wrong")
except:
    frappe.db.rollback()
```

---

## Bulk Operations

### Bulk Insert
```python
for i in range(100):
    doc = frappe.get_doc({
        "doctype": "Task",
        "subject": f"Task {i}"
    })
    doc.insert()

frappe.db.commit()  # Commit once at end
```

### Bulk Update
```python
# Update all matching records
frappe.db.sql("""
    UPDATE tabTask SET status = 'Archived'
    WHERE creation < %s
""", ("2023-01-01",))

frappe.db.commit()
```

---

## Related Topics
- [Query Builder](./03_query-builder.md)
- [Migrations](./07_migrations.md)
