# Controller Lifecycle & Hooks

## Quick Reference
Complete guide to Frappe Document controller lifecycle events and hooks.

## AI Prompt
```
When working with Frappe controllers:
1. Use appropriate hooks for different stages
2. Be aware of execution order
3. Avoid circular calls
4. Use flags to prevent recursion
5. Keep business logic in controllers
```

---

## Document Lifecycle

### Document States (docstatus)
| State | Description | Can Edit |
|-------|-------------|----------|
| 0 | Draft | Yes |
| 1 | Submitted | No (need to cancel first) |
| 2 | Cancelled | No |

---

## Controller Hooks

### Execution Order
```
1. __init__(self, doc)
2. before_load(doc) - Called before form loads
3. load_from_db() - Loads document from database
4. validate() - Called on insert and update
5. before_save() - Before saving
6. on_update() - After save (only for updates)
7. after_save() - After save
8. on_change() - When document field changes
```

---

## Core Hooks

### 1. before_load
```python
# Called before the document is loaded in the form
def before_load(self, doc):
    # Run when form is loading
    if not doc.docstatus:
        doc.default_status = "Open"
```

### 2. validate
```python
# Called on every save - best place for business logic
def validate(self):
    # Check required fields
    if not self.customer:
        frappe.throw("Customer is required")
    
    # Validate data
    self.validate_dates()
    self.validate_amounts()
    
    # Set default values
    if not self.status:
        self.status = "Draft"
```

### 3. before_save
```python
# Called before saving to database
def before_save(self):
    # Prepare data before saving
    self.set_title()
    self.calculate_totals()
    self.update_modified_details()
```

### 4. after_save
```python
# Called after successful save
def after_save(self):
    # Post-save operations
    frappe.publish_realtime("document_saved", {
        "doctype": self.doctype,
        "name": self.name
    })
```

### 5. on_update
```python
# Only called on UPDATE (not on first insert)
def on_update(self):
    # Track changes
    if self.has_changed("status"):
        self.log_status_change()
```

### 6. on_change
```python
# Called when specific field changes
def on_change(self):
    # Only runs when field value changes
    if self.has_changed("workflow_state"):
        self.notify_approvers()
```

---

## Submission Hooks

### 1. before_submit
```python
# Called before document is submitted
def before_submit(self):
    # Final validation before submission
    if not self.items:
        frappe.throw("Cannot submit without items")
    
    if self.total <= 0:
        frappe.throw("Total must be greater than zero")
```

### 2. on_submit
```python
# Called after successful submission
def on_submit(self):
    # Create related documents
    self.create_stock_entries()
    self.update_accounts()
    self.send_notification()
```

### 3. before_cancel
```python
# Called before cancellation
def before_cancel(self):
    # Check if cancellation is allowed
    if self.docstatus == 2:
        frappe.throw("Already cancelled")
    
    # Check dependencies
    if self.has_linked_documents():
        frappe.throw("Cannot cancel - linked documents exist")
```

### 4. on_cancel
```python
# Called after successful cancellation
def on_cancel(self):
    # Reverse related entries
    self.reverse_stock_entries()
    self.reverse_gl_entries()
```

### 5. after_cancel
```python
# Called after cancellation is complete
def after_cancel(self):
    # Cleanup operations
    self.cleanup_related()
```

---

## Deletion Hooks

### 1. before_delete
```python
# Called before document is deleted
def before_delete(self):
    # Check if deletion is allowed
    if self.status == "Active":
        frappe.throw("Cannot delete active records")
```

### 2. on_trash
```python
# Called after document is deleted
def on_trash(self):
    # Cleanup related data
    self.delete_related_logs()
```

---

## Common Methods

### Document State Checks
```python
def some_method(self):
    # Check document status
    if self.docstatus == 0:
        # Draft
        pass
    elif self.docstatus == 1:
        # Submitted
        pass
    elif self.docstatus == 2:
        # Cancelled
        pass
    
    # Check field changes
    if self.has_changed("status"):
        old_value = self.get_doc_before_save().status
        new_value = self.status
    
    # Check if new document
    if self.is_new():
        # This is a new document
        pass
```

