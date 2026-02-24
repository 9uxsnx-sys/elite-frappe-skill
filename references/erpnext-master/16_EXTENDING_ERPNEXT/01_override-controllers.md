# Override Controllers

## Quick Reference
Override controllers to completely replace ERPNext DocType behavior. Use `override_doctype_class` hook. Last app wins.

## AI Prompt
```
When overriding controllers:
1. Only override when necessary
2. Call super() for standard behavior
3. Don't break existing functionality
4. Document changes thoroughly
5. Consider upgrade impact
```

---

## Override Hook

### In hooks.py
```python
override_doctype_class = {
    "Sales Invoice": "custom_app.overrides.sales_invoice.CustomSalesInvoice",
    "Purchase Order": "custom_app.overrides.purchase_order.CustomPurchaseOrder"
}
```

---

## Override Pattern

### Complete Override
```python
# custom_app/overrides/sales_invoice.py

import frappe
from frappe import _
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice

class CustomSalesInvoice(SalesInvoice):
    def validate(self):
        # Custom validation first
        self.validate_custom_rules()
        
        # Then call standard validation
        super().validate()
    
    def on_submit(self):
        # Custom logic before
        self.custom_pre_submit()
        
        # Standard submission
        super().on_submit()
        
        # Custom logic after
        self.custom_post_submit()
    
    def validate_custom_rules(self):
        """Add custom validation rules"""
        if self.total_amount > 100000:
            if not self.approved_by:
                frappe.throw(_("Large orders require approval"))
    
    def custom_post_submit(self):
        """Post submit custom logic"""
        self.notify_external_system()
        self.update_custom_ledger()
    
    def notify_external_system(self):
        """Sync to external CRM"""
        import requests
        requests.post("https://api.example.com/invoices", json={
            "invoice_id": self.name,
            "customer": self.customer,
            "amount": self.grand_total
        })
```

### Partial Override
```python
# Only override specific methods

class CustomSalesInvoice(SalesInvoice):
    # Only override validate
    def validate(self):
        self.add_custom_validation()
        super().validate()
    
    # All other methods use standard behavior
```

---

## Extend vs Override

### Extend (Additive)
```python
# hooks.py
extend_doctype_class = {
    "Sales Invoice": "custom_app.extensions.ExtendSalesInvoice"
}

# custom_app/extensions/sales_invoice.py
class ExtendSalesInvoice:
    """Extension adds methods without replacing"""
    
    def custom_method(self):
        """New method added to Sales Invoice"""
        return "Custom functionality"
    
    def get_custom_field_value(self):
        """Helper method"""
        return self.custom_field
```

### Override (Replacement)
```python
# hooks.py
override_doctype_class = {
    "Sales Invoice": "custom_app.overrides.CustomSalesInvoice"
}

# custom_app/overrides/sales_invoice.py
class CustomSalesInvoice(SalesInvoice):
    """Complete replacement - inherits but can replace methods"""
    pass
```

---

## Common Overrides

### Override GL Entry Creation
```python
class CustomSalesInvoice(SalesInvoice):
    def make_gl_entries(self):
        # Custom GL entry logic
        gl_entries = []
        
        # Standard entries
        gl_entries.extend(self.get_standard_gl_entries())
        
        # Additional custom entries
        if self.custom_charge:
            gl_entries.append({
                "account": "Custom Charges - MC",
                "credit": self.custom_charge,
                "debit": 0,
                "against": self.customer
            })
        
        from erpnext.accounts.general_ledger import make_gl_entries
        make_gl_entries(gl_entries)
```

### Override Stock Update
```python
class CustomDeliveryNote(DeliveryNote):
    def update_stock_ledger(self):
        # Custom stock logic
        for item in self.items:
            # Add custom stock validation
            if item.serial_no:
                self.validate_serial_location(item)
        
        # Call standard update
        super().update_stock_ledger()
```

### Override Naming
```python
class CustomSalesInvoice(SalesInvoice):
    def autoname(self):
        # Custom naming pattern
        from frappe.model.naming import make_autoname
        
        # Format: SI-CUSTOMER-YYYY-####
        self.name = make_autoname(
            f"SI-{self.customer[:3]}-{'YYYY'}-.####"
        )
```

---

## Best Practices

### 1. Always Call Super
```python
def on_submit(self):
    # Your custom code before
    self.do_something()
    
    # Standard behavior
    super().on_submit()
    
    # Your custom code after
    self.do_something_else()
```

### 2. Check Method Exists
```python
def validate(self):
    # Check if parent has method
    if hasattr(super(), 'validate'):
        super().validate()
    
    # Your custom validation
    self.custom_validate()
```

### 3. Handle Exceptions
```python
def on_submit(self):
    try:
        self.sync_to_external_system()
    except Exception as e:
        frappe.log_error(e, "External sync failed")
        # Don't block submission
    
    super().on_submit()
```

### 4. Document Changes
```python
class CustomSalesInvoice(SalesInvoice):
    """
    Custom Sales Invoice handler
    
    Overrides:
    - validate: Adds branch validation
    - on_submit: Syncs to CRM system
    
    New Methods:
    - sync_to_crm: Pushes invoice to CRM
    - validate_branch: Checks branch rules
    """
```

---

## Testing Overrides

```python
# tests/test_sales_invoice_override.py

import frappe
from custom_app.overrides.sales_invoice import CustomSalesInvoice

def test_custom_validation():
    si = frappe.new_doc("Sales Invoice")
    si.customer = "TEST-001"
    si.append("items", {"item_code": "ITEM-001", "qty": 1, "rate": 100})
    
    # Test custom validation
    si.total_amount = 150000  # Large order
    # Should throw error without approval
    try:
        si.save()
        assert False, "Should have thrown error"
    except frappe.ValidationError:
        pass  # Expected

def test_standard_behavior():
    si = frappe.new_doc("Sales Invoice")
    si.customer = "TEST-001"
    si.append("items", {"item_code": "ITEM-001", "qty": 1, "rate": 100})
    si.save()
    
    # Standard fields should work
    assert si.grand_total == 100
```

---

## Related Topics
- [Hooks System](./03_erpnext-hooks.md)
- [Custom Scripts](../15_CUSTOMIZATION/02_custom-scripts.md)
