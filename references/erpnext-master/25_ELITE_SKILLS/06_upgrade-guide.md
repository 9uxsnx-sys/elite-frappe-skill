# Migration & Upgrade Guide

## Quick Reference
Complete guide for migrating to ERPNext/Frappe and upgrading between versions.

## AI Prompt
```
When handling migrations:
1. Always backup first
2. Test in staging first
3. Check app compatibility
4. Run migrations in order
5. Verify after each step
```

---

## 1. Pre-Migration Checklist

### Backup Everything
```bash
# Backup database
bench --site site1.local backup

# Backup files
tar -czvf files_backup.tar.gz ~/frappe-bench/sites/site1.local/private/files/

# Backup custom apps
cp -r ~/frappe-bench/apps/my_app ~/my_app_backup/
```

### Check Compatibility
```bash
# Check Frappe version
bench version

# Check ERPNext version
bench get-app erpnext

# List installed apps and versions
bench apps

# Check Python version
python --version
```

---

## 2. Frappe/ERPNext Upgrade

### Standard Upgrade Process
```bash
# Step 1: Get latest version
cd ~/frappe-bench

# Step 2: Pull latest code
bench update --pull

# Step 3: Update pip dependencies
pip install -q -e git+https://github.com/frappe/frappe.git#egg=frappe

# Step 4: Run migration for all sites
bench --all migrate

# Step 5: Rebuild assets
bench build

# Step 6: Clear cache
bench --all clear-cache
```

### Upgrade to Specific Version
```bash
# Switch to specific branch
cd ~/frappe-bench/apps/frappe
git fetch origin
git checkout version-15

cd ~/frappe-bench/apps/erpnext
git fetch origin
git checkout version-15

# Update and migrate
bench update --patch
bench --all migrate
bench build
```

---

## 3. Data Migration from Other Systems

### From Excel/CSV
```python
import frappe
import csv

def migrate_from_csv(file_path, doctype):
    """Import data from CSV file"""
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            doc = frappe.get_doc({
                "doctype": doctype,
                **{k: v for k, v in row.items() if v}
            })
            try:
                doc.insert()
                print(f"Created: {doc.name}")
            except Exception as e:
                print(f"Error creating {row}: {e}")
    
    frappe.db.commit()

# Usage
migrate_from_csv('/path/to/customers.csv', 'Customer')
```

### From QuickBooks
```python
# Step 1: Export from QuickBooks
# Step 2: Map fields
# Step 3: Import using CSV or API

field_mapping = {
    'CompanyName': 'customer_name',
    'Email': 'email_id',
    'Phone': 'phone',
    'Address': 'address_line1',
    'City': 'city',
    'Balance': 'opening_balance'
}

def migrate_quickbooks_customers(qb_data):
    for customer in qb_data:
        doc = frappe.get_doc({
            "doctype": "Customer",
            **{field_mapping[k]: v for k, v in customer.items() if k in field_mapping},
            "customer_type": "Company",
            "customer_group": "All Customer Groups",
            "territory": "All Territories"
        })
        doc.insert()
```

### From SAP/Oracle
```python
# Complex migration requires careful planning:
# 1. Map all tables
# 2. Migrate master data first (Items, Customers, Suppliers)
# 3. Then transactions (Invoices, Orders)
# 4. Finally opening balances

def migrate_opening_balances():
    """Migrate opening balances from legacy system"""
    
    # GL Opening
    for account, balance in gl_balances.items():
        je = frappe.get_doc({
            "doctype": "Journal Entry",
            "title": f"Opening Balance - {account}",
            "posting_date": "2024-01-01",
            "accounts": [{
                "account": account,
                "debit_in_account_currency": balance if balance > 0 else 0,
                "credit_in_account_currency": abs(balance) if balance < 0 else 0
            }, {
                "account": "Opening Balance Account - TC",
                "debit_in_account_currency": abs(balance) if balance < 0 else 0,
                "credit_in_account_currency": balance if balance > 0 else 0
            }]
        })
        je.insert()
        je.submit()
```

---

## 4. Site Migration (Moving to New Server)

### Export Site
```bash
# On old server
cd ~/frappe-bench

# Create backup with files
bench --site site1.local backup --with-files

# Backup location
# ~/frappe-bench/sites/site1.local/private/backups/
```

