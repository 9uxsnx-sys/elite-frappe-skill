# Desk UI

## Quick Reference
Desk is the admin interface built with Vue.js. Customize via Form Scripts, Client Scripts, and Page customizations.

## AI Prompt
```
When customizing Desk:
1. Use form scripts for form behavior
2. Use client scripts for quick customizations
3. Use workspace for navigation
4. Use page customizations for layout
```

---

## Form Scripts

### Basic Structure
```javascript
frappe.ui.form.on('Task', {
    refresh: function(frm) {
        // Called when form is loaded/refreshed
    },
    status: function(frm) {
        // Called when status field changes
    },
    on_submit: function(frm) {
        // Called after form is submitted
    }
});
```

### Common Patterns

#### Add Custom Button
```javascript
refresh: function(frm) {
    frm.add_custom_button('Complete', function() {
        frm.set_value('status', 'Completed');
        frm.save();
    }, 'Actions');
}
```

#### Set Field Properties
```javascript
refresh: function(frm) {
    frm.toggle_display('completed_date', frm.doc.status === 'Completed');
    frm.set_df_property('status', 'read_only', frm.doc.docstatus === 1);
}
```

#### Fetch Data
```javascript
customer: function(frm) {
    if (frm.doc.customer) {
        frappe.db.get_value('Customer', frm.doc.customer, 'customer_name')
            .then(r => {
                frm.set_value('customer_name', r.message.customer_name);
            });
    }
}
```

---

## Child Table Scripts

```javascript
frappe.ui.form.on('Task Item', {
    item_code: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        frappe.db.get_value('Item', row.item_code, 'item_name')
            .then(r => {
                frappe.model.set_value(cdt, cdn, 'item_name', r.message.item_name);
            });
    },
    qty: function(frm, cdt, cdn) {
        calculate_total(frm, cdt, cdn);
    }
});

function calculate_total(frm, cdt, cdn) {
    var row = locals[cdt][cdn];
    var total = (row.qty || 0) * (row.rate || 0);
    frappe.model.set_value(cdt, cdn, 'total', total);
}
```

---

## Client Scripts (Server-Side)

```python
# Create via Desk
# Tools > Client Script

# Or programmatically
script = frappe.get_doc({
    "doctype": "Client Script",
    "dt": "Task",
    "script": """
        frappe.ui.form.on('Task', {
            refresh: function(frm) {
                console.log('Form refreshed');
            }
        });
    """,
    "enabled": 1
})
script.insert()
```

---

## Workspace Customization

```python
# Create custom workspace
workspace = frappe.get_doc({
    "doctype": "Workspace",
    "title": "Task Management",
    "icon": "check",
    "charts": [...],
    "shortcuts": [...],
    "links": [...]
})
workspace.insert()
```

---

## Related Topics
- [Form Scripts](./02_form-scripts.md)
