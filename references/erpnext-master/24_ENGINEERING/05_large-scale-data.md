# Large-Scale Data Handling Guide

## Quick Reference
Guide for handling millions of records, optimizing queries, and managing large databases in ERPNext.

## AI Prompt
```
When handling large-scale data:
1. Use pagination for large datasets
2. Index properly
3. Archive old data
4. Use batch processing
5. Monitor performance
```

---

## 1. Database Optimization

### Indexing Strategy
```sql
-- Create composite indexes for common queries
CREATE INDEX idx_si_company_docstatus 
ON `tabSales Invoice` (company, docstatus);

CREATE INDEX idx_si_customer_posting 
ON `tabSales Invoice` (customer, posting_date);

CREATE INDEX idx_si_posting_company 
ON `tabSales Invoice` (posting_date, company);

-- For text search
ALTER TABLE `tabItem` ADD FULLTEXT(item_name, description);

-- Partial index for active records
CREATE INDEX idx_active_items 
ON `tabItem` (name) WHERE is_stock_item = 1;
```

### Query Optimization
```python
# BAD: Load all records
all_invoices = frappe.get_all("Sales Invoice")

# GOOD: Filter and limit
invoices = frappe.get_all(
    "Sales Invoice",
    filters={"company": "Test Company", "docstatus": 1},
    fields=["name", "customer", "grand_total"],
    limit=100,
    order_by="posting_date desc"
)

# GOOD: Use pagination
def get_invoices_page(page, per_page=100):
    return frappe.get_all(
        "Sales Invoice",
        filters={"docstatus": 1},
        fields=["name", "customer", "grand_total"],
        limit=per_page,
        offset=page * per_page
    )
```

---

## 2. Batch Processing

### Processing Large Datasets
```python
from frappe.utils import chunkify

def process_large_dataset():
    """Process millions of records in batches"""
    
    # Get all records to process
    all_items = frappe.get_all("Item", pluck="name")
    
    # Process in chunks of 1000
    for chunk in chunkify(all_items, 1000):
        process_items_batch(chunk)
        
        # Commit periodically
        frappe.db.commit()
        
        # Log progress
        frappe.publish_realtime(
            "import_progress",
            {"processed": len(chunk), "total": len(all_items)}
        )

def process_items_batch(items):
    """Process a batch of items"""
    
    for item_name in items:
        item = frappe.get_doc("Item", item_name)
        
        # Do something with item
        update_item_pricing(item)
        
    return True
```

### Background Jobs for Heavy Processing
```python
from frappe.utils import enqueue
import time

def process_all_transactions():
    """Queue heavy transaction processing"""
    
    # Get all transactions to process
    transactions = frappe.get_all(
        "Sales Invoice",
        filters={"docstatus": 1, "processed": 0},
        pluck="name"
    )
    
    # Enqueue in batches
    batch_size = 1000
    for i in range(0, len(transactions), batch_size):
        batch = transactions[i:i + batch_size]
        
        enqueue(
            "my_app.utils.process_transaction_batch",
            transaction_names=batch,
            queue="long"
        )

def process_transaction_batch(transaction_names):
    """Process a batch of transactions"""
    
    for name in transaction_names:
        try:
            doc = frappe.get_doc("Sales Invoice", name)
            # Process...
            doc.processed = 1
            doc.save(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(f"Error processing {name}: {e}")
    
    frappe.db.commit()
```

---

## 3. Data Archiving

### Archive Strategy
```python
# my_app/utils/archiving.py

def archive_old_transactions():
    """Archive transactions older than 3 years"""
    
    cutoff_date = frappe.utils.add_years(
        frappe.utils.today(), -3
    )
    
    # Get old invoices
    old_invoices = frappe.get_all(
        "Sales Invoice",
        filters=[
            ["posting_date", "<", cutoff_date],
            ["docstatus", "=", 1]
        ],
        pluck="name"
    )
    
    # Archive each
    archived_count = 0
    for inv_name in old_invoices:
        try:
            # Create archive record
            create_archive_record("Sales Invoice", inv_name)
            
            # Cancel original
            doc = frappe.get_doc("Sales Invoice", inv_name)
            doc.cancel()
            
            archived_count += 1
            
            if archived_count % 100 == 0:
                frappe.publish_realtime(
                    "archiving_progress",
                    {"archived": archived_count, "total": len(old_invoices)}
                )
                
        except Exception as e:
            frappe.log_error(f"Error archiving {inv_name}: {e}")
    
    frappe.db.commit()
    return archived_count

def create_archive_record(doctype, docname):
    """Create archive copy of document"""
    
    original = frappe.get_doc(doctype, docname)
    
    archive = frappe.get_doc({
        "doctype": f"{doctype} Archive",
        "original_name": original.name,
        "data": frappe.as_json(original.as_dict()),
        "archived_on": frappe.utils.now()
    })
    archive.insert()
    
    return archive
```

