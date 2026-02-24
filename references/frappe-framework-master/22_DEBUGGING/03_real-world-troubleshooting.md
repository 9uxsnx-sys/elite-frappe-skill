# Real-World Troubleshooting Guide

## Quick Reference
Common Frappe/ERPNext issues encountered in production and their solutions.

## AI Prompt
```
When troubleshooting Frappe issues:
1. Check error logs first
2. Identify the root cause
3. Test in development first
4. Document the solution
5. Prevent recurrence
```

---

## 1. Sales & Accounting Issues

### Issue: Sales Invoice Not Submitting
```
Error: Cannot submit Sales Invoice - Items quantity not sufficient
```

**Solution:**
```python
# Check stock levels
from erpnext.stock.utils import get_stock_balance

item = "ITEM-001"
warehouse = "Main Warehouse - TC"
balance = get_stock_balance(item, warehouse)
print(f"Available: {balance}")

# Fix: Either:
# 1. Add stock to warehouse
# 2. Allow negative stock in settings
# 3. Update delivery note before invoicing
```

### Issue: Payment Entry Not Linking to Invoice
```
Error: Outstanding amount not matching
```

**Solution:**
```python
# 1. Reconcile manually
# Go to: Accounts > Payment Reconciliation

# 2. Or via code
from erpnext.accounts.doctype.payment_entry.payment_entry import get_reference_details

invoice = frappe.get_doc("Sales Invoice", "INV-2024-001")
payment = frappe.get_doc("Payment Entry", "PAY-2024-001")

# Match manually
payment.append("references", {
    "reference_doctype": "Sales Invoice",
    "reference_name": invoice.name,
    "allocated_amount": invoice.outstanding_amount
})
payment.save()
```

### Issue: GL Entries Not Created
```
Error: Account {0} does not exist in {1}
```

**Solution:**
```python
# 1. Check company default accounts
company = frappe.get_doc("Company", "Test Company")
print(company.default_bank_account)
print(company.default_cash_account)

# 2. Fix missing accounts
frappe.get_doc({
    "doctype": "Account",
    "account_name": "Cash",
    "company": "Test Company",
    "account_type": "Cash",
    "is_group": 0,
    "parent_account": "Cash and Bank - TC"
}).insert()

# 3. Update company defaults
company.default_cash_account = "Cash - TC"
company.save()
```

---

## 2. Stock & Inventory Issues

### Issue: Negative Stock
```
Error: Negative stock for Item {item_code}
```

**Solution:**
```python
# 1. Allow negative stock temporarily
frappe.db.set_value("Stock Settings", None, "allow_negative_stock", 1)

# 2. Or fix via stock reconciliation
from erpnext.stock.doctype.stock_reconciliation.stock_reconciliation import (
    EmptyStockError,
    StockRecreationError
)

recon = frappe.get_doc({
    "doctype": "Stock Reconciliation",
    "posting_date": "2024-01-01",
    "company": "Test Company",
    "items": [{
        "item_code": "ITEM-001",
        "warehouse": "Main Warehouse - TC",
        "qty": 100,
        "valuation_rate": 50
    }]
})
recon.insert()
recon.submit()
```

### Issue: Stock Balance Mismatch
```
Error: Stock balance mismatch
```

**Solution:**
```python
# Run stock reconciliation
# 1. Go to: Stock > Tools > Stock Reconciliation
# 2. Select items and warehouses
# 3. Click "Submit"

# Or via code
from erpnext.stock.doctype.stock_ledger_entry.stock_ledger_entry import (
    validate_serial_no,
    get_sle_by_voucher
)

# Find discrepancies
items = frappe.get_all("Item", filters={"is_stock_item": 1})
for item in items:
    actual = frappe.db.sql("""
        SELECT SUM(actual_qty) as qty
        FROM `tabStock Ledger Entry`
        WHERE item_code = %s
    """, item.name)[0][0] or 0
    
    bin_qty = frappe.db.sql("""
        SELECT SUM(actual_qty) as qty
        FROM `tabBin`
        WHERE item_code = %s
    """, item.name)[0][0] or 0
    
    if actual != bin_qty:
        print(f"Mismatch: {item.name} - Actual: {actual}, Bin: {bin_qty}")
```

### Issue: Serial Number Already Exists
```
Error: Serial No {0} already exists
```

