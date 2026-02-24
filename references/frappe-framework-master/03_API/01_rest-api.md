# REST API

## Quick Reference
Frappe provides REST API for all DocTypes. Authenticate via API Key/Secret or Token. All CRUD operations via /api/resource/ endpoint.

## AI Prompt
```
When using Frappe REST API:
1. Use API Key/Secret for server-to-server
2. Use Token for user sessions
3. Handle pagination with limit_start, limit_page_length
4. Use proper HTTP methods (GET, POST, PUT, DELETE)
5. Validate all inputs server-side
```

---

## Authentication

### API Key/Secret
```bash
# Create in User settings
# Headers:
Authorization: token api_key:api_secret
```

### Token-Based
```bash
# Login
POST /api/method/frappe.auth.login
{"usr": "user@example.com", "pwd": "password"}

# Response contains session cookie
```

---

## CRUD Operations

### List Documents
```bash
GET /api/resource/Task?fields=["name","subject","status"]&filters=[["status","=","Open"]]&limit_page_length=10

# Response
{
    "data": [
        {"name": "TASK-001", "subject": "First Task", "status": "Open"},
        {"name": "TASK-002", "subject": "Second Task", "status": "Open"}
    ]
}
```

### Get Document
```bash
GET /api/resource/Task/TASK-001

# Response
{
    "data": {
        "name": "TASK-001",
        "subject": "My Task",
        "status": "Open",
        "description": "..."
    }
}
```

### Create Document
```bash
POST /api/resource/Task
Content-Type: application/json

{
    "subject": "New Task",
    "status": "Open",
    "description": "Task description"
}

# Response
{
    "data": {
        "name": "TASK-003",
        "subject": "New Task",
        ...
    }
}
```

### Update Document
```bash
PUT /api/resource/Task/TASK-001
Content-Type: application/json

{
    "status": "Completed"
}

# Response
{
    "data": {
        "name": "TASK-001",
        "status": "Completed",
        ...
    }
}
```

### Delete Document
```bash
DELETE /api/resource/Task/TASK-001

# Response
{
    "message": "ok"
}
```

---

## Query Parameters

| Parameter | Description |
|-----------|-------------|
| fields | Fields to return ["name","field1"] |
| filters | Filter conditions [["field","=","value"]] |
| order_by | Sort field |
| limit_start | Pagination offset |
| limit_page_length | Page size |

---

## Custom API Methods

### Create Endpoint
```python
# In your app
@frappe.whitelist()
def get_task_statistics(project):
    """Get task statistics for a project"""
    tasks = frappe.get_all("Task",
        filters={"project": project},
        fields=["status", "count(*) as count"],
        group_by="status"
    )
    return tasks
```

### Call Custom Method
```bash
POST /api/method/app.api.get_task_statistics
Content-Type: application/json

{
    "project": "PROJ-001"
}

# Response
{
    "message": [
        {"status": "Open", "count": 5},
        {"status": "Completed", "count": 10}
    ]
}
```

---

## Python Client Example

```python
import requests

base_url = "https://your-site.com"
headers = {
    "Authorization": "token api_key:api_secret",
    "Content-Type": "application/json"
}

# List
response = requests.get(
    f"{base_url}/api/resource/Task",
    headers=headers,
    params={"fields": '["name","subject"]'}
)
tasks = response.json()["data"]

# Create
response = requests.post(
    f"{base_url}/api/resource/Task",
    headers=headers,
    json={"subject": "New Task"}
)
task = response.json()["data"]
```

---

## Related Topics
- [Whitelisted Methods](./02_whitelisted-methods.md)
- [Python API](./03_python-api-reference.md)
