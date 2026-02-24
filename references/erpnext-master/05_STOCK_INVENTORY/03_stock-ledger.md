# Stock Ledger Entry

## Quick Reference
Stock Ledger Entry (SLE) is the atomic record of every stock movement. Contains item, warehouse, qty, rate, value. Created automatically on stock transactions.

## AI Prompt
```
When debugging stock issues:
1. Query SLE for item/warehouse
2. Check actual_qty (positive=receipt, negative=issue)
3. Verify valuation_rate consistency
4. Trace voucher_no to source document
5. Check for duplicate or missing entries
```

---

## Stock Ledger Entry DocType

### Key Fields
| Field | Type | Description |
|-------|------|-------------|
| item_code | Link | Item reference |
| warehouse | Link | Warehouse |
| posting_date | Date | Transaction date |
| actual_qty | Float | Quantity (+/-) |
| valuation_rate | Currency | Rate per unit |
| stock_value | Currency | Total value |
| voucher_type | Link | Source DocType |
| voucher_no | Data | Source document |

---

## Querying SLE

### Get Stock Balance
```python
from erpnext.stock.utils import get_stock_balance

balance = get_stock_balance("ITEM-001", "Stores - MC")
```

### Get Stock History
```python
entries = frappe.get_all("Stock Ledger Entry",
    filters={"item_code": "ITEM-001", "warehouse": "Stores - MC"},
    fields=["posting_date", "actual_qty", "valuation_rate", "voucher_no"],
    order_by="posting_date, creation"
)
```

### Get Stock Value
```python
from erpnext.stock.utils import get_stock_value_on

value = get_stock_value_on("Stores - MC", "2024-01-31")
```

---

## Creating SLE

### Via Stock Entry (Automatic)
```python
se = frappe.get_doc({
    "doctype": "Stock Entry",
    "stock_entry_type": "Material Receipt",
    "items": [{
        "item_code": "ITEM-001",
        "qty": 10,
        "t_warehouse": "Stores - MC",
        "basic_rate": 100
    }]
})
se.insert()
se.submit()  # Creates SLE automatically
```

### Programmatic SLE
```python
from erpnext.stock.stock_ledger import make_sl_entries

sl_entries = [{
    "item_code": "ITEM-001",
    "warehouse": "Stores - MC",
    "actual_qty": 10,
    "valuation_rate": 100,
    "voucher_type": "Stock Entry",
    "voucher_no": "SE-001",
    "posting_date": "2024-01-15",
    "company": "My Company Ltd"
}]

make_sl_entries(sl_entries)
```

---

## Stock Projection

```python
from erpnext.stock.utils import get_stock_projection

projection = get_stock_projection("ITEM-001", "Stores - MC")
```

---

## Related Topics
- [Stock Entry](./02_stock-entry.md)
- [Warehouse](./01_warehouse.md)
