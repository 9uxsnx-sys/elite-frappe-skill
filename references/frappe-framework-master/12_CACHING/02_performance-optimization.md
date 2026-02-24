# Performance Optimization Guide

## Quick Reference
Comprehensive guide to optimizing Frappe/ERPNext performance for high-traffic and data-intensive applications.

## AI Prompt
```
When optimizing Frappe performance:
1. Profile before optimizing
2. Cache frequently accessed data
3. Optimize database queries
4. Use async for long-running tasks
5. Monitor with New Relic or similar
```

---

## 1. Database Query Optimization

### Index Optimization
```sql
-- Add index for frequently filtered fields
ALTER TABLE `tabSales Invoice` ADD INDEX `idx_customer` (`customer`);
ALTER TABLE `tabSales Invoice` ADD INDEX `idx_docstatus` (`docstatus`);
ALTER TABLE `tabSales Invoice` ADD INDEX `idx_company` (`company`);
ALTER TABLE `tabSales Invoice` ADD INDEX `idx_posting_date` (`posting_date`);

-- Composite index for common query patterns
ALTER TABLE `tabSales Invoice` ADD INDEX `idx_company_docstatus` (`company`, `docstatus`);
```

### In Frappe, Use ORM with Optimization
```python
# Bad: Loads all fields
items = frappe.get_all("Item")

# Good: Select only needed fields
items = frappe.get_all(
    "Item",
    fields=["name", "item_name", "stock_uom"]
)

# Good: Use filters efficiently
items = frappe.get_all(
    "Item",
    filters={"is_stock_item": 1, "disabled": 0},
    fields=["name", "item_name"]
)

# Good: Limit results
items = frappe.get_all(
    "Item",
    limit=100,
    order_by="modified desc"
)
```

### Avoid N+1 Queries
```python
# Bad: N+1 query problem
invoices = frappe.get_all("Sales Invoice", filters={"docstatus": 1})
for inv in invoices:
    customer = frappe.get_doc("Customer", inv.customer)  # Query for each!

# Good: Single query with JOIN
invoices = frappe.db.sql("""
    SELECT 
        si.name,
        si.customer,
        c.customer_name,
        c.mobile_no
    FROM `tabSales Invoice` si
    LEFT JOIN `tabCustomer` c ON si.customer = c.name
    WHERE si.docstatus = 1
    LIMIT 100
""", as_dict=True)

# Good: Get all in one go and process in memory
customers = {c.name: c for c in frappe.get_all("Customer", as_dict=True)}
for inv in invoices:
    customer_name = customers.get(inv.customer).customer_name
```

---

## 2. Caching Strategies

### Frappe Cache API
```python
import frappe

# Set cache
frappe.cache().set_value("my_key", "my_value", expires_in_sec=3600)

# Get cache
value = frappe.cache().get_value("my_key")

# Delete cache
frappe.cache().delete_value("my_key")

# Delete pattern
frappe.cache().delete_pattern("product_*")

# Hash operations (for multiple keys)
frappe.cache().hset("my_hash", "field1", "value1")
frappe.cache().hget("my_hash", "field1")
frappe.cache().hdel("my_hash", "field1")
```

### Application-Level Caching
```python
import frappe

def get_company_settings(company):
    """Cached company settings"""
    cache_key = f"company_settings_{company}"
    settings = frappe.cache().get_value(cache_key)
    
    if not settings:
        settings = frappe.get_doc("Company", company)
        frappe.cache().set_value(cache_key, settings.as_dict(), expires_in_sec=3600)
    
    return settings

def invalidate_company_cache(company):
    """Clear cache when company is updated"""
    frappe.cache().delete_value(f"company_settings_{company}")
```

### Redis Cache Configuration
```json
{
    "redis_cache": "redis://localhost:13000",
    "redis_queue": "redis://localhost:13001",
    "redis_socket": "redis://localhost:13002"
}
```

---

## 3. Document Loading Optimization

### Lazy Loading
```python
# Bad: Load all child tables immediately
doc = frappe.get_doc("Sales Invoice", "INV-001")
# Items already loaded!

# Good: Access child tables only when needed
doc = frappe.get_doc("Sales Invoice", "INV-001", for_load=True)
if need_items:
    items = doc.items  # Now loads
```

### Use `get_value` for Single Values
```python
# Bad: Full document for single field
doc = frappe.get_doc("Item", "ITEM-001")
item_group = doc.item_group

# Good: Direct database query
item_group = frappe.db.get_value("Item", "ITEM-001", "item_group")

# Even better: Multiple values
item_data = frappe.db.get_value(
    "Item", 
    "ITEM-001", 
    ["item_name", "item_group", "stock_uom"],
    as_dict=True
)
```

### Field Selection in get_all
```python
# Bad: Fetch all fields
transactions = frappe.get_all("Sales Invoice")

# Good: Explicit fields
transactions = frappe.get_all(
    "Sales Invoice",
    fields=[
        "name", "customer", "grand_total", 
        "outstanding_amount", "posting_date"
    ]
)
```

---

## 4. Background Jobs for Heavy Processing

### Enqueue Heavy Tasks
```python
import frappe
from frappe.utils import enqueue

def send_bulk_emails(emails, subject, message):
    """Process in background"""
    for email in emails:
        send_email(email, subject, message)

# Call as background job
enqueue(
    "my_app.utils.send_bulk_emails",
    emails=email_list,
    subject="Bulk Email",
    message="Content",
    queue="long",  # or "default", "short"
    timeout=3600
)
```

