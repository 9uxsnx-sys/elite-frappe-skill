# Stock Entry

## Quick Reference
Stock Entry handles all inventory movements: Material Receipt (inward), Material Issue (outward), Material Transfer (between warehouses), Manufacturing (production). Creates Stock Ledger Entry and optionally GL Entry.

## AI Prompt
\`\`\`
When working with Stock Entry:
1. Validate item exists and is stockable
2. Check warehouse availability for issues
3. Understand stock valuation (FIFO/Moving Average)
4. Know which entries create GL Entry
5. Use correct purpose type
\`\`\`

---

## Stock Entry DocType

### Key Fields
| Field | Type | Description |
|-------|------|-------------|
| stock_entry_type | Select | Entry purpose |
| company | Link | Company |
| posting_date | Date | Transaction date |
| items | Table | Stock items |
| from_warehouse | Link | Source warehouse |
| to_warehouse | Link | Destination warehouse |

### Stock Entry Types (Purpose)
| Purpose | Description | GL Entry |
|---------|-------------|----------|
| Material Receipt | Items inward | Yes |
| Material Issue | Items outward | Yes |
| Material Transfer | Between warehouses | No |
| Material Transfer for Manufacture | To production | No |
| Manufacture | Finished goods | Yes |
| Repack | Change packaging | Yes |

---

## Creating Stock Entry

### Material Receipt
\`\`\`python
se = frappe.get_doc({
    "doctype": "Stock Entry",
    "stock_entry_type": "Material Receipt",
    "company": "My Company Ltd",
    "posting_date": "2024-01-15",
    "items": [{
        "item_code": "LAPTOP-001",
        "qty": 10,
        "t_warehouse": "Stores - MC",
        "basic_rate": 35000
    }]
})
se.insert()
se.submit()
\`\`\`

### Material Issue
\`\`\`python
se = frappe.get_doc({
    "doctype": "Stock Entry",
    "stock_entry_type": "Material Issue",
    "company": "My Company Ltd",
    "items": [{
        "item_code": "LAPTOP-001",
        "qty": 2,
        "s_warehouse": "Stores - MC"
    }]
})
se.insert()
se.submit()
\`\`\`

### Material Transfer
\`\`\`python
se = frappe.get_doc({
    "doctype": "Stock Entry",
    "stock_entry_type": "Material Transfer",
    "company": "My Company Ltd",
    "items": [{
        "item_code": "LAPTOP-001",
        "qty": 5,
        "s_warehouse": "Stores - MC",
        "t_warehouse": "Finished Goods - MC"
    }]
})
se.insert()
se.submit()
\`\`\`

### Manufacture
\`\`\`python
se = frappe.get_doc({
    "doctype": "Stock Entry",
    "stock_entry_type": "Manufacture",
    "company": "My Company Ltd",
    "work_order": "WO-001",
    "items": [
        # Raw materials (source)
        {
            "item_code": "RAW-001",
            "qty": 5,
            "s_warehouse": "Raw Materials - MC",
            "basic_rate": 100
        },
        # Finished good (target)
        {
            "item_code": "FIN-001",
            "qty": 1,
            "t_warehouse": "Finished Goods - MC",
            "basic_rate": 500
        }
    ]
})
se.insert()
se.submit()
\`\`\`

---

## Stock Ledger Entry

### On Submit
\`\`\`python
# Each Stock Entry item creates Stock Ledger Entry

# Material Receipt creates:
{
    "doctype": "Stock Ledger Entry",
    "item_code": "LAPTOP-001",
    "warehouse": "Stores - MC",
    "actual_qty": 10,  # Positive for receipt
    "valuation_rate": 35000,
    "stock_value": 350000,
    "voucher_type": "Stock Entry",
    "voucher_no": "SE-001"
}

# Material Issue creates:
{
    "actual_qty": -2,  # Negative for issue
    "valuation_rate": 35000,
    "stock_value": -70000
}
\`\`\`

### Get Stock Balance
\`\`\`python
from erpnext.stock.utils import get_stock_balance

# Current balance
balance = get_stock_balance("LAPTOP-001", "Stores - MC")

# Balance at date
balance = get_stock_balance("LAPTOP-001", "Stores - MC", "2024-01-31")

# Balance with posting time
balance = get_stock_balance(
    "LAPTOP-001", 
    "Stores - MC", 
    "2024-01-31 18:00:00"
)
\`\`\`

---

## Stock Valuation

### FIFO (First In First Out)
\`\`\`
Receipt 1: 10 units @ ₹100 = ₹1,000
Receipt 2: 5 units @ ₹120 = ₹600
Issue 1: 8 units = 8 × ₹100 = ₹800 (from Receipt 1)
Issue 2: 5 units = 2 × ₹100 + 3 × ₹120 = ₹560 (rest from Receipt 1 + Receipt 2)
\`\`\`

### Moving Average
\`\`\`
Receipt 1: 10 units @ ₹100 = ₹1,000 → Avg: ₹100
Receipt 2: 5 units @ ₹120 = ₹600 → Total: 15 units, ₹1,600 → Avg: ₹106.67
Issue 1: 8 units @ ₹106.67 = ₹853.36
\`\`\`

### Setting Valuation Method
\`\`\`python
# In Item DocType
item = frappe.get_doc("Item", "LAPTOP-001")
item.valuation_method = "FIFO"  # or "Moving Average"
item.save()
\`\`\`

---

## GL Entry for Stock

### Material Receipt
\`\`\`
GL Entries:
┌─────────────────────┬────────┬────────┐
│ Account             │ Debit  │ Credit │
├─────────────────────┼────────┼────────┤
│ Stock Assets - MC   │ 3,50,000│       │
│ Stock Received - MC │        │ 3,50,000│
└─────────────────────┴────────┴────────┘
\`\`\`

### Material Issue
\`\`\`
GL Entries:
┌──────────────────────┬────────┬────────┐
│ Account              │ Debit  │ Credit │
├──────────────────────┼────────┼────────┤
│ COGS - MC            │ 70,000 │        │
│ Stock Assets - MC    │        │ 70,000 │
└──────────────────────┴────────┴────────┘
\`\`\`

---

## Stock Entry API

### Get Stock Value
\`\`\`python
from erpnext.stock.utils import get_stock_value_on

value = get_stock_value_on("Stores - MC", "2024-01-31")
\`\`\`

### Get Stock Projection
\`\`\`python
from erpnext.stock.utils import get_stock_forecast

forecast = get_stock_forecast(
    item_code="LAPTOP-001",
    warehouse="Stores - MC"
)
\`\`\`

### Check Availability
\`\`\`python
def check_availability(item_code, warehouse, required_qty):
    current = get_stock_balance(item_code, warehouse)
    if current < required_qty:
        frappe.throw(
            f"Insufficient stock. Available: {current}, Required: {required_qty}"
        )
    return True
\`\`\`

---

## Serial No & Batch

### With Serial No
\`\`\`python
se = frappe.get_doc({
    "doctype": "Stock Entry",
    "stock_entry_type": "Material Receipt",
    "items": [{
        "item_code": "LAPTOP-001",
        "qty": 2,
        "t_warehouse": "Stores - MC",
        "serial_no": "SN001\nSN002",
        "basic_rate": 35000
    }]
})
\`\`\`

### With Batch
\`\`\`python
se = frappe.get_doc({
    "doctype": "Stock Entry",
    "stock_entry_type": "Material Receipt",
    "items": [{
        "item_code": "MEDICINE-001",
        "qty": 100,
        "t_warehouse": "Stores - MC",
        "batch_no": "BATCH-2024-001",
        "basic_rate": 50
    }]
})
\`\`\`

---

## Common Patterns

### Auto Stock Entry on Event
\`\`\`python
# In hooks.py
doc_events = {
    "Sales Order": {
        "on_submit": "custom_app.stock.auto_issue_stock"
    }
}

# In custom_app/stock.py
def auto_issue_stock(doc, method):
    for item in doc.items:
        if item.delivered_qty == 0:
            se = frappe.get_doc({
                "doctype": "Stock Entry",
                "stock_entry_type": "Material Issue",
                "items": [{
                    "item_code": item.item_code,
                    "qty": item.qty,
                    "s_warehouse": item.warehouse
                }]
            })
            se.insert()
            se.submit()
\`\`\`

### Stock Reconciliation
\`\`\`python
# For bulk stock adjustment
sr = frappe.get_doc({
    "doctype": "Stock Reconciliation",
    "purpose": "Stock Reconciliation",
    "items": [{
        "item_code": "LAPTOP-001",
        "warehouse": "Stores - MC",
        "qty": 50,
        "valuation_rate": 35000
    }]
})
sr.insert()
sr.submit()
\`\`\`

---

## Related Topics
- [Warehouse](./01_warehouse.md)
- [Stock Ledger](./03_stock-ledger.md)
- [Serial No Batch](./04_serial-no-batch.md)
