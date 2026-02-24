# Serial No & Batch

## Quick Reference
Serial No tracks individual items. Batch tracks groups of items. Both enable traceability and expiry management.

## AI Prompt
```
When working with Serial/Batch:
1. Enable in Item settings
2. Generate or import serials
3. Track movements
4. Handle expiry for batches
5. Validate on transactions
```

---

## Serial No

### Creating Serial Numbers
```python
# Auto-generate on Stock Entry
se = frappe.get_doc({
    "doctype": "Stock Entry",
    "stock_entry_type": "Material Receipt",
    "items": [{
        "item_code": "LAPTOP-001",
        "qty": 2,
        "t_warehouse": "Stores - MC",
        "serial_no": "SN001\nSN002",  # Newline separated
        "basic_rate": 35000
    }]
})

# Or create manually
serial = frappe.get_doc({
    "doctype": "Serial No",
    "item_code": "LAPTOP-001",
    "serial_no": "SN001",
    "warehouse": "Stores - MC",
    "purchase_rate": 35000
})
serial.insert()
```

### Querying Serial No
```python
# Get serial info
serial = frappe.get_doc("Serial No", "SN001")
print(serial.warehouse, serial.status)

# Get serials for item
serials = frappe.get_all("Serial No",
    filters={"item_code": "LAPTOP-001", "warehouse": "Stores - MC"},
    fields=["name", "serial_no", "warranty_expiry_date"]
)
```

---

## Batch

### Creating Batch
```python
batch = frappe.get_doc({
    "doctype": "Batch",
    "item": "MEDICINE-001",
    "batch_id": "BATCH-2024-001",
    "expiry_date": "2025-12-31",
    "manufacturing_date": "2024-01-01"
})
batch.insert()
```

### Using Batch in Stock Entry
```python
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
```

### Batch Expiry Check
```python
from erpnext.stock.doctype.batch.batch import get_batches

batches = get_batches("MEDICINE-001", "Stores - MC")
for batch in batches:
    print(f"{batch.batch_no}: Expires {batch.expiry_date}")
```

---

## Related Topics
- [Stock Entry](./02_stock-entry.md)
- [Item Master](../01_CORE_DOCTYPES/02_item-master.md)