### Archive Configuration
```python
# In hooks.py
scheduler_events = {
    "monthly": [
        "my_app.utils.archiving.archive_old_transactions"
    ]
}

# Archive settings
ARCHIVE_CONFIG = {
    "Sales Invoice": {"age_years": 3, "archive_doctype": "Sales Invoice Archive"},
    "Purchase Invoice": {"age_years": 3, "archive_doctype": "Purchase Invoice Archive"},
    "Delivery Note": {"age_years": 2, "archive_doctype": "Delivery Note Archive"},
    "Purchase Receipt": {"age_years": 2, "archive_doctype": "Purchase Receipt Archive"}
}
```

---

## 4. Pagination Techniques

### Cursor-Based Pagination
```python
def get_transactions_cursor(last_name=None, limit=100):
    """Efficient cursor-based pagination"""
    
    filters = {"docstatus": 1}
    if last_name:
        filters["name"] = [">", last_name]
    
    transactions = frappe.get_all(
        "Sales Invoice",
        filters=filters,
        fields=["name", "customer", "posting_date", "grand_total"],
        order_by="name asc",
        limit=limit
    )
    
    has_more = len(transactions) == limit
    
    return {
        "transactions": transactions,
        "next_cursor": transactions[-1]["name"] if has_more else None,
        "has_more": has_more
    }
```

### Offset Pagination with Total Count
```python
def get_paginated_data(page=1, per_page=50, filters=None):
    """Get paginated data with total count"""
    
    # Get total count
    total = frappe.db.count("Sales Invoice", filters or {})
    
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Get data
    data = frappe.get_all(
        "Sales Invoice",
        filters=filters or {},
        fields=["name", "customer", "grand_total", "posting_date"],
        order_by="posting_date desc",
        limit=per_page,
        offset=offset
    )
    
    return {
        "data": data,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }
```

---

## 5. Report Optimization

### Using Summary Tables
```python
# Create summary table for fast reporting
def create_summary_table():
    """Create and populate summary table"""
    
    # Create table
    frappe.db.sql("""
        CREATE TABLE IF NOT EXISTS `tabSales Summary By Month` (
            name VARCHAR(255) PRIMARY KEY,
            company VARCHAR(255),
            month VARCHAR(7),
            total_sales DECIMAL(18, 2),
            total_count INT,
            updated_at DATETIME
        )
    """)
    
    # Populate from actual data
    frappe.db.sql("""
        INSERT INTO `tabSales Summary By Month` 
        (name, company, month, total_sales, total_count, updated_at)
        SELECT 
            CONCAT(company, '-', DATE_FORMAT(posting_date, '%Y-%m')),
            company,
            DATE_FORMAT(posting_date, '%Y-%m'),
            SUM(grand_total),
            COUNT(*),
            NOW()
        FROM `tabSales Invoice`
        WHERE docstatus = 1
        GROUP BY company, DATE_FORMAT(posting_date, '%Y-%m')
        ON DUPLICATE KEY UPDATE
            total_sales = VALUES(total_sales),
            total_count = VALUES(total_count),
            updated_at = NOW()
    """)
    
    frappe.db.commit()
```

### Cached Reports
```python
import frappe
from datetime import datetime, timedelta

def get_cached_sales_report(company, from_date, to_date):
    """Get report with caching"""
    
    cache_key = f"sales_report_{company}_{from_date}_{to_date}"
    
    # Try cache first
    cached = frappe.cache().get_value(cache_key)
    if cached:
        return cached
    
    # Generate report
    report = generate_sales_report(company, from_date, to_date)
    
    # Cache for 1 hour
    frappe.cache().set_value(cache_key, report, expires_in_sec=3600)
    
    return report

def invalidate_report_cache(company):
    """Invalidate cache when data changes"""
    
    # Delete all matching cache keys
    frappe.cache().delete_pattern(f"sales_report_{company}_*")
```

---

## 6. Import/Export Optimization

