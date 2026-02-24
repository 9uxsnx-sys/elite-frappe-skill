# ERPNext Workflows

## Quick Reference
Workflows define approval processes for documents. Set states, transitions, and approvers. Trigger notifications on state changes.

## AI Prompt
```
When designing workflows:
1. Define all possible states
2. Map transitions between states
3. Assign approvers by role
4. Set up notifications
5. Test thoroughly before deployment
```

---

## Workflow DocType

### Key Fields
| Field | Type | Description |
|-------|------|-------------|
| document_type | Link | Target DocType |
| is_active | Check | Active workflow |
| states | Table | Workflow states |
| transitions | Table | Allowed transitions |

---

## Creating Workflow

### Define Workflow
```python
wf = frappe.get_doc({
    "doctype": "Workflow",
    "workflow_name": "Sales Order Approval",
    "document_type": "Sales Order",
    "is_active": 1,
    "states": [
        {"state": "Draft", "doc_status": "0"},
        {"state": "Pending Approval", "doc_status": "0"},
        {"state": "Approved", "doc_status": "1"},
        {"state": "Rejected", "doc_status": "0"}
    ],
    "transitions": [
        {"state": "Draft", "action": "Submit", "next_state": "Pending Approval", "allowed": "Sales User"},
        {"state": "Pending Approval", "action": "Approve", "next_state": "Approved", "allowed": "Sales Manager"},
        {"state": "Pending Approval", "action": "Reject", "next_state": "Rejected", "allowed": "Sales Manager"}
    ]
})
wf.insert()
```

---

## Workflow State

### Check Current State
```python
doc = frappe.get_doc("Sales Order", "SO-001")
print(doc.workflow_state)
```

### Get Allowed Actions
```python
from frappe.workflow import get_transitions

transitions = get_transitions(doc)
for t in transitions:
    print(t.action)  # Available actions
```

### Apply Transition
```python
from frappe.workflow import apply_workflow

apply_workflow(doc, "Approve")
```

---

## Workflow Notifications

```python
# In Workflow, set email alert
# On state change, send notification to role
```

---

## Related Topics
- [Approval Flows](./02_approval-hierarchies.md)
- [Automation Actions](./03_automation-actions.md)
