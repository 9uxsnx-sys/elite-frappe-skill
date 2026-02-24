# DocType Fundamentals

## Quick Reference
DocType is the core building block. It defines database schema, form UI, and controller logic. Each DocType creates a database table and a Python controller class.

## AI Prompt
```
When creating DocTypes:
1. Use singular names (Task, not Tasks)
2. Choose correct field types
3. Set mandatory fields appropriately
4. Configure permissions
5. Write controller for business logic
```

---

## DocType Components

### 1. JSON Definition (Schema)
```json
{
    "doctype": "DocType",
    "name": "Task",
    "module": "Tasks",
    "fields": [
        {
            "fieldname": "subject",
            "fieldtype": "Data",
            "label": "Subject",
            "reqd": 1
        },
        {
            "fieldname": "description",
            "fieldtype": "Text Editor",
            "label": "Description"
        },
        {
            "fieldname": "status",
            "fieldtype": "Select",
            "options": "Open\nIn Progress\nCompleted",
            "default": "Open"
        },
        {
            "fieldname": "due_date",
            "fieldtype": "Date",
            "label": "Due Date"
        }
    ],
    "permissions": [
        {
            "role": "System Manager",
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1
        }
    ]
}
```

### 2. Python Controller
```python
# task.py
import frappe
from frappe.model.document import Document

class Task(Document):
    def validate(self):
        if self.due_date and self.due_date < frappe.utils.today():
            frappe.throw("Due date cannot be in the past")
    
    def on_update(self):
        frappe.publish_realtime('task_updated', self.name)
```

### 3. JavaScript Client Script
```javascript
// task.js
frappe.ui.form.on('Task', {
    refresh: function(frm) {
        if (frm.doc.status === 'Completed') {
            frm.add_custom_button('Reopen', function() {
                frm.set_value('status', 'Open');
                frm.save();
            });
        }
    },
    status: function(frm) {
        if (frm.doc.status === 'Completed') {
            frm.set_value('completed_date', frappe.datetime.get_today());
        }
    }
});
```

---

## Field Types

| Field Type | Use Case | Database Type |
|------------|----------|---------------|
| Data | Short text | varchar(255) |
| Text | Long text | text |
| Text Editor | Rich text | longtext |
| Int | Integer numbers | int |
| Float | Decimal numbers | decimal |
| Currency | Money | decimal |
| Percent | Percentage | decimal |
| Date | Date | date |
| Datetime | Date and time | datetime |
| Time | Time | time |
| Check | Boolean | int(1) |
| Select | Dropdown | varchar(255) |
| Link | Reference | varchar(255) |
| Dynamic Link | Dynamic reference | varchar(255) |
| Table | Child table | (child table) |
| Attach | File upload | text |
| Image | Image upload | text |
| Code | Code editor | text |

---

## DocType Properties

### Core Properties
| Property | Description |
|----------|-------------|
| module | Module this DocType belongs to |
| is_submittable | Can be submitted (docstatus 0→1) |
| is_tree | Hierarchical structure |
| is_child_table | Child table of another DocType |
| is_single | Single record (settings) |
| is_virtual | No database table |

### Naming
| Property | Description |
|----------|-------------|
| naming_series | Auto-naming pattern |
| autoname | Custom naming rule |
| title_field | Field for display name |

---

## Creating DocTypes

### Via Desk
```
1. Go to DocType List
2. Click "New"
3. Fill in properties
4. Add fields
5. Configure permissions
6. Save
```

### Via Python
```python
import frappe

doctype = frappe.get_doc({
    "doctype": "DocType",
    "name": "Custom Task",
    "module": "Custom Module",
    "fields": [
        {"fieldname": "subject", "fieldtype": "Data", "label": "Subject", "reqd": 1}
    ]
})
doctype.insert()
```

---

## DocType vs Database

```
DocType "Task" → Database table "tabTask"

Fields:
- subject → `subject` column (varchar)
- description → `description` column (text)
- status → `status` column (varchar)

Auto-added columns:
- name (primary key)
- creation (datetime)
- modified (datetime)
- owner (varchar)
- modified_by (varchar)
- docstatus (int)
- parent (varchar)
- parentfield (varchar)
- parenttype (varchar)
- idx (int)
```

---

## Related Topics
- [Controllers](./04_controllers.md)
- [Field Types](./02_doctype-fields.md)
