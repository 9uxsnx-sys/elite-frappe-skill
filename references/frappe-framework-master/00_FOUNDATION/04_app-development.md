# Frappe App Development Guide

## Quick Reference
Complete guide to building production-ready Frappe applications from scratch.

## AI Prompt
```
When developing Frappe applications:
1. Follow app structure conventions
2. Use hooks for customization
3. Implement proper DocTypes
4. Write tests alongside code
5. Follow security best practices
```

---

## Creating a New App

### Step 1: Generate the App
```bash
cd ~/frappe-bench
bench new-app my_app
```

Follow the prompts:
- App Name: My App
- App Title: My Application
- App Description: A custom Frappe application
- App Publisher: Your Company
- App Email: dev@company.com
- App Icon: (optional)
- App Color: (optional)
- App License: MIT

### Step 2: App Structure
```
my_app/
├── __init__.py              # App package
├── app.py                  # App entry point
├── hooks.py                # App hooks (REQUIRED)
├── my_app/
│   ├── __init__.py
│   ├── __init__.py         # Module package
│   ├── controllers/
│   │   └── __init__.py
│   ├── doctypes/
│   │   └── __init__.py
│   ├── patches.txt         # Database migrations
│   ├── templates/
│   │   ├── pages/
│   │   ├── web forms/
│   │   └── www/
│   ├── www/
│   │   └── index.html
│   ├── api/
│   │   └── __init__.py
│   ├── fixtures/
│   │   └── property_setter.json
│   ├── hooks.py            # Module hooks
│   ├──overrides/
│   │   └── __init__.py
│   ├── test/
│   │   ├── __init__.py
│   │   └── test_my_app.py
│   ├── utils.py
│   └── version.py
├── MANIFEST.in
├── README.md
├── requirements.txt
├── setup.py
└── yarn.lock
```

---

## hooks.py - The Heart of Your App

### Essential Hooks
```python
# my_app/hooks.py
app_name = "my_app"
app_title = "My Application"
app_publisher = "Your Company"
app_description = "A custom Frappe application"
app_icon = "octicon octicon-file-directory"
app_color = "blue"
app_email = "dev@company.com"
app_license = "MIT"

# DocTypes to install (optional - will create after app install)
# doc_types = []

# Boot Session - Add data to boot
# boot_session = "my_app.boot.boot_session"

# Application Hooks
fixtures = []

# Website Routes
website_route_rules = [
    {"from_route": "/blog/<path:app_path>", "to_route": "blog"},
]

# Web Templates
web_template_mappings = {}

# Permissions
permission_query_conditions = {}
has_permission = {}

# Scheduler Events
scheduler_events = {
    "all": [
        "my_app.utils.daily_tasks"
    ],
    "daily": [
        "my_app.utils.daily_cleanup"
    ],
    "hourly": [
        "my_app.utils.hourly_sync"
    ],
    "weekly": [
        "my_app.utils.weekly_report"
    ],
    "monthly": [
        "my_app.utils.monthly_summary"
    ]
}

# Global Filters
# global_search_doctypes = {}

# App Source App Include (for adding JS/CSS)
# app_include_css = "/assets/my_app/css/my_app.css"
# app_include_js = "/assets/my_app/js/my_app.js"

# Website Include
# website_include_css = "/assets/my_app/css/web.css"
# website_include_js = "/assets/my_app/js/web.js"

# Portal Menu Items
# portal_menu_items = {}

# Notification Channels
# notification_channels = ["Email"]

# Before Install Hooks
# before_install = "my_app.install.before_install"
# after_install = "my_app.install.after_install"

# Before Migration Hooks
# before_migrate = "my_app.migrations.before_migrate"
# after_migrate = "my_app.migrations.after_migrate"

# DocType Hooks - Extend existing DocTypes
# doc_events = {
#     "*": {
#         "on_update": "my_app.utils.on_doc_update",
#         "on_trash": "my_app.utils.on_doc_trash",
#         "validate": "my_app.utils.validate_doc"
#     },
#     "Sales Invoice": {
#         "on_submit": "my_app.utils.on_invoice_submit"
#     }
# }

# Override Whitelisted Functions
# override_whitelisted_methods = {
#     "frappe.auth.login": "my_app.auth.login"
# }

# Override Controllers
# override_doctype_class = {
#     "Sales Invoice": "my_app.overrides.SalesInvoice"
# }

# Form Scripts
# form_scripts = {
#     "Sales Invoice": "my_app/form_scripts/sales_invoice.js"
# }

# Form Grid Field Types
# form_grid_fields = {
#     "docfield": {
#         "currency": {
#             "options": "Exchange Rate"
#         }
#     }
# }

```

