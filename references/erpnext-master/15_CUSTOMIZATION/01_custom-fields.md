# Custom Fields

## Quick Reference
Custom Fields add new fields to existing DocTypes without modifying core code. Export as fixtures for version control and deployment.

## AI Prompt
```
When adding custom fields:
1. Use Customize Form or Custom Field DocType
2. Choose correct field type for data
3. Set appropriate permissions (perm level)
4. Export as fixture in hooks.py
5. Consider impact on existing data
```

---

## Creating Custom Fields

### Method 1: Customize Form (UI)
```
1. Go to Customize Form
2. Select DocType (e.g., Sales Invoice)
3. Add new row in fields section
4. Configure field properties
5. Save and reload
```

### Method 2: Python Script
```python
# Create custom field programmatically
custom_field = frappe.get_doc({
    "doctype": "Custom Field",
    "dt": "Sales Invoice",
    "label": "Delivery Notes",
    "fieldname": "delivery_notes",
    "fieldtype": "Small Text",
    "insert_after": "customer_name",
    "permlevel": 0,
    "mandatory_depends_on": "",
    "read_only": 0
})
custom_field.insert()
```

### Method 3: JSON Fixtures
```json
{
    "doctype": "Custom Field",
    "dt": "Sales Invoice",
    "label": "Branch Code",
    "fieldname": "branch_code",
    "fieldtype": "Data",
    "insert_after": "customer"
}
```

---

## Field Types

| Field Type | Use Case | Example |
|------------|----------|---------|
| Data | Short text | Branch Code |
| Text | Long text | Notes |
| Int | Whole numbers | Priority |
| Float | Decimal numbers | Discount % |
| Currency | Money amounts | Custom Charge |
| Date | Date picker | Delivery Date |
| Datetime | Date and time | Processing Time |
| Check | Boolean | Is Priority |
| Select | Dropdown list | Status |
| Link | Reference to DocType | Branch |
| Dynamic Link | Dynamic reference | Party |
| Text Editor | Rich text | Terms |
| Code | Code snippet | Script |
| Image | Image upload | Logo |
| Attach | File upload | Document |
| Table | Child table | Custom Items |

---

## Export Fixtures

### In hooks.py
```python
fixtures = [
    # Export all custom fields for specific DocTypes
    {
        "doctype": "Custom Field",
        "filters": [
            ["dt", "in", ["Sales Invoice", "Customer", "Item"]]
        ]
    },
    
    # Export specific custom fields
    {
        "doctype": "Custom Field",
        "filters": [
            ["name", "in", ["Sales Invoice-delivery_notes", "Customer-branch_code"]]
        ]
    }
]
```

### Export Command
```bash
bench --site [site] export-fixtures
```

---

## Common Patterns

### Add Field to Multiple DocTypes
```python
def add_custom_field_to_doctypes():
    doctypes = ["Sales Invoice", "Sales Order", "Delivery Note"]
    
    for dt in doctypes:
        if not frappe.db.exists("Custom Field", {"dt": dt, "fieldname": "branch_code"}):
            frappe.get_doc({
                "doctype": "Custom Field",
                "dt": dt,
                "label": "Branch Code",
                "fieldname": "branch_code",
                "fieldtype": "Link",
                "options": "Branch",
                "insert_after": "customer"
            }).insert()
    
    frappe.db.commit()
```

### Custom Field with Options
```python
frappe.get_doc({
    "doctype": "Custom Field",
    "dt": "Sales Invoice",
    "label": "Priority",
    "fieldname": "priority",
    "fieldtype": "Select",
    "options": "High\nMedium\nLow",
    "default": "Medium",
    "insert_after": "customer_name"
}).insert()
```

### Custom Child Table
```python
# First create the child DocType
frappe.get_doc({
    "doctype": "DocType",
    "name": "Custom Item Detail",
    "module": "Custom App",
    "istable": 1,
    "fields": [
        {"fieldname": "item", "fieldtype": "Link", "label": "Item", "options": "Item"},
        {"fieldname": "qty", "fieldtype": "Float", "label": "Quantity"},
        {"fieldname": "note", "fieldtype": "Text", "label": "Note"}
    ]
}).insert()

# Then add as custom field
frappe.get_doc({
    "doctype": "Custom Field",
    "dt": "Sales Invoice",
    "label": "Custom Items",
    "fieldname": "custom_items",
    "fieldtype": "Table",
    "options": "Custom Item Detail",
    "insert_after": "items"
}).insert()
```

---

## Validation with Custom Fields

### Via Server Script
```python
# In hooks.py
doc_events = {
    "Sales Invoice": {
        "validate": "custom_app.validation.validate_branch_code"
    }
}

# In custom_app/validation.py
def validate_branch_code(doc, method):
    if doc.branch_code and not frappe.db.exists("Branch", doc.branch_code):
        frappe.throw("Invalid Branch Code")
```

### Via Custom Script (Client)
```javascript
// In public/js/sales_invoice.js
frappe.ui.form.on('Sales Invoice', {
    branch_code: function(frm) {
        if (frm.doc.branch_code) {
            frappe.db.get_value('Branch', frm.doc.branch_code, 'name')
                .then(r => {
                    if (!r.message) {
                        frappe.msgprint('Invalid Branch Code');
                        frm.set_value('branch_code', '');
                    }
                });
        }
    }
});
```

---

## Best Practices

1. **Naming Convention**: Use descriptive fieldnames (e.g., `custom_branch_code`)
2. **Insert Position**: Use `insert_after` for logical placement
3. **Permissions**: Set correct `permlevel` for field security
4. **Default Values**: Set defaults where appropriate
5. **Validation**: Add validation via scripts, not field settings
6. **Fixtures**: Always export for version control

---

## Related Topics
- [Property Setters](./03_property-setters.md)
- [Custom Scripts](./02_custom-scripts.md)
- [Extending ERPNext](../16_EXTENDING_ERPNEXT/)
