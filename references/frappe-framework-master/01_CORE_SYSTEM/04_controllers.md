# Controllers

## Quick Reference
Controllers are Python classes that extend Document. They handle business logic through lifecycle hooks: validate, on_update, on_submit, etc.

## AI Prompt
```
When writing controllers:
1. Extend from frappe.model.document.Document
2. Use hooks for lifecycle events
3. Call super() if overriding methods
4. Use frappe.throw() for validation errors
5. Keep logic in separate modules for complex features
```

---

## Controller Structure

```python
import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate

class Task(Document):
    """Task Controller"""
    
    # Lifecycle hooks
    def validate(self):
        """Called before save (insert or update)"""
        self.validate_dates()
        self.calculate_totals()
    
    def on_update(self):
        """Called after save (insert or update)"""
        self.update_related()
    
    def on_submit(self):
        """Called when document is submitted"""
        self.create_notifications()
    
    def on_cancel(self):
        """Called when document is cancelled"""
        self.cleanup()
    
    # Custom methods
    def validate_dates(self):
        if self.due_date and getdate(self.due_date) < getdate(self.creation):
            frappe.throw("Due date cannot be in the past")
    
    def calculate_totals(self):
        self.total = sum(flt(item.amount) for item in self.items)
```

---

## Lifecycle Hooks

### Insert Hooks
| Hook | When Called |
|------|-------------|
| before_insert | Before new document inserted |
| after_insert | After new document inserted |

### Save Hooks
| Hook | When Called |
|------|-------------|
| before_validate | Before validation |
| validate | During validation |
| before_save | Before saving to database |
| on_update | After saving to database |

### Submit Hooks
| Hook | When Called |
|------|-------------|
| before_submit | Before submission |
| on_submit | After submission |

### Cancel Hooks
| Hook | When Called |
|------|-------------|
| before_cancel | Before cancellation |
| on_cancel | After cancellation |

### Delete Hooks
| Hook | When Called |
|------|-------------|
| on_trash | Before deletion |
| after_delete | After deletion |

### Other Hooks
| Hook | When Called |
|------|-------------|
| autoname | To set document name |
| before_rename | Before renaming |
| after_rename | After renaming |
| on_change | After any change |

---

## Document Methods

### Accessing Fields
```python
class Task(Document):
    def validate(self):
        # Direct access
        subject = self.subject
        
        # Child tables
        for item in self.items:
            print(item.item_code, item.qty)
        
        # Get field value with default
        priority = self.get("priority", "Medium")
```

### Database Operations
```python
class Task(Document):
    def on_submit(self):
        # Update without triggering hooks
        self.db_set("status", "Completed")
        
        # Get value
        customer = frappe.db.get_value("Customer", self.customer, "customer_name")
        
        # Check existence
        if frappe.db.exists("Task", {"status": "Open", "project": self.project}):
            frappe.throw("Open tasks exist for this project")
```

### Saving
```python
doc = frappe.get_doc("Task", "TASK-001")
doc.status = "Completed"
doc.save()  # Triggers validate, before_save, on_update

doc.save(ignore_permissions=True)  # Skip permission check
doc.save(ignore_validate=True)  # Skip 