**Solution:**
```python
# Find duplicate serial numbers
duplicates = frappe.db.sql("""
    SELECT serial_no, COUNT(*) as count
    FROM `tabSerial No`
    GROUP BY serial_no
    HAVING COUNT(*) > 1
""", as_dict=True)

for dup in duplicates:
    # Get all instances
    serial_nos = frappe.get_all("Serial No", 
        filters={"serial_no": dup.serial_no},
        order_by="creation"
    )
    
    # Keep first, unlink others
    for sn in serial_nos[1:]:
        frappe.db.set_value("Stock Ledger Entry", 
            {"serial_no": sn.name}, 
            "serial_no", ""
        )
        frappe.delete_doc("Serial No", sn.name)
```

---

## 3. User & Permission Issues

### Issue: User Cannot Access Document
```
Error: No permission for Sales Invoice
```

**Solution:**
```python
# 1. Check current permissions
frappe.has_permission("Sales Invoice", "read", doc=doc)

# 2. Check user roles
user = frappe.get_doc("User", "user@example.com")
for role in user.roles:
    print(role.role)

# 3. Add role via code
user.append("roles", {"role": "Accounts User"})
user.save()

# 4. Or add to DocType permissions
doc = frappe.get_doc("DocType", "Sales Invoice")
doc.append("permissions", {
    "role": "Custom Role",
    "read": 1,
    "write": 1,
    "create": 1
})
doc.save()
```

### Issue: Document Shared But Not Visible
```
Error: You don't have access to this document
```

**Solution:**
```python
# 1. Check shares
shares = frappe.get_all("DocShare", 
    filters={
        "share_name": "INV-2024-001",
        "share_doctype": "Sales Invoice"
    }
)
print(shares)

# 2. Remove bad shares
frappe.db.sql("""
    DELETE FROM `tabDocShare`
    WHERE share_name = %s AND share_doctype = %s
""", ("INV-2024-001", "Sales Invoice"))

# 3. Or share properly
from frappe.share import add_docshare
add_docshare(
    "Sales Invoice", 
    "INV-2024-001", 
    "user@example.com", 
    read=1, 
    write=1
)
```

---

## 4. Performance Issues

### Issue: Form Loading Very Slow
**Diagnosis:**
1. Too many custom fields
2. Heavy custom scripts
3. Too many child tables
4. Missing database indexes

**Solution:**
```python
# Check custom fields count
custom_fields = frappe.db.sql("""
    SELECT COUNT(*) 
    FROM `tabCustom Field` 
    WHERE dt = 'Sales Invoice'
""")[0][0]
print(f"Custom fields: {custom_fields}")

# Check child table rows
rows = frappe.db.sql("""
    SELECT name, COUNT(*) as items
    FROM `tabSales Invoice Item`
    GROUP BY name
    ORDER BY items DESC
    LIMIT 10
""", as_dict=True)
print(rows)

# Add index
frappe.db.sql("""
    CREATE INDEX idx_customer 
    ON `tabSales Invoice` (customer)
""")
```

### Issue: Report Taking Too Long
**Solution:**
```python
# 1. Add database indexes
frappe.db.sql("""
    CREATE INDEX idx_posting_date 
    ON `tabSales Invoice` (posting_date)
""")

frappe.db.sql("""
    CREATE INDEX idx_company_date 
    ON `tabSales Invoice` (company, posting_date)
""")

# 2. Optimize query
# Bad: SELECT * 
# Good: SELECT specific columns only

# 3. Use caching
import frappe

@frappe.whitelist()
def get_sales_summary():
    cache_key = "sales_summary_2024"
    data = frappe.cache().get_value(cache_key)
    
    if not data:
        # Calculate
        data = frappe.db.sql("""
            SELECT 
                company,
                SUM(grand_total) as total,
                COUNT(*) as count
            FROM `tabSales Invoice`
            WHERE docstatus = 1
            GROUP BY company
        """, as_dict=True)
        
        frappe.cache().set_value(cache_key, data, expires_in_sec=3600)
    
    return data
```

---

## 5. Integration Issues

