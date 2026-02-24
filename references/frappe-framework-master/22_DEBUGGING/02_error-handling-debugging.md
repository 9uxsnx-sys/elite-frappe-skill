# Error Handling & Debugging Guide

## Quick Reference
Comprehensive guide to debugging Frappe/ERPNext applications and handling errors effectively.

## AI Prompt
```
When debugging Frappe applications:
1. Enable debug mode first
2. Check error logs systematically
3. Use frappe.errprint() for quick debugging
4. Understand the error traceback
5. Isolate the problem before fixing
```

---

## Debug Mode

### Enabling Debug Mode
```python
# Via bench command
bench set-config developer_mode 1 --site site1.local
bench set-config enable_debug 1 --site site1.local

# Or in site_config.json
{
    "developer_mode": 1,
    "enable_debug": 1
}
```

### Debug Toolbar
When enabled, you'll see a debug toolbar on every page showing:
- SQL queries executed
- Form objects loaded
- Timeline events
- Cache information

---

## Viewing Logs

### Log Locations
```bash
# Error logs
~/frappe-bench/sites/site1.local/logs/

# Frappe error log
tail -f ~/frappe-bench/sites/site1.local/logs/frappe.log

# Python traceback
tail -f ~/frappe-bench/sites/site1.local/logs/error.log

# Scheduler logs
tail -f ~/frappe-bench/sites/site1.local/logs/scheduler.log

# Web requests
tail -f ~/frappe-bench/logs/web.log
```

### Bench Logs Command
```bash
# View all logs
bench logs

# View specific number of lines
bench logs --lines 100

# Follow in real-time
bench logs -f
```

---

## Common Errors & Solutions

### 1. Permission Error
```
frappe.exceptions.PermissionError: No permission for User
```

**Solution:**
```python
# Check current user permissions
frappe.has_permission("Sales Invoice", "write")

# Add to your code
frappe.flags.ignore_permissions = True  # Use sparingly!

# Or properly check
if not frappe.has_permission("Sales Invoice", "create"):
    frappe.throw("No permission to create Sales Invoice")
```

### 2. Document Not Found
```
frappe.exceptions.DoesNotExistError: Document not found: Sales Invoice INV-2024-001
```

**Solution:**
```python
# Always check existence
if frappe.db.exists("Sales Invoice", "INV-2024-001"):
    doc = frappe.get_doc("Sales Invoice", "INV-2024-001")

# Or handle gracefully
try:
    doc = frappe.get_doc("Sales Invoice", "INV-2024-001")
except frappe.DoesNotExistError:
    frappe.throw("Invoice not found")
```

### 3. Database Lock Timeout
```
pymysql.err.OperationalError: (1205, 'Lock wait timeout exceeded')
```

**Solution:**
```python
# Use frappe.db.begin() for long operations
frappe.db.begin()

try:
    for item in items:
        process_item(item)
    frappe.db.commit()
except:
    frappe.db.rollback()
    raise

# Or disable foreign keys temporarily
frappe.db.sql("SET FOREIGN_KEY_CHECKS = 0")
# ... do work ...
frappe.db.sql("SET FOREIGN_KEY_CHECKS = 1")
```

### 4. Validation Error
```
frappe.exceptions.ValidationError: Value is required for field
```

**Solution:**
```python
# Check field before saving
if not doc.customer:
    frappe.throw("Customer is required")

# Or in DocType validation
def validate(self):
    if not self.customer:
        frappe.throw("Customer is required", frappe.MandatoryError)
```

### 5. Circular Reference
```
RecursionError: maximum recursion depth exceeded
```

**Solution:**
```python
# Add flags to prevent recursion
def on_update(self):
    if frappe.flags.in_update:
        return
    frappe.flags.in_update = True
    
    self.update_related()
    
    frappe.flags.in_update = False

# Or use db.set_value instead of save
frappe.db.set_value("Sales Invoice", self.name, "status", "Completed")
```

---

## Debugging Techniques

### 1. Print Debugging
```python
# Server-side print (appears in bench logs)
frappe.errprint("DEBUG: Reached here")
frappe.errprint(f"Customer: {self.customer}")
frappe.errprint(f"Items: {len(self.items)}")

# Console log (client-side)
console.log("DEBUG: Form loaded")

# Python print (for development)
print(f"Processing {len(items)} items")
```

### 2. Using Frappe's Debug
```python
# Print document
frappe.dev_log(doc.as_dict())

# Print SQL query
frappe.db.sql(query, as_dict=True)
print(frappe.db.last_query)

# Profile execution time
import time
start = time.time()
# ... code ...
frappe.errprint(f"Execution time: {time.time() - start}s")
```

### 3. Interactive Console
```bash
# Enter bench console
bench --site site1.local console

# Then run Python code
frappe.init(site='site1.local')
frappe.set_user('Administrator')
doc = frappe.get_doc('Sales Invoice', 'INV-2024-001')
print(doc.as_dict())
exit()
```

### 4. Browser Console Debugging
```javascript
// JavaScript debugging
frappe.ui.form.on('Sales Invoice', {
    refresh: function(frm) {
        console.log("Current docstatus:", frm.doc.docstatus);
        console.log("Customer:", frm.doc.customer);
        console.log("Items:", frm.doc.items);
    }
});

// Break on errors
window.onerror = function(msg, url, lineNo, columnNo, error {
    console.error("Error: ", msg, url, lineNo);
    return false;
};
```

