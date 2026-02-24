# ERPNext Design Patterns

## Quick Reference
Common patterns for ERPNext development: Master-Detail, Event-Driven, Ledger Pattern, and Document State Machine.

## AI Prompt
```
When designing ERPNext solutions:
1. Use Master-Detail for hierarchical data
2. Leverage event hooks for extensibility
3. Apply Ledger Pattern for accounting
4. Use State Machine for workflows
5. Follow naming conventions
```

---

## Master-Detail Pattern

### Description
Parent document with child table items.

### Example: Sales Invoice
```python
# Master: Sales Invoice
# Detail: Sales Invoice Item

si = frappe.get_doc({
    "doctype": "Sales Invoice",
    "customer": "ABC Corp",
    "items": [  # Child table
        {"item_code": "ITEM-001", "qty": 2, "rate": 100},
        {"item_code": "ITEM-002", "qty": 1, "rate": 50}
    ]
})
```

---

## Event-Driven Pattern

### Description
Respond to document lifecycle events.

### Example: Hooks
```python
# hooks.py
doc_events = {
    "Sales Invoice": {
        "on_submit": "app.hooks.on_sales_invoice_submit"
    }
}

# app/hooks.py
def on_sales_invoice_submit(doc, method):
    # Send notification
    send_notification(doc)
    # Sync to external system
    sync_to_crm(doc)
```

---

## Ledger P