---

## Creating DocTypes in Your App

### Automatic Generation
```bash
bench new-doctype Project Task --app my_app --module "My App"
```

### Manual DocType Structure
```python
# my_app/my_app/doctype/project_task/project_task.py
import frappe
from frappe.model.document import Document

class ProjectTask(Document):
    def validate(self):
        self.set_status()
        self.validate_dates()
    
    def set_status(self):
        if not self.status:
            self.status = "Open"
    
    def validate_dates(self):
        if self.end_date and self.start_date:
            if self.end_date < self.start_date:
                frappe.throw("End date cannot be before start date")
    
    def on_update(self):
        self.update_project_progress()
    
    def on_trash(self):
        self.cleanup_related()
    
    # Custom Method
    def mark_complete(self):
        self.status = "Completed"
        self.completed_on = frappe.utils.now()
        self.save(ignore_permissions=True)

# my_app/my_app/doctype/project_task/project_task.json
{
    "name": "Project Task",
    "doctype": "DocType",
    "module": "My App",
    "autoname": "field:title",
    "is_submittable": 1,
    "fields": [
        {
            "fieldname": "title",
            "fieldtype": "Data",
            "label": "Title",
            "reqd": 1
        },
        {
            "fieldname": "status",
            "fieldtype": "Select",
            "label": "Status",
            "options": "Open\nIn Progress\nCompleted\nCancelled",
            "default": "Open"
        },
        {
            "fieldname": "start_date",
            "fieldtype": "Date",
            "label": "Start Date"
        },
        {
            "fieldname": "end_date",
            "fieldtype": "Date",
            "label": "End Date"
        },
        {
            "fieldname": "description",
            "fieldtype": "Text Editor",
            "label": "Description"
        }
    ],
    "permissions": [
        {
            "role": "System Manager",
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1
        },
        {
            "role": "Projects User",
            "read": 1,
            "write": 1,
            "create": 1
        }
    ]
}
```

---

## Custom Fixtures

### What Are Fixtures?
Fixtures are initial data that gets installed with your app (custom fields, property setters, roles, etc.)

### Creating Fixtures
```python
# my_app/fixtures/custom_field.json
[
    {
        "dt": "Task",
        "fieldname": "my_custom_field",
        "fieldtype": "Data",
        "label": "My Custom Field",
        "insert_after": "subject",
        "description": "Custom field added by my_app"
    }
]

# my_app/fixtures/property_setter.json
[
    {
        "doc_type": "Task",
        "doctype": "Property Setter",
        "field_name": "status",
        "property": "options",
        "value": "Open\nIn Progress\nCompleted\nCancelled\nOn Hold"
    }
]
```

### In hooks.py
```python
fixtures = [
    {"dt": "Custom Field", "filters": [["module", "=", "My App"]]},
    {"dt": "Property Setter", "filters": [["module", "=", "My App"]]},
    {"dt": "Role", "filters": [["module", "=", "My App"]]},
    "Workflow",
    "Print Format",
    "Web Template"
]
```

---

## API Development

### Creating REST API Endpoints
```python
# my_app/api.py
import frappe
import json

@frappe.whitelist()
def get_tasks(project=None):
    """Get all tasks, optionally filtered by project"""
    filters = {}
    if project:
        filters["project"] = project
    
    tasks = frappe.get_all(
        "Project Task",
        filters=filters,
        fields=["name", "title", "status", "start_date", "end_date"],
        order_by="start_date asc"
    )
    return tasks

@frappe.whitelist()
def create_task(data):
    """Create a new task"""
    if isinstance(data, str):
        data = json.loads(data)
    
    doc = frappe.get_doc({
        "doctype": "Project Task",
        "title": data.get("title"),
        "start_date": data.get("start_date"),
        "end_date": data.get("end_date"),
        "description": data.get("description"),
        "status": "Open"
    })
    doc.insert(ignore_permissions=True)
    return doc.name

@frappe.whitelist()
def update_task_status(task_name, status):
    """Update task status"""
    doc = frappe.get_doc("Project Task", task_name)
    doc.status = status
    doc.save(ignore_permissions=True)
    return {"success": True, "message": f"Task {task_name} updated to {status}"}
```

