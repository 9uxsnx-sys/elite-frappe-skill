# Workflow Configuration Guide

## Quick Reference
Complete guide to creating and configuring workflows in Frappe/ERPNext.

## AI Prompt
```
When creating workflows:
1. Define clear states and transitions
2. Set proper role-based permissions
3. Add conditions for automation
4. Test all transitions
5. Document for users
```

---

## What is a Workflow?

A workflow in Frappe defines:
- **States**: The different stages a document goes through
- **Transitions**: How to move from one state to another
- **Roles**: Who can perform each transition
- **Conditions**: Rules that must be met for transitions
- **Actions**: Automated actions on state changes

---

## Creating a Workflow

### Step 1: Create Workflow Document
```
1. Go to: Workflow List
2. Click "New"
3. Fill in:
   - Workflow Name
   - Document Type
   - Is Active: Yes
   - Override Status: Yes/No
```

### Step 2: Define States
Add states in the Workflow States child table:

| State | Style |
|-------|-------|
| Draft | Primary |
| Submitted | Success |
| Approved | Warning |
| Rejected | Danger |
| Cancelled | Secondary |

### Step 3: Define Transitions
Add transitions in the Workflow Transitions child table:

| Field | Description |
|-------|-------------|
| State | Current state |
| Action | Button label |
| Next State | Target state |
| Allowed Role | Who can perform |
| Condition | When allowed |

---

## Workflow Example: Purchase Approval

### Scenario
- Purchase Request < $5,000 → Auto-approve
- Purchase Request $5,000-$20,000 → Manager approval
- Purchase Request > $20,000 → Director approval

### Configuration
```python
# Workflow: Purchase Request Approval
# Document Type: Purchase Request

# States:
- Draft (Primary)
- Pending Approval (Warning)
- Approved (Success)
- Rejected (Danger)
- Cancelled (Secondary)

# Transitions:
{
    "state": "Draft",
    "action": "Submit for Approval",
    "next_state": "Pending Approval",
    "allowed_role": "Purchase User",
    "condition": "doc.total < 5000"  # Auto-approve small amounts
}
```

---

## Workflow States Configuration

### State Properties
| Property | Description |
|----------|-------------|
| State | Unique state name |
| Workflow State | Display name |
| Style | Color (Primary, Success, Warning, Danger, Secondary) |
| Document Status | 0=Draft, 1=Submitted, 2=Cancelled |

### Example States
```python
states = [
    {"state": "Draft", "style": "Primary"},
    {"state": "Pending Review", "style": "Warning"},
    {"state": "Approved", "style": "Success"},
    {"state": "Rejected", "style": "Danger"},
    {"state": "Cancelled", "style": "Secondary"}
]
```

---

## Workflow Transitions

### Transition Properties
| Property | Description |
|----------|-------------|
| State | Current state |
| Action | Button text user clicks |
| Next State | Target state |
| Allowed Role | Role that can perform |
| Condition | Field condition (JavaScript) |
| Allow Self Approval | Let creator approve |

### Condition Examples
```javascript
// Condition: Total > 10000
doc.total > 10000

// Condition: Specific item category
doc.category == "Electronics"

// Condition: Multiple conditions
doc.total > 10000 && doc.priority == "High"

// Condition: Check workflow state
doc.workflow_state == "Pending Approval"
```

---

## Client Script Integration

### Update Workflow State
```javascript
// In Purchase Request form
frappe.ui.form.on('Purchase Request', {
    refresh: function(frm) {
        // Custom buttons based on workflow state
        if (frm.doc.workflow_state == "Draft") {
            frm.add_custom_button("Submit", () => {
                frm.events.submit_for_approval(frm);
            });
        }
    },
    
    submit_for_approval: function(frm) {
        frm.set_value("workflow_state", "Pending Approval");
        frm.save();
    }
});
```

### Server Script Actions
```python
# In hooks.py or controller
def trigger_workflow(doc, action):
    """Trigger workflow action"""
    from frappe.workflow.doctype.workflow_action import workflow_action
    
    workflow_action.apply_workflow(doc, action)

# Usage
def on_submit(self):
    if self.total > 50000:
        self.trigger_workflow("Submit for Approval")
```

---

## Workflow Actions