### Issue: Webhook Not Firing
**Solution:**
```python
# 1. Check webhook logs
webhooks = frappe.get_all("Webhook", filters={"enabled": 1})
for wh in webhooks:
    print(f"Webhook: {wh.name}")
    logs = frappe.get_all("Webhook Log",
        filters={"webhook": wh.name},
        order_by="creation desc",
        limit=5
    )
    print(logs)

# 2. Manually trigger
from frappe.integrations.doctype.webhook.webhook import enqueue_webhook

doc = frappe.get_doc("Sales Invoice", "INV-2024-001")
enqueue_webhook(doc, "Sales Invoice")

# 3. Check webhook request
# Go to: Integrations > Webhook > Webhook Log
```

### Issue: API Returning 403
**Solution:**
```python
# 1. Check API key
# Go to: User > API Access

# 2. Generate new API key/secret
user = frappe.get_doc("User", "Administrator")
user.api_key = frappe.generate_hash(length=15)
user.api_secret = frappe.generate_hash(length=15)
user.save()

# 3. Use in requests
import requests

headers = {
    "Authorization": "token api_key:api_secret"
}
response = requests.get(
    "http://site.local/api/resource/Sales Invoice",
    headers=headers
)
```

---

## 6. Email Issues

### Issue: Emails Not Sending
**Solution:**
```python
# 1. Check Email Queue
queue = frappe.get_all("Email Queue",
    filters={"status": ["in", ["Not Sent", "Failed"]]},
    order_by="creation desc",
    limit=10
)
print(queue)

# 2. Check email account settings
email_account = frappe.get_doc("Email Account", "Default")
print(email_account.smtp_server)
print(email_account.smtp_port)

# 3. Send test email
from frappe.utils import sendmail
sendmail(
    recipients=["test@example.com"],
    subject="Test Email",
    message="Test body"
)

# 4. Check error in Email Queue
queue_doc = frappe.get_doc("Email Queue", queue[0].name)
print(queue_doc.error)
```

---

## 7. Database Issues

### Issue: Database Locked
```
Error: Database lock wait timeout
```

**Solution:**
```python
# 1. Check running processes
frappe.db.sql("SHOW PROCESSLIST")

# 2. Kill long-running queries (CAREFUL!)
# Only do this in development!

# 3. Use with deadlock timeout
frappe.db.sql("SET SESSION innodb_lock_wait_timeout = 50")

# 4. Or restart MariaDB
# sudo systemctl restart mariadb
```

### Issue: Large Database Size
**Solution:**
```python
# 1. Find large tables
tables = frappe.db.sql("""
    SELECT 
        table_name,
        ROUND(data_length / 1024 / 1024, 2) as MB
    FROM information_schema.tables
    WHERE table_schema = 'site1_local'
    ORDER BY data_length DESC
    LIMIT 20
""")
print(tables)

# 2. Archive old data
# Move old data to archive tables or JSON files

# 3. Clear logs
frappe.db.sql("DELETE FROM `tabError Log` WHERE creation < DATE_SUB(NOW(), INTERVAL 30 DAY)")
frappe.db.sql("DELETE FROM `tabEmail Queue` WHERE creation < DATE_SUB(NOW(), INTERVAL 7 DAY)")
frappe.db.commit()
```

---

## 8. Installation & Setup Issues

### Issue: Bench Command Not Found
**Solution:**
```bash
# Add to PATH
export PATH="$PATH:$HOME/frappe-bench/env/bin"

# Or reinstall
pip install frappe-bench
```

### Issue: Site Not Loading After Reboot
**Solution:**
```bash
# Check services
systemctl status supervisor
systemctl status nginx
systemctl status redis

# Restart services
sudo systemctl restart supervisor
sudo systemctl restart nginx
sudo systemctl restart redis

# Check ports
netstat -tlnp | grep 8000
```

---

## 9. Quick Fix Commands

| Problem | Command |
|---------|---------|
| Clear all cache | `bench --site site1.local clear-cache` |
| Rebuild permissions | `bench --site site1.local rebuild-permissions` |
| Reset sequence | `bench --site site1.local reset-permissions` |
| Check errors | `bench logs` |
| Database console | `bench --site site1.local mysql` |
| Force quit jobs | `bench --site site1.local python -c "from frappe.utils.background_jobs import remove_failed_jobs; remove_failed_jobs()"` |

---

## Related Topics
- [Error Handling & Debugging](./02_error-handling-debugging.md)
- [Common Errors](./01_common-errors.md)
- [Performance Optimization](../12_CACHING/02_performance-optimization.md)
