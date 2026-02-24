# ERPNext Troubleshooting Guide

## Quick Reference
Step-by-step debugging workflow for ERPNext issues. Start with logs, isolate the problem, trace code, and apply fixes.

## AI Prompt
```
When troubleshooting ERPNext:
1. Reproduce the issue
2. Check Error Log and bench logs
3. Identify the component (DocType, workflow, integration)
4. Trace code execution
5. Test fix in development
6. Document the solution
```

---

## Troubleshooting Workflow

### Step 1: Reproduce the Issue
```
- Document exact steps to reproduce
- Note error messages
- Check if it's user-specific or global
- Verify if it's data-specific
```

### Step 2: Check Logs
```bash
# Error Log in Desk
# Tools > Error Log

# Bench logs
tail -f logs/bench-start.log

# Web error logs
tail -f logs/web.error.log

# Worker logs
tail -f logs/worker.log

# Schedule logs
tail -f logs/schedule.log
```

### Step 3: Isolate the Component
```
Is it:
- Frontend (JS) issue?
- Backend (Python) issue?
- Database issue?
- Permission issue?
- Configuration issue?
```

---

## Common Issues by Category

### Document Issues

#### "Document not found"
```python
# Debug: Check if document exists
frappe.db.exists("Sales Invoice", "SI-001")

# Debug: Check naming
frappe.db.get_value("Sales Invoice", {"customer": "ABC"}, "name")

# Debug: Check permissions
frappe.has_permission("Sales Invoice", "read", "SI-001")
```

#### "Cannot edit submitted document"
```python
# Solution: Cancel first, then edit
doc = frappe.get_doc("Sales Invoice", "SI-001")
doc.cancel()
# Now can modify and resubmit
```

#### "Linked with another document"
```python
# Find linked documents
frappe.get_all("GL Entry", 
    filters={"voucher_no": "SI-001"},
    fields=["name", "account"]
)

# Check references in child tables
```

### Stock Issues

#### "Negative stock"
```python
# Debug: Check stock ledger
from erpnext.stock.utils import get_stock_balance
balance = get_stock_balance("ITEM-001", "Stores - MC")

# Debug: Get stock ledger entries
frappe.get_all("Stock Ledger Entry",
    filters={"item_code": "ITEM-001"},
    fields=["actual_qty", "posting_date", "voucher_no"],
    order_by="posting_date, creation"
)

# Fix: Stock Reconciliation
sr = frappe.new_doc("Stock Reconciliation")
sr.purpose = "Stock Reconciliation"
# Add items with correct quantities
```

#### "Valuation rate missing"
```python
# Debug: Check item valuation
frappe.db.get_value("Item", "ITEM-001", "valuation_rate")

# Debug: Check stock valuation entries
frappe.get_all("Stock Ledger Entry",
    filters={"item_code": "ITEM-001", "valuation_rate": 0}
)

# Fix: Set valuation rate
frappe.db.set_value("Item", "ITEM-001", "valuation_rate", 100)
```

### Accounting Issues

#### "GL Entry not balancing"
```python
# Debug: List all GL entries for voucher
entries = frappe.get_all("GL Entry",
    filters={"voucher_no": "SI-001"},
    fields=["account", "debit", "credit"]
)

for e in entries:
    print(f"{e.account}: Dr {e.debit}, Cr {e.credit}")

total_dr = sum(e.debit for e in entries)
total_cr = sum(e.credit for e in entries)
print(f"Difference: {total_dr - total_cr}")

# Fix: Check if all entries were created
# May need to cancel and recreate
```

#### "Account not found"
```python
# Debug: Check account with abbreviation
account = "Sales - MC"  # Include company abbreviation

# List all accounts for company
frappe.get_all("Account",
    filters={"company": "My Company Ltd"},
    fields=["name", "account_name"]
)
```

### Permission Issues

#### "No permission"
```python
# Debug: Check user roles
frappe.get_roles("user@example.com")

# Debug: Check DocType permissions
frappe.get_all("DocPerm",
    filters={"parent": "Sales Invoice"},
    fields=["role", "permlevel", "read", "write"]
)

# Debug: Check if user has permission
frappe.has_permission("Sales Invoice", "write")
```

### Performance Issues

#### "Slow document load"
```python
# Debug: Check number of fields
meta = frappe.get_meta("Sales Invoice")
print(f"Fields: {len(meta.fields)}")

# Debug: Check custom fields
frappe.get_all("Custom Field", filters={"dt": "Sales Invoice"})

# Debug: Check linked queries
# Use frappe.db.sql with EXPLAIN
frappe.db.sql("EXPLAIN SELECT * FROM `tabSales Invoice` WHERE customer = 'ABC'")
```

---

## Debugging Tools

### Python Console
```bash
bench --site [site] console

# In console
>>> import frappe
>>> frappe.db.get_value("Customer", "ABC", "credit_limit")
>>> doc = frappe.get_doc("Sales Invoice", "SI-001")
>>> doc.as_dict()
```

### Query Debug
```python
# Enable SQL logging
frappe.db.sql_debug = True

# Run queries - check bench-start.log
frappe.db.sql("SELECT * FROM tabCustomer LIMIT 1")
```

### Breakpoints
```python
# Add in code
import pdb; pdb.set_trace()

# Or use frappe.log_error for production
frappe.log_error(f"Debug: {doc.as_dict()}", "Custom Debug")
```

---

## Recovery Procedures

### Cancel Stuck Document
```python
# If document stuck in inconsistent state
doc = frappe.get_doc("Sales Invoice", "SI-001")
frappe.db.set_value("Sales Invoice", "SI-001", "docstatus", 0)
doc.reload()
doc.delete()
```

### Rebuild Indexes
```bash
bench --site [site] rebuild-global-search
bench --site [site] clear-cache
```

### Reset Permissions
```python
# Reset DocType permissions
from frappe.desk.doctype.doctype.doctype import reset_permissions
reset_permissions("Sales Invoice")
```

---

## Related Topics
- [Common Errors](./01_common-errors.md)
- [Performance Debugging](./03_performance-debugging.md)