### Creating Custom Actions
```python
# my_app/workflow.py
import frappe

def send_approval_notification(doc, workflow_state):
    """Send notification on workflow state change"""
    if workflow_state == "Pending Approval":
        # Notify approvers
        frappe.sendmail(
            recipients=get_approvers(doc),
            subject=f"Approval Required: {doc.doctype}",
            message=f"Please review {doc.name}"
        )

# Register in hooks.py
# workflow_action = "my_app.workflow.send_approval_notification"
```

### State-Specific Actions
```python
def on_workflow_state_change(doc, workflow_state):
    """Handle workflow state changes"""
    actions = {
        "Approved": on_approved,
        "Rejected": on_rejected,
        "Cancelled": on_cancelled
    }
    
    if workflow_state in actions:
        actions[workflow_state](doc)

def on_approved(doc):
    """Handle approval"""
    frappe.publish_realtime(
        f"workflow_{doc.doctype}_{doc.name}",
        {"status": "approved"}
    )

def on_rejected(doc):
    """Handle rejection"""
    doc.status = "Rejected"
    doc.save()
```

---

## Approval Workflow Matrix

### Example: Multi-Level Approval
```python
# Condition for each transition:

# Level 1: Manager Approval (>$5,000)
{
    "condition": "doc.total >= 5000",
    "allowed_role": "Purchase Manager"
}

# Level 2: Director Approval (>$20,000)
{
    "condition": "doc.total >= 20000", 
    "allowed_role": "Purchase Director"
}

# Self-approval for small amounts
{
    "condition": "doc.total < 5000",
    "allowed_role": "Purchase User",
    "allow_self_approval": 1
}
```

---

## Workflow Permissions

### Role-Based Access
```python
# Each transition can have different roles
transitions = [
    {
        "state": "Draft",
        "action": "Approve",
        "next_state": "Approved",
        "allowed_role": "Approver",  # Only approvers
    },
    {
        "state": "Approved",
        "action": "Review",
        "next_state": "Reviewed",
        "allowed_role": "Reviewer",  # Different role
    }
]
```

### Workflow State Field
When workflow is active, a `workflow_state` field is added to the document. 
Use it in conditions:

```javascript
// Only show button if workflow allows
if (frm.doc.workflow_state == "Pending Approval") {
    frm.add_custom_button("Approve", () => {
        // Approve action
    });
}
```

---

## Best Practices

### 1. Simple State Machine
- Keep states minimal (3-7 max)
- Clear, meaningful names
- Linear progression when possible

### 2. Clear Conditions
```javascript
// Good: Explicit
doc.total > doc.approval_limit

// Avoid: Complex nested
doc.total > 10000 && doc.status == "Active" && doc.items.length > 0
```

### 3. Role Clarity
```python
# Good: Single role per transition
allowed_role: "Purchase Manager"

# Avoid: Multiple roles (use separate transitions)
```

### 4. Testing
```python
# Test each transition
def test_workflow():
    # Create document
    doc = create_test_document()
    
    # Test each transition
    doc.submit()
    assert doc.workflow_state == "Pending Approval"
    
    doc.workflow_action = "Approve"
    doc.save()
    assert doc.workflow_state == "Approved"
```

---

## Common Issues

### Issue: Workflow Not Triggering
**Solution:**
- Check if workflow is active
- Verify role permissions
- Check condition evaluates to true

### Issue: Button Not Showing
**Solution:**
- Check current workflow state
- Verify role matches
- Add `allow_self_approval` if needed

### Issue: State Not Updating
**Solution:**
- Check workflow transitions exist
- Verify next_state is valid
- Ensure no validation errors

---

## Advanced: Dynamic Workflow

### Conditional States
```python
# Different workflow based on document values
def get_workflow_state(doc):
    if doc.docstatus == 0:
        return "Draft"
    
    if doc.total < 5000:
        return "Approved"  # Auto-approve
    
    return "Pending Approval"
```

### Parallel Approvals
```python
# Multiple approvers required
{
    "condition": "doc.total > 100000",
    "allowed_role": "Finance Manager"
},
{
    "condition": "doc.total > 100000", 
    "allowed_role": "Purchase Director"
}
```

---

## Related Topics
- [ERPNext Workflows](./01_erpnext-workflows.md)
- [Custom Fields](../15_CUSTOMIZATION/01_custom-fields.md)
- [Hooks Overview](../frappe-framework-master/04_HOOKS_SYSTEM/01_hooks-overview.md)