### Queue Types
| Queue | Use Case | Timeout |
|-------|----------|---------|
| short | Quick tasks (< 5 min) | 300s |
| default | Normal tasks (< 30 min) | 1800s |
| long | Heavy tasks (> 30 min) | 3600s+ |

### Scheduled Jobs for Recurring Tasks
```python
# In hooks.py
scheduler_events = {
    "daily": [
        "my_app.utils.daily_summary"
    ],
    "hourly": [
        "my_app.utils.sync_data"
    ]
}

# my_app/utils.py
import frappe

@frappe.whitelist()
def daily_summary():
    """Generate daily report"""
    # Heavy processing here
    generate_sales_report()
    update_dashboard()
    frappe.log_error("Daily summary generated", "Scheduled Job")
```

---

## 5. Frontend Optimization

### Minimize API Calls
```javascript
// Bad: Multiple calls
frappe.call({
    method: "my_app.api.get_data",
    callback: function(r) { /* ... */ }
});

// Good: Batch requests
frappe.call({
    method: "my_app.api.get_dashboard_data",
    callback: function(r) {
        // Single response with all data
        renderSales(r.message.sales);
        renderInventory(r.message.inventory);
        renderHR(r.message.hr);
    }
});
```

### Use Lazy Loading
```javascript
// Only load when needed
$('.report-section').on('click', function() {
    frappe.call({
        method: 'my_app.api.get_report_data',
        callback: function(r) {
            renderReport(r.message);
        }
    });
});
```

### Optimize Client Scripts
```javascript
// Bad: Run on every field change
frappe.ui.form.on('Sales Invoice', {
    customer: function(frm) {
        // Heavy calculation
    }
});

// Good: Use debounce
var debouncedCalculation = _.debounce(function() {
    calculateTotals();
}, 500);

frappe.ui.form.on('Sales Invoice', {
    items: function(frm) {
        debouncedCalculation();
    }
});
```

---

## 6. Server Configuration

### Gunicorn Workers
```python
# Procfile or bench configuration
web: gunicorn -b 0.0.0.0:8000 --workers 4 --timeout 120 frappe.app:application --worker-class gthread

# Worker calculation: 2-4 workers per CPU core
# For 4 cores: 8-16 workers
```

### Database Connection Pooling
```python
# In site_config.json
{
    "db_pool_size": 10,
    "db_pool_max": 20
}
```

### Nginx Caching
```nginx
# /etc/nginx/sites-available/frappe
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=frappe_cache:100m max_size=1g inactive=60m use_temp_path=off;

server {
    location /api {
        proxy_pass http://localhost:8000;
        proxy_cache_valid 200 60m;
        add_header X-Cache-Status $upstream_cache_status;
    }
}
```

---

## 7. Monitoring & Profiling

### Enable Query Logging
```python
# Temporary debug
frappe.flags.print_sql = True

# In site_config for debugging
{
    "enable_query_logging": 1
}
```

### Custom Performance Logging
```python
import frappe
import time

def timed_function(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        
        if duration > 1:  # Log if > 1 second
            frappe.log_error(
                f"Function {func.__name__} took {duration:.2f}s",
                "Performance Log"
            )
        return result
    return wrapper

# Usage
@timed_function
def heavy_calculation():
    # ... code ...
    pass
```

### Use New Relic for APM
```python
# In your app's hooks.py or custom start script
import newrelic.agent

# Configure in newrelic.ini
# newrelic.ini should be in your bench/config
```

---

## 8. Common Performance Pitfalls

### Pitfall 1: Too Many Custom Fields
```python
# Bad: 50+ custom fields on a frequently used DocType
# Impact: Slow form loading, larger database

# Solution: Use child tables for rarely used fields
# Or use separate DocTypes with links
```

### Pitfall 2: Real-time Updates
```python
# Bad: Publish on every save
def on_update(self):
    frappe.publish_realtime('data_updated', self.as_dict())

# Good: Batch or conditional publishing
def on_update(self):
    if self.has_changed('status'):
        frappe.publish_realtime('status_changed', {
            'doc': self.name, 
            'status': self.status
        })
```

### Pitfall 3: Heavy Validations
```python
# Bad: Query database in validate for each item
def validate(self):
    for item in self.items:
        stock = get_stock_balance(item.item_code)  # Query for each!

# Good: Batch load all needed data
def validate(self):
    item_codes = [item.item_code for item in self.items]
    stocks = {i.item_code: i.actual_qty for i in frappe.get_all(
        "Bin", 
        filters={"item_code": ["in", item_codes]},
        fields=["item_code", "actual_qty"]
    )}
    
    for item in self.items:
        if stocks.get(item.item_code, 0) < item.qty:
            frappe.throw(f"Insufficient stock for {item.item_code}")
```

---

## 9. Quick Wins Checklist

| Optimization | Impact | Effort |
|--------------|--------|--------|
| Add database indexes | High | Low |
| Cache frequently accessed data | High | Low |
| Use `get_value` instead of `get_doc` | Medium | Low |
| Select only needed fields | High | Low |
| Enqueue heavy background tasks | High | Medium |
| Optimize N+1 queries | High | Medium |
| Minify JavaScript/CSS | Medium | Low |
| Enable Redis caching | High | Medium |
| Use CDN for static files | Medium | Medium |
| Database connection pooling | Medium | Low |

---

## Related Topics
- [Redis Cache](./01_redis-cache.md)
- [Background Jobs](../09_BACKGROUND_JOBS/01_scheduler-overview.md)
- [Error Handling & Debugging](../22_DEBUGGING/02_error-handling-debugging.md)