---

## SQL Query Debugging

### Enable SQL Logging
```python
# In your code
frappe.flags.print_sql = True

# Or set in site_config
{
    "sql_format_json": 1,
    "allow_tests": 1
}
```

### Query Analysis
```python
# Explain query
query = "SELECT * FROM `tabSales Invoice` WHERE customer = 'CUST-001'"
frappe.db.sql(query, as_dict=True)

# Using EXPLAIN
frappe.db.sql("EXPLAIN SELECT * FROM `tabSales Invoice` WHERE customer = 'CUST-001'")

# Check slow queries
frappe.db.sql("SHOW PROCESSLIST")
```

### ORM Debugging
```python
# Print generated SQL
frappe.flags.in_print = False
invoices = frappe.get_all(
    "Sales Invoice",
    filters={"customer": "CUST-001", "docstatus": 1},
    fields=["name", "customer", "grand_total"]
)
# Check frappe.log for the actual SQL
```

---

## Error Handling Best Practices

### Try-Except Pattern
```python
import frappe
import traceback

def process_invoice(invoice_name):
    try:
        doc = frappe.get_doc("Sales Invoice", invoice_name)
        
        # Validate
        if not doc.items:
            frappe.throw("Invoice has no items")
        
        # Process
        for item in doc.items:
            update_stock(item)
        
        frappe.db.commit()
        return {"success": True}
        
    except frappe.ValidationError as e:
        frappe.db.rollback()
        frappe.throw(str(e))
        
    except Exception as e:
        frappe.db.rollback()
        # Log full traceback
        frappe.log_error(
            f"Error processing invoice {invoice_name}: {str(e)}\n{traceback.format_exc()}",
            "Invoice Processing Error"
        )
        return {"success": False, "error": str(e)}
```

### Custom Error Classes
```python
# Define custom errors
class InvoiceProcessingError(frappe.ValidationError):
    pass

class InsufficientStockError(frappe.ValidationError):
    pass

# Use them
def validate_inventory(self, item_code, qty):
    available = get_stock_balance(item_code)
    if available < qty:
        frappe.throw(
            f"Insufficient stock for {item_code}. Available: {available}, Required: {qty}",
            InsufficientStockError
        )
```

### Error Logging
```python
# Log error to Error Log DocType
frappe.log_error(
    "Custom Error Message",
    "Error Log Title",
    doc=doc  # Optional: link to document
)

# Log with context
frappe.log_error(
    f"Failed to process {len(items)} items\n{traceback.format_exc()}",
    "Batch Processing Error",
    {"items": [i.name for i in items], "user": frappe.session.user}
)
```

---

## Performance Debugging

### Identifying Slow Code
```python
import frappe
from frappe.utils import now_datetime
import time

def slow_function():
    start = now_datetime()
    
    # Code to profile
    result = process_data()
    
    end = now_datetime()
    duration = (end - start).total_seconds()
    
    if duration > 5:  # Log if > 5 seconds
        frappe.log_error(
            f"Function took {duration}s",
            "Performance Warning"
        )
    
    return result
```

### Using cProfile
```python
import cProfile
import pstats
import io

def profile_code():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Your code here
    process_sales()
    
    profiler.disable()
    
    # Print stats
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(20)  # Top 20 functions
    print(s.getvalue())
```

### Database Query Optimization
```python
# Bad: N+1 queries
for invoice in invoices:
    customer = frappe.get_doc("Customer", invoice.customer)  # Query for each!

# Good: Single query with joins
invoices = frappe.db.sql("""
    SELECT 
        si.name,
        si.customer,
        c.customer_name
    FROM `tabSales Invoice` si
    LEFT JOIN `tabCustomer` c ON si.customer = c.name
    WHERE si.docstatus = 1
""", as_dict=True)
```

---

## Debugging Background Jobs

### View Scheduled Jobs
```bash
bench --site site1.local list-jobs
```

### Check Job Status
```python
# In code
job = frappe.get_doc("Scheduled Job Log", job_name)
print(job.status, job.start_date, job.end_date)

# Check if job is queued
frappe.db.get_all(
    "RQ Job",
    filters={"status": "queued"},
    fields=["id", "func_name", "created_at"]
)
```

### Retry Failed Jobs
```python
# Manually retry
from frappe.utils.background_jobs import enqueue

# Re-queue a job
enqueue(
    "my_app.utils.my_function",
    queue="long",
    timeout=5000
)
```

---

## Common Debugging Scenarios

### Issue: Form Not Saving
1. Check browser console for JS errors
2. Check `frappe.log` for validation errors
3. Add `console.log(frm.fields_dict)` in JS
4. Check `onload` events in DocType

### Issue: Data Not Appearing
1. Clear cache: `bench --site site1.local clear-cache`
2. Check if document is submitted (docstatus = 1)
3. Verify permissions
4. Check if it's a role-based field

### Issue: Email Not Sending
1. Check Email Queue DocType
2. Check error log
3. Verify email settings
4. Check SMTP configuration

### Issue: Slow Page Load
1. Check SQL queries in debug mode
2. Look for missing indexes
3. Check for too many custom fields
4. Review custom scripts

---

## Related Topics
- [Common Errors](./01_common-errors.md)
- [Troubleshooting Guide](./05_troubleshooting-guide.md)
- [Performance Optimization](../12_CACHING/01_redis-cache.md)
