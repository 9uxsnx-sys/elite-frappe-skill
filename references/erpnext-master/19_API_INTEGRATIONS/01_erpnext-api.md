# ERPNext REST API

## Quick Reference
ERPNext provides REST API for all CRUD operations. Use API Key/Secret or Token for authentication. All DocTypes accessible via /api/resource/ endpoint.

## AI Prompt
```
When using ERPNext API:
1. Use API Key/Secret for server-to-server
2. Use Token for user sessions
3. Handle pagination for large datasets
4. Validate all inputs
5. Use proper error handling
```

---

## Authentication

### API Key/Secret
```bash
# Create API Key in User settings
# Headers:
Authorization: token [api_key]:[api_secret]
```

### Token Based
```bash
# Get token
POST /api/method/frappe.auth.get_logged_user
# Response contains token in cookie
```

---

## CRUD Operations

### List Documents
```bash
GET /api/resource/Sales Invoice?fields=["name","customer","grand_total"]&filters=[["status","=","Unpaid"]]&limit_page_length=20

# Response
{
    "data": [
        {"name": "SI-001", "customer": "ABC Corp", "grand_total": 10000},
        {"name": "SI-002", "customer": "XYZ Ltd", "grand_total": 20000}
    ]
}
```

### Get Document
```bash
GET /api/resource/Sales Invoice/SI-001

# Response
{
    "data": {
        "name": "SI-001",
        "customer": "ABC Corp",
        "items": [...],
        "grand_total": 10000
    }
}
```

### Create Document
```bash
POST /api/resource/Sales Invoice
Content-Type: application/json

{
    "customer": "ABC Corp",
    "items": [
        {"item_code": "ITEM-001", "qty": 1, "rate": 100}
    ]
}
```

### Update Document
```bash
PUT /api/resource/Sales Invoice/SI-001
Content-Type: application/json

{
    "customer": "New Customer"
}
```

### Delete Document
```bash
DELETE /api/resource/Sales Invoice/SI-001
```

---

## Custom API Endpoints

### Whitelisted Method
```python
# In your app
@frappe.whitelist()
def get_customer_orders(customer):
    return frappe.get_all("Sales Order",
        filters={"customer": customer, "docstatus": 1},
        fields=["name", "transaction_date", "grand_total"]
    )
```

### Call Custom API
```bash
POST /api/method/custom_app.api.get_customer_orders
Content-Type: application/json

{
    "customer": "ABC Corp"
}
```

---

## Python Client

```python
import requests

base_url = "https://your-site.com"
api_key = "your_api_key"
api_secret = "your_api_secret"

headers = {
    "Authorization": f"token {api_key}:{api_secret}",
    "Content-Type": "application/json"
}

# Get list
response = requests.get(
    f"{base_url}/api/resource/Customer",
    headers=headers,
    params={"fields": '["name","customer_name"]'}
)

# Create
response = requests.post(
    f"{base_url}/api/resource/Customer",
    headers=headers,
    json={"customer_name": "New Customer"}
)
```

---

## Related Topics
- [Webhooks](./02_webhooks.md)
- [External APIs](./04_external-apis.md)