### Fast Bulk Import
```python
import frappe
from frappe.utils import chunkify

def bulk_import_items(csv_data):
    """Fast bulk import using direct SQL"""
    
    items_to_insert = []
    
    for row in csv_data:
        items_to_insert.append({
            "name": row["item_code"],
            "item_name": row["item_name"],
            "item_group": row.get("item_group", "All Item Groups"),
            "stock_uom": row.get("uom", "Nos"),
            "is_stock_item": 1,
            "creation": frappe.utils.now(),
            "modified": frappe.utils.now(),
            "owner": "Administrator",
            "modified_by": "Administrator"
        })
    
    # Insert in batches
    batch_size = 500
    for batch in chunkify(items_to_insert, batch_size):
        for item in batch:
            try:
                frappe.db.sql("""
                    INSERT IGNORE INTO `tabItem` 
                    (name, item_name, item_group, stock_uom, is_stock_item, 
                     creation, modified, owner, modified_by)
                    VALUES 
                    (%(name)s, %(item_name)s, %(item_group)s, %(stock_uom)s, 
                     %(is_stock_item)s, %(creation)s, %(modified)s, %(owner)s, %(modified_by)s)
                """, item)
            except Exception as e:
                frappe.log_error(f"Error inserting {item['name']}: {e}")
        
        frappe.db.commit()
        frappe.publish_realtime("import_progress", {"done": len(batch)})
```

---

## 7. Performance Monitoring

### Query Monitoring
```python
import frappe
import time

class QueryMonitor:
    def __init__(self, threshold_ms=100):
        self.threshold_ms = threshold_ms
        self.queries = []
    
    def __enter__(self):
        frappe.flags.queries = []
        return self
    
    def __exit__(self, *args):
        slow_queries = []
        for q in frappe.flags.get('queries', []):
            duration = q.get('duration', 0)
            if duration > self.threshold_ms:
                slow_queries.append({
                    'query': q.get('query', ''),
                    'duration': duration
                })
        
        if slow_queries:
            frappe.log_error(
                f"Slow queries detected: {len(slow_queries)}",
                "Query Performance"
            )

# Usage
with QueryMonitor(threshold_ms=200):
    # Run your slow code
    result = get_large_report()
```

### Database Health Check
```python
def check_database_health():
    """Check database for performance issues"""
    
    issues = []
    
    # Check table sizes
    large_tables = frappe.db.sql("""
        SELECT 
            table_name,
            ROUND(data_length / 1024 / 1024, 2) as size_mb
        FROM information_schema.tables
        WHERE table_schema = DATABASE()
        ORDER BY data_length DESC
        LIMIT 10
    """, as_dict=True)
    
    for table in large_tables:
        if table.size_mb > 1000:  # > 1GB
            issues.append(f"Large table: {table.table_name} ({table.size_mb} MB)")
    
    # Check for missing indexes
    tables_to_check = ["Sales Invoice", "Purchase Invoice", "GL Entry"]
    for table in tables_to_check:
        indexes = frappe.db.sql(f"SHOW INDEX FROM `tab{table}`")
        if len(indexes) < 3:
            issues.append(f"Table {table} may need indexes")
    
    return issues
```

---

## 8. Data Retention Policies

### Automated Retention
```python
RETENTION_POLICIES = {
    "Error Log": {"keep_days": 90, "archive": True},
    "Email Queue": {"keep_days": 30, "archive": False},
    "Transaction Logs": {"keep_days": 365, "archive": True},
    "Audit Trail": {"keep_days": 2555, "archive": True},  # 7 years for compliance
    "Old Invoices": {"keep_days": 1095, "archive": True}  # 3 years
}

def apply_retention_policies():
    """Apply data retention policies"""
    
    for doctype, config in RETENTION_POLICIES.items():
        cutoff = frappe.utils.add_days(
            frappe.utils.today(), 
            -config["keep_days"]
        )
        
        # Get old records
        old_records = frappe.get_all(
            doctype,
            filters={"creation": ["<", cutoff]},
            pluck="name"
        )
        
        if config["archive"]:
            # Archive before deleting
            for record in old_records:
                create_archive_record(doctype, record)
        
        # Delete old records
        frappe.db.sql(f"""
            DELETE FROM `tab{doctype}`
            WHERE creation < %s
        """, cutoff)
        
        frappe.db.commit()
        
        frappe.log_error(
            f"Retention: Deleted {len(old_records)} {doctype} records",
            "Retention Policy"
        )
```

---

## Related Topics
- [Performance Optimization](../frappe-framework-master/12_CACHING/02_performance-optimization.md)
- [Migration & Upgrade](../25_ELITE_SKILLS/06_upgrade-guide.md)
- [Complex Multi-Company](./03_complex-multi-company.md)
