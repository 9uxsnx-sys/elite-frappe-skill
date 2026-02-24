# Whitelisted Methods

## Quick Reference
@frappe.whitelist() decorator exposes methods for API calls. Methods must return JSON-serializable data.

## AI Prompt
```
When creating API methods:
1. Always use @frappe.whitelist()
2. Validate all inputs
3. Check permissions
4. Return JSON-serializable data
```

---

## Creating Whitelisted Methods

### Basic Method
```python
import frappe
from frappe import _

@frappe.whitelist()
def get_customer_info(customer):
    if not frappe.db.exists("Customer", customer):
        frappe.throw("Customer not found")
    return frappe.get_doc("Customer", customer).as_dict()
```

### With Multiple Arguments
```python
@frappe.whitelist()
def create_task(subject, description=None, priority="Medium"):
    task = frappe.get_doc({
        "doctype": "Task",
        "subject": subject,
        "description": description,
        "priority": priority
    })
    task.insert()
    return task.name
```

---

## Calling Methods

### From JavaScript
```javascript
frappe.call({
    method: 'app.api.get_customer_info',
    args: { customer: 'CUST-001' },
    callback: function(r) {
        console.log(r.message);
    }
});
```

### From External
```bash
POST /api/method/app.api.get_customer_info
Content-Type: application/json
{"customer": "CUST-001"}
```

---

## Security

```python
# Guest access
@frappe.whitelist(allow_guest=True)
def public_api():
    return {"status": "ok"}

# Permission check
@frappe.whitelist()
def get_sensitive_data(record_id):
    if not frappe.has_permission("Sensitive Data", "read"):
        frappe.throw("No permission")
    return frappe.get_doc("Sensitive Data", record_id).as_dict()
```

---

## Related Topics
- [REST API](./01_rest-api.md)