### Using REST API from External Systems
```python
import requests

# Login
session = requests.Session()
login = session.post(
    "http://site.local/api/method/login",
    data={"usr": "Administrator", "pwd": "password"}
)

# Call API
response = session.get(
    "http://site.local/api/method/my_app.api.get_tasks"
)
data = response.json()
```

---

## Testing Your App

### Writing Tests
```python
# my_app/my_app/test/test_my_app.py
import frappe
import unittest

class TestMyApp(unittest.TestCase):
    def setUp(self):
        frappe.set_user("Administrator")
    
    def test_task_creation(self):
        """Test creating a new task"""
        task = frappe.get_doc({
            "doctype": "Project Task",
            "title": "Test Task",
            "start_date": "2024-01-01",
            "end_date": "2024-01-31"
        })
        task.insert()
        
        self.assertTrue(task.name)
        self.assertEqual(task.status, "Open")
    
    def test_task_dates_validation(self):
        """Test that end date must be after start date"""
        task = frappe.get_doc({
            "doctype": "Project Task",
            "title": "Test Task",
            "start_date": "2024-01-31",
            "end_date": "2024-01-01"
        })
        
        with self.assertRaises(frappe.ValidationError):
            task.insert()
    
    def test_task_status_update(self):
        """Test updating task status"""
        task = frappe.get_doc({
            "doctype": "Project Task",
            "title": "Test Task"
        })
        task.insert()
        
        task.status = "Completed"
        task.save()
        
        self.assertEqual(task.status, "Completed")
        self.assertIsNotNone(task.completed_on)

# Run tests
# bench --app my_app run-tests
```

---

## Installing & Updating Your App

### Install on Site
```bash
# Get the app (if from GitHub)
bench get-app https://github.com/yourcompany/my_app

# Install on site
bench --site site1.local install-app my_app

# Update app
bench update --pull

# Rebuild
bench build --app my_app

# Clear cache
bench --site site1.local clear-cache
```

### Version Management
```python
# my_app/__init__.py
__version__ = "1.0.0"

# In setup.py
setup(
    version="1.0.0",
    # ...
)
```

### Creating Patches
```python
# my_app/patches.txt
my_app.patches.update_status_field
my_app.patches.migrate_custom_fields

# my_app/patches/update_status_field.py
import frappe

def execute():
    # Add new status options
    frappe.reload_doctype("Project Task")
    
    # Migrate existing data
    frappe.db.sql("""
        UPDATE `tabProject Task`
        SET status = 'On Hold'
        WHERE status = 'Pending'
    """)
```

---

## Best Practices

### Code Structure
1. **Separate concerns**: Keep business logic in controllers, utilities in utils
2. **Use fixtures** for configuration, not code
3. **Write tests** before fixing bugs
4. **Use type hints** in Python code
5. **Document your API** endpoints

### Security
1. **Always use** `frappe.whitelist()` for server-side methods
2. **Check permissions** with `frappe.has_permission()`
3. **Never expose** sensitive data in API responses
4. **Sanitize inputs** using frappe utils
5. **Use CSRF protection** built into Frappe

### Performance
1. **Cache frequently accessed data**
2. **Use database indexes** on filtered fields
3. **Batch database operations** when possible
4. **Lazy load** heavy computations
5. **Profile queries** using Frappe's debug mode

---

## Publishing Your App

### On Frappe Cloud
1. Push code to GitHub
2. Create account on Frappe Cloud
3. Create new bench/app
4. Connect GitHub repository
5. Deploy

### On GitHub
```bash
# Tag release
git tag v1.0.0
git push origin v1.0.0

# Create GitHub release with:
# - Version number
# - Release notes
# - Downloadable assets
```

---

## Related Topics
- [Bench Commands](./03_bench-commands.md)
- [DocType Fundamentals](../01_CORE_SYSTEM/01_doctype-fundamentals.md)
- [Controllers](../01_CORE_SYSTEM/04_controllers.md)
