# Frappe Framework Quick Reference

## Core Concepts

| Concept | Description |
|---------|-------------|
| DocType | Model + View + Controller definition |
| Document | Instance of a DocType (row in database) |
| Controller | Python class with document logic |
| Hooks | Extend framework behavior |
| ORM | Object-Relational Mapping for database |

---

## Document Operations

### Create
```python
doc = frappe.get_doc({
    "doctype": "Task",
    "subject": "New Task"
})
doc.insert()
```

### Read
```python
doc = frappe.get_doc("Task", "TASK-001")
print(doc.subject, doc.status)
```

### Update
```python
doc = frappe.get_doc("Task", "TASK-001")
doc.status = "Completed"
doc.save()
```

### Delete
```python
frappe.delete_doc("Task", "TASK-001")
```

---

## Query Operations

### Get All
```python
tasks = frappe.get_all("Task",
    filters={"status": "Open"},
    fields=["name", "subject", "priority"]
)
```

### Get Value
```python
subject = frappe.db.get_value("Task", "TASK-001", "subject")
```

### SQL Query
```python
results = frappe.db.sql("""
    SELECT name, subject FROM tabTask 
    WHERE status = %s
""", ("Open",), as_dict=True)
```

---

## Controller Hooks

```python
class Task(Document):
    def validate(self):
        # Called before save
        if self.due_date < self.creation:
            frappe.throw("Due date cannot be in past")
    
    def on_submit(self):
        # Called on submit (if submittable)
        pass
    
    def on_cancel(self):
        # Called on cancel
        pass
```

---

## API Creation

### Whitelisted Method
```python
@frappe.whitelist()
def get_task_details(task_id):
    task = frappe.get_doc("Task", task_id)
    return task.as_dict()
```

### REST API
```bash
GET /api/resource/Task/TASK-001
POST /api/resource/Task
PUT /api/resource/Task/TASK-001
DELETE /api/resource/Task/TASK-001
```

---

## Form Script (Client)

```javascript
frappe.ui.form.on('Task', {
    refresh: function(frm) {
        // Add custom button
        frm.add_custom_button('Complete', function() {
            frm.set_value('status', 'Completed');
            frm.save();
        });
    },
    status: function(frm) {
        // On status change
        console.log('Status changed to:', frm.doc.status);
    }
});
```

---

## Hooks (hooks.py)

```python
# Document events
doc_events = {
    "Task": {
        "validate": "app.handlers.validate_task",
        "on_submit": "app.handlers.task_submitted"
    }
}

# Scheduled tasks
scheduler_events = {
    "daily": ["app.tasks.daily_cleanup"],
    "hourly": ["app.tasks.hourly_check"]
}

# Include JS/CSS
app_include_js = "/assets/app/js/custom.js"
app_include_css = "/assets/app/css/custom.css"
```

---

## Permissions

```python
# Check permission
if frappe.has_permission("Task", "write"):
    doc.save()

# Get permitted documents
tasks = frappe.get_list("Task")  # Respects permissions
```

---

## Caching

```python
# Set cache
frappe.cache.set_value("key", "value")

# Get cache
value = frappe.cache.get_value("key")

# Clear cache
frappe.clear_cache()
```

---

## Background Jobs

```python
# Enqueue job
frappe.enqueue("app.tasks.process_task", task_id="TASK-001")

# With queue
frappe.enqueue("app.tasks.long_task", queue="long", timeout=3600)
```

---

## Common DocTypes

| DocType | Purpose |
|---------|---------|
| User | User accounts |
| Role | User roles |
| DocType | DocType definitions |
| Custom Field | Added fields |
| Property Setter | Modified properties |
| Workflow | Approval workflows |
| Error Log | System errors |

---

## Bench Commands

```bash
# Site management
bench new-site [site]
bench --site [site] console
bench --site [site] backup
bench --site [site] migrate

# App management
bench new-app [app_name]
bench get-app [app_url]
bench install-app [app]

# Development
bench start
bench watch

# Production
bench setup production
bench setup nginx
```