### Saving Without Triggers
```python
# Save without triggering hooks
self.save(ignore_permissions=True)
self.save(ignore_version=True)

# Update single field without loading full doc
frappe.db.set_value("Sales Invoice", self.name, "status", "Completed")

# Update multiple fields
frappe.db.set_value("Sales Invoice", self.name, {
    "status": "Completed",
    "completed_on": frappe.utils.now()
})
```

---

## Real-World Examples

### Sales Invoice Controller
```python
import frappe
from frappe.model.document import Document

class SalesInvoice(Document):
    def validate(self):
        """Validate invoice before save"""
        self.validate_items()
        self.calculate_taxes()
        self.validate_credit_limit()
    
    def before_save(self):
        """Prepare invoice before saving"""
        self.set_payment_terms()
        self.update_serial_no()
    
    def on_submit(self):
        """After submission - create GL entries"""
        self.make_gl_entries()
        self.update_stock_ledger()
        self.enqueue_payment_reminder()
    
    def on_cancel(self):
        """Reverse everything on cancellation"""
        self.reverse_gl_entries()
        self.reverse_stock_ledger()
    
    def validate_items(self):
        """Validate all items have stock"""
        for item in self.items:
            if not item.warehouse:
                frappe.throw(f"Row {item.idx}: Warehouse required")
    
    def calculate_taxes(self):
        """Calculate tax amounts"""
        self.total_taxes = sum(tax.amount for tax in self.taxes)
        self.grand_total = self.net_total + self.total_taxes
    
    def validate_credit_limit(self):
        """Check customer credit limit"""
        if self.customer:
            credit_limit = frappe.db.get_value(
                "Customer", 
                self.customer, 
                "credit_limit"
            ) or 0
            
            outstanding = frappe.db.get_value(
                "Sales Invoice",
                {"customer": self.customer, "docstatus": ["!=", 2]},
                "sum(outstanding_amount)"
            ) or 0
            
            if outstanding + self.grand_total > credit_limit:
                frappe.throw("Credit limit exceeded")
```

### Custom Workflow Controller
```python
class ProjectTask(Document):
    def on_change(self):
        """Handle status changes"""
        if self.has_changed("status"):
            self.handle_status_change()
    
    def handle_status_change(self):
        """Process status change"""
        status_handlers = {
            "In Progress": self.on_in_progress,
            "Completed": self.on_completed,
            "On Hold": self.on_hold,
            "Cancelled": self.on_cancelled
        }
        
        handler = status_handlers.get(self.status)
        if handler:
            handler()
    
    def on_in_progress(self):
        """Start tracking time"""
        self.start_time = frappe.utils.now()
    
    def on_completed(self):
        """Complete the task"""
        if not self.completed_on:
            self.completed_on = frappe.utils.now()
        
        # Notify project manager
        frappe.publish_realtime(
            "task_completed",
            {"task": self.name, "project": self.project}
        )
    
    def on_cancelled(self):
        """Handle cancellation"""
        # Release assigned resources
        self.release_resources()
```

---

## Best Practices

### 1. Avoid Infinite Loops
```python
# Bad: Causes infinite loop
def on_update(self):
    self.status = "Updated"
    self.save()  # Triggers on_update again!

# Good: Use flags
def on_update(self):
    if not frappe.flags.in_update:
        frappe.flags.in_update = True
        self.status = "Updated"
        self.save()
        frappe.flags.in_update = False
```

### 2. Use Appropriate Hooks
- **validate**: Business rules and data validation
- **before_save**: Data preparation
- **after_save**: Notifications, publishing
- **on_submit/on_cancel**: Related document creation

### 3. Keep Methods Focused
```python
# Bad: One method doing everything
def validate(self):
    self.validate_dates()
    self.validate_items()
    self.validate_customer()
    self.calculate_totals()
    self.set_status()
    self.send_notifications()

# Good: Separate concerns
def validate(self):
    self.validate_dates()
    self.validate_items()
    self.validate_customer()

def before_save(self):
    self.calculate_totals()
    self.set_status()

def after_save(self):
    self.send_notifications()
```

---

## Related Topics
- [DocType Fundamentals](./01_doctype-fundamentals.md)
- [Controllers](./04_controllers.md)
- [Hooks System](../04_HOOKS_SYSTEM/01_hooks-overview.md)
