# ERPNext Common Errors

## Quick Reference
Most errors stem from: missing master data, permission issues, date/fiscal year problems, or ledger mismatches. Always check error logs and use bench console for debugging.

## AI Prompt
\`\`\`
When encountering errors:
1. Check error log: Error Log doctype
2. Verify master data exists (customer, item, account)
3. Check permissions for user/role
4. Validate fiscal year and posting date
5. Trace ledger entries for mismatches
\`\`\`

---

## Error Categories

### 1. Master Data Errors

#### "Customer [XXX] not found"
\`\`\`python
# Solution: Create customer or check name
if not frappe.db.exists("Customer", "XXX"):
    customer = frappe.get_doc({
        "doctype": "Customer",
        "customer_name": "XXX",
        "customer_group": "All Customer Groups",
        "territory": "All Territories"
    })
    customer.insert()
\`\`\`

#### "Item [XXX] not found"
\`\`\`python
# Solution: Check item code or create item
if not frappe.db.exists("Item", "XXX"):
    # Check if item was renamed
    old_name = frappe.db.get_value("Item", {"item_name": "XXX"}, "name")
\`\`\`

#### "Account [XXX] not found"
\`\`\`python
# Solution: Check account with company abbreviation
account_name = "Sales - MC"  # Include abbreviation
if not frappe.db.exists("Account", account_name):
    # Create account
\`\`\`

### 2. Stock Errors

#### "Stock not available for item [XXX]"
\`\`\`python
# Solution: Check stock balance
from erpnext.stock.utils import get_stock_balance
balance = get_stock_balance("XXX", "Stores - MC")

# Allow negative stock (not recommended for production)
frappe.db.set_value("Stock Settings", None, "allow_negative_stock", 1)
\`\`\`

#### "Negative stock error"
\`\`\`python
# Solution: Check ledger entries
entries = frappe.get_all("Stock Ledger Entry",
    filters={"item_code": "XXX", "warehouse": "Stores - MC"},
    fields=["actual_qty", "posting_date", "voucher_no"],
    order_by="posting_date, creation"
)

# Reconcile stock
from erpnext.stock.doctype.stock_reconciliation.stock_reconciliation import StockReconciliation
\`\`\`

#### "Serial No [XXX] not found"
\`\`\`python
# Solution: Check serial no exists and not in another warehouse
serial = frappe.db.get_value("Serial No", "XXX", ["warehouse", "status"], as_dict=True)
\`\`\`

### 3. Accounting Errors

#### "GL Entry not balancing"
\`\`\`python
# Solution: Check debit = credit
gl_entries = frappe.get_all("GL Entry",
    filters={"voucher_no": "SI-001"},
    fields=["account", "debit", "credit"]
)
total_debit = sum(e.debit for e in gl_entries)
total_credit = sum(e.credit for e in gl_entries)
difference = total_debit - total_credit
\`\`\`

#### "Fiscal Year [XXX] does not exist"
\`\`\`python
# Solution: Create fiscal year
fy = frappe.get_doc({
    "doctype": "Fiscal Year",
    "year": "2024",
    "year_start_date": "2024-01-01",
    "year_end_date": "2024-12-31"
})
fy.insert()
\`\`\`

#### "Posting date not in valid fiscal year"
\`\`\`python
# Solution: Check fiscal year covers the date
from erpnext.accounts.utils import get_fiscal_year
try:
    fy = get_fiscal_year("2024-06-15", company="My Company Ltd")
except:
    # Create or extend fiscal year
\`\`\`

### 4. Permission Errors

#### "Not permitted for [DocType]"
\`\`\`python
# Solution: Add role to user
user = frappe.get_doc("User", "user@example.com")
user.append("roles", {"role": "Sales User"})
user.save()

# Or check current permissions
has_perm = frappe.has_permission("Sales Invoice", "write")
\`\`\`

#### "No permission to set [field]"
\`\`\`python
# Solution: Check perm level on field
# Go to DocType → Field → Perm Level
# Ensure user's role has permission at that level
\`\`\`

### 5. Validation Errors

#### "Credit limit exceeded for Customer [XXX]"
\`\`\`python
# Solution: Check and adjust credit limit
customer = frappe.get_doc("Customer", "XXX")
customer.credit_limit = 500000
customer.save()

# Or bypass (not recommended)
frappe.db.set_value("Customer", "XXX", "bypass_credit_limit_check", 1)
\`\`\`

#### "Item cannot be sold"
\`\`\`python
# Solution: Check is_sales_item
item = frappe.get_doc("Item", "XXX")
item.is_sales_item = 1
item.save()
\`\`\`

---

## Debugging Techniques

### 1. Check Error Log
\`\`\`python
# Via Desk
# Tools > Error Log

# Via Python
errors = frappe.get_all("Error Log",
    filters={"seen": 0},
    fields=["name", "error", "creation"],
    order_by="creation desc",
    limit=10
)
\`\`\`

### 2. Use Console
\`\`\`bash
bench --site [site] console

# In console
>>> import frappe
>>> frappe.db.get_value("Customer", "ABC Corp", "credit_limit")
>>> 100000
\`\`\`

### 3. Enable Debug Mode
\`\`\`python
# In site_config.json
{
    "developer_mode": 1
}

# Or via bench
bench --site [site] set-config developer_mode 1
\`\`\`

### 4. Add Print Statements
\`\`\`python
# In controller
def validate(self):
    print(f"Debug: Customer = {self.customer}")
    print(f"Debug: Items = {len(self.items)}")
    frappe.log_error(f"Debug: {self.as_dict()}", "Custom Debug")
\`\`\`

### 5. Trace SQL Queries
\`\`\`python
# Enable query logging
frappe.db.sql_debug = True

# Run query
frappe.db.sql("SELECT * FROM tabCustomer LIMIT 1")

# Check logs in bench-start.log
\`\`\`

---

## Error Resolution Checklist

\`\`\`
[ ] Check Error Log doctype
[ ] Verify master data exists
[ ] Check user permissions
[ ] Validate fiscal year and dates
[ ] Check company/warehouse/account mappings
[ ] Review ledger entries for consistency
[ ] Check for duplicate entries
[ ] Verify naming series
[ ] Check hooks.py for conflicting overrides
\`\`\`

---

## Common Database Queries

### Find Orphan Records
\`\`\`sql
-- GL Entry without voucher
SELECT * FROM `tabGL Entry` 
WHERE voucher_no NOT IN (
    SELECT name FROM `tabSales Invoice`
    UNION
    SELECT name FROM `tabPurchase Invoice`
    UNION
    SELECT name FROM `tabJournal Entry`
);
\`\`\`

### Stock Ledger Mismatch
\`\`\`sql
-- Check stock ledger vs actual balance
SELECT item_code, warehouse, SUM(actual_qty) as balance
FROM `tabStock Ledger Entry`
GROUP BY item_code, warehouse
HAVING balance < 0;
\`\`\`

### Duplicate GL Entries
\`\`\`sql
-- Find duplicate GL entries
SELECT voucher_no, COUNT(*)
FROM `tabGL Entry`
WHERE docstatus = 1
GROUP BY voucher_no
HAVING COUNT(*) > 20;
\`\`\`

---

## Related Topics
- [Debugging Techniques](./02_debugging-techniques.md)
- [Troubleshooting Guide](./05_troubleshooting-guide.md)
