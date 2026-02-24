# Webhooks

## Quick Reference
Webhooks send HTTP POST requests on document events. Configure in Webhook DocType. Use for real-time integrations.

## AI Prompt
```
When setting up webhooks:
1. Choose correct trigger event
2. Structure payload properly
3. Handle authentication
4. Implement retry logic
5. Log responses for debugging
```

---

## Creating Webhook

### Via Desk
```
Setup > Webhook > New

- Webhook Name: Sales Invoice Sync
- Document Type: Sales Invoice
- Event: on_submit
- Request URL: https://api.example.com/webhook
- Condition: doc.grand_total > 10000
```

### Via Python
```python
webhook = frappe.get_doc({
    "doctype": "Webhook",
    "webhook_name": "Sales Invoice Sync",
    "document_type": "Sales Invoice",
    "event": "on_submit",
    "request_url": "https://api.example.com/webhook",
    "condition": "doc.grand_total > 10000",
    "webhook_headers": [
        {"key": "Authorization", "value": "Bearer xxx"}
    ]
})
webhook.insert()
```

---

## Webhook Events

| Event | Trigger |
|-------|---------|
| before_insert | Before document created |
| after_insert | After document created |
| before_save | Before document saved |
| on_update | After document updated |
| on_submit | After document submitted |
| on_cancel | After document cancelled |
| on_trash | Before document deleted |
| on_update_after_submit | After update on submitted doc |

---

## Webhook Request

### Headers
```json
{
    "Content-Type": "application/json",
    "Authorization": "Bearer xxx"
}
```

### Payload
```json
{
    "doctype": "Sales Invoice",
    "name": "SI-001",
    "event": "on_submit",
    "data": {
        "customer": "ABC Corp",
        "grand_total": 10000,
        "items": [...]
    }
}
```

---

## Custom Payload

```python
# In webhook, enable "Enable Custom Payload"
# Use Jinja templating:
{
    "invoice_id": "{{ doc.name }}",
    "customer": "{{ doc.customer }}",
    "amount": {{ doc.grand_total }},
    "date": "{{ doc.posting_date }}"
}
```

---

## Testing Webhooks

```python
# View webhook logs
logs = frappe.get_all("Webhook Log",
    filters={"webhook": "Sales Invoice Sync"},
    fields=["name", "creation", "status", "response"],
    order_by="creation desc"
)
```

---

## Related Topics
- [ERPNext API](./01_erpnext-api.md)
- [External APIs](./04_external-apis.md)
