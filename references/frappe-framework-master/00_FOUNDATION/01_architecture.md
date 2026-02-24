# Frappe Framework Architecture

## Quick Reference
Frappe is a full-stack framework: Python (backend) + MariaDB (database) + Redis (cache/queue) + Vue.js (frontend). Uses meta-programming for DocTypes.

## AI Prompt
```
When understanding Frappe architecture:
1. DocType = Model + View + Controller
2. Hooks extend behavior without modification
3. ORM handles all database operations
4. Desk is the admin interface (Vue.js)
5. Background jobs use Redis + RQ
```

---

## Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│                    Client Layer                          │
├─────────────────────────────────────────────────────────┤
│  Browser (Desk UI - Vue.js)    │    Portal/Website      │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                    Web Layer                             │
├─────────────────────────────────────────────────────────┤
│  Nginx (reverse proxy) → Gunicorn (WSGI) → WSGI Handler │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                    Application Layer                     │
├─────────────────────────────────────────────────────────┤
│  Frappe Framework                                        │
│  ├── ORM (Document, DB)                                  │
│  ├── Auth & Permissions                                  │
│  ├── Hooks System                                        │
│  ├── REST API                                            │
│  └── Web Framework                                       │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                    Data Layer                            │
├─────────────────────────────────────────────────────────┤
│  MariaDB (primary)    │    Redis (cache, queue, socket) │
└─────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
frappe-bench/
├── apps/                      # Installed apps
│   ├── frappe/               # Framework core
│   │   ├── frappe/
│   │   │   ├── model/        # ORM, Document class
│   │   │   ├── desk/         # Desk UI
│   │   │   ├── www/          # Website pages
│   │   │   ├── api/          # REST API handlers
│   │   │   ├── core/         # Core DocTypes
│   │   │   └── hooks.py      # Framework hooks
│   │   └── setup.py
│   └── custom_app/           # Your custom app
│       ├── custom_app/
│       │   ├── doctype/      # Custom DocTypes
│       │   ├── api/          # API endpoints
│       │   └── hooks.py
│       └── setup.py
├── sites/                    # Site instances
│   ├── site1.localhost/
│   │   ├── site_config.json  # Site configuration
│   │   ├── logs/             # Site logs
│   │   └── private/          # Private files
│   └── common_site_config.json
├── env/                      # Python virtual environment
├── config/                   # Redis, supervisor configs
└── logs/                     # Bench logs
```

---

## Core Components

### 1. DocType System
```python
# DocType = JSON definition + Python controller + JS client

# JSON: Defines schema and UI
{
    "name": "Task",
    "fields": [
        {"fieldname": "subject", "fieldtype": "Data"},
        {"fieldname": "status", "fieldtype": "Select", 
         "options": "Open\nIn Progress\nCompleted"}
    ]
}

# Python: Controller class
class Task(Document):
    def validate(self):
        if self.due_date < self.creation:
            frappe.throw("Invalid due date")

# JS: Client script
frappe.ui.form.on('Task', {
    refresh: function(frm) { }
});
```

### 2. ORM (Object-Relational Mapping)
```python
# All database operations through ORM
doc = frappe.get_doc("Task", "TASK-001")  # Read
doc.subject = "Updated"                    # Modify
doc.save()                                 # Write
doc.delete()                               # Delete

# Queries
tasks = frappe.get_all("Task", fields=["name", "subject"])
```

### 3. Hooks System
```python
# Extend framework without modifying core
# hooks.py

doc_events = {
    "Task": {
        "validate": "app.handlers.validate_task",
        "on_submit": "app.handlers.task_submitted"
    }
}

scheduler_events = {
    "daily": ["app.tasks.daily_cleanup"]
}
```

### 4. Permissions
```python
# Role-based permission system
# Defined in DocType, stored in tabDocPerm

# Check permission
frappe.has_permission("Task", "write")

# Query respects permissions
frappe.get_list("Task")  # Only permitted docs
```

---

## Request Lifecycle

```
1. Browser → Nginx → Gunicorn
2. WSGI Handler → frappe.handler
3. Auth check → Session validation
4. Route resolution → Controller method
5. Permission check
6. Business logic execution
7. Response → JSON/HTML
8. Browser rendering
```

---

## Background Services

### Redis Servers
```
Port 13000 - Cache
Port 11000 - Queue
Port 12000 - Socket.io
```

### Worker Processes
```
bench worker               # Default queue
bench worker --queue long  # Long-running jobs
bench schedule             # Scheduled tasks
```

---

## Key Tables

| Table | Purpose |
|-------|---------|
| tabDocType | DocType definitions |
| tabDocField | Field definitions |
| tabDocPerm | Permission rules |
| tabUser | User accounts |
| tabRole | Roles |
| tabCustom Field | Custom fields |
| tabProperty Setter | Property overrides |
| tabError Log | Error logs |
| tab[DocType] | Each DocType's data |

---

## Related Topics
- [Directory Structure](./02_directory-structure.md)
- [DocType System](../01_CORE_SYSTEM/01_doctype-fundamentals.md)
