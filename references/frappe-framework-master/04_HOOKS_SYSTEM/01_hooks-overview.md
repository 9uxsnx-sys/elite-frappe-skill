# Hooks Overview

## Quick Reference
Hooks extend framework behavior without modifying core code. Defined in hooks.py. Multiple apps can define same hook.

## AI Prompt
```
When using hooks:
1. Place in hooks.py of your app
2. Use doc_events for document events
3. Use scheduler_events for scheduled tasks
4. Last installed app wins for overrides
5. Multiple apps can extend same hook
```

---

## Hook Types

### Document Events
```python
# hooks.py
doc_events = {
    "Task": {
        "validate": "app.handlers.validate_task",
        "on_submit": "app.handlers.task_submitted",
        "on_cancel": "app.handlers.task_cancelled"
    },
    "*": {
        "on_update": "app.handlers.on_any_update"
    }
}
```

### Override Controllers
```python
override_doctype_class = {
    "Task": "app.overrides.CustomTask"
}
```

### Extend Controllers
```python
extend_doctype_class = {
    "Task": "app.extensions.ExtendedTask"
}
```

### Scheduler Events
```python
scheduler_events = {
    "hourly": ["app.tasks.hourly_cleanup"],
    "daily": ["app.tasks.daily_report"],
    "weekly": ["app.tasks.weekly_summary"],
    "monthly": ["app.tasks.monthly_billing"],
    "cron": {
        "0 9 * * *": ["app.tasks.morning_reminder"]
    }
}
```

### Include JS/CSS
```python
app_include_js = "/assets/app/js/custom.js"
app_include_css = "/assets/app/css/custom.css"

doctype_js = {
    "Task": "public/js/task.js"
}
```

### Permission Hooks
```python
permission_query_conditions = {
    "Task": "app.permissions.task_query"
}

has_permission = {
    "Task": "app.permissions.has_task_permission"
}
```

### Install Hooks
```python
before_install = "app.install.before_install"
after_install = "app.install.after_install"
after_sync = "app.install.after_sync"
```

### Website Hooks
```python
website_route_rules = [
    {"from_route": "/custom/<name>", "to_route": "custom_page"}
]

website_redirects = [
    {"source": "/old", "target": "/new"}
]
```

---

## Hook Resolution

### Last Writer Wins
```python
# App A hooks.py
override_doctype_class = {"Task": "app_a.CustomTask"}

# App B hooks.py (installed later)
override_doctype_class = {"Task": "app_b.CustomTask"}

# App B's override wins
```

### List Accumulation
```python
# App A hooks.py
doc_events = {"Task": {"validate": "app_a.validate"}}

# App B hooks.py
doc_events = {"Task": {"validate": "app_b.validate"}}

# Both are called in order: app_a, then app_b
```

---

## Getting Hooks in Code

```python
# Get hook value
hooks = frappe.get_hooks("doc_events")
print(hooks["Task"])

# Get all hooks for doctype
task_hooks = frappe.get_hooks("doc_events", {"Task": {}})
```

---

## Related Topics
- [Controller Hooks](./05_controller-hooks-complete.md)