### Import Site
```bash
# On new server

# Install Frappe and bench (same version)
pip install frappe erpnext

# Initialize bench
cd ~
mkdir frappe-bench
cd frappe-bench
bench init frappe-bench --frappe-branch version-14

# Create new site
bench new-site site1.local

# Restore backup
bench --site site1.local restore-path /path/to/database.sql

# Restore files
cp -r /path/to/site1.local/private/files/* ~/frappe-bench/sites/site1.local/private/files/

# Install apps
bench install-app erpnext
bench install-app your_custom_app
```

---

## 5. Version-Specific Migrations

### v14 to v15 Migration
```python
# my_app/patches/v15_migration.py

def execute():
    # 1. Handle removed features
    # Some fields might be removed in v15
    
    # 2. Update custom fields
    frappe.reload_doctype("Sales Invoice")
    
    # 3. Migrate data to new format
    frappe.db.sql("""
        UPDATE `tabSales Invoice`
        SET workflow_state = status
        WHERE workflow_state IS NULL
    """)
    
    # 4. Clean up
    frappe.db.commit()
```

### Common Migration Tasks
```python
def execute():
    # Fix corrupted data
    frappe.db.sql("""
        UPDATE `tabItem`
        SET stock_uom = 'Nos'
        WHERE stock_uom IS NULL OR stock_uom = ''
    """)
    
    # Add missing fields
    frappe.reload_doctype("Customer")
    
    # Migrate custom fields
    frappe.db.sql("""
        UPDATE `tabCustom Field`
        SET dt = 'Sales Invoice'
        WHERE dt = 'SalesInvoice'
    """)
    
    frappe.db.commit()
```

---

## 6. App Migration

### Updating Custom Apps
```bash
# Update app code
cd ~/frappe-bench/apps/my_app
git pull origin master

# Check for breaking changes
git log --oneline --all

# Run app-specific patches
bench --site site1.local migrate

# If needed, run custom migrations
bench --site site1.local execute my_app.patches.migrate_data
```

### Handling Breaking Changes
```python
# In your app's hooks.py
app_version = "2.0.0"

def migrate_from_v1():
    """One-time migration from v1"""
    if frappe.db.get_value("DocType", "My Old DocType"):
        # Migrate data
        pass
    
    # Remove old DocTypes
    frappe.delete_doc("DocType", "My Old DocType")

# In patches.txt
my_app.patches.v2_migration.migrate_from_v1
```

---

## 7. Post-Migration Checklist

### Verify Data Integrity
```python
# Run verification checks
def verify_migration():
    checks = {
        "Customers": frappe.db.count("Customer"),
        "Suppliers": frappe.db.count("Supplier"),
        "Items": frappe.db.count("Item"),
        "Invoices": frappe.db.count("Sales Invoice"),
    }
    
    for doctype, count in checks.items():
        print(f"{doctype}: {count}")
    
    # Verify balances
    from erpnext.accounts.utils import get_balance_on
    accounts = frappe.get_all("Account", filters={"is_group": 0})
    for acc in accounts[:10]:
        balance = get_balance_on(acc.name)
        if balance:
            print(f"{acc.name}: {balance}")
```

### Test Critical Flows
```bash
# Test sales flow
# 1. Create Quotation
# 2. Convert to Sales Order
# 3. Deliver
# 4. Invoice
# 5. Receive Payment

# Test purchase flow
# 1. Create Purchase Order
# 2. Receive
# 3. Invoice
# 4. Make Payment
```

---

## 8. Troubleshooting Migration Issues

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Migration fails | Check `bench migrate` output, fix errors first |
| Missing fields | Run `frappe.reload_doctype()` |
| Permission errors | Run `bench --site site1.local rebuild-permissions` |
| Missing documents | Restore from backup |
| Broken links | Run data integrity check |

### Rollback Procedure
```bash
# If migration fails completely
bench --site site1.local restore-path /path/to/backup_database.sql

# Reinstall apps
bench --site site1.local install-app erpnext

# Clear cache
bench --site site1.local clear-cache
```

---

## Related Topics
- [Implementation Checklist](./01_implementation-checklist.md)
- [Gap Analysis](./03_gap-analysis.md)
- [Error Handling & Debugging](../frappe-framework-master/22_DEBUGGING/02_error-handling-debugging.md)
