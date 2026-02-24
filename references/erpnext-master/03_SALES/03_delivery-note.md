# Delivery Note

## Quick Reference
Delivery Note records goods sent to customer. Creates Stock Ledger Entry. Can be created from Sales Order or standalone. Links to Sales Invoice for billing.

## AI Prompt
```
When working with Delivery Notes:
1. Validate stock availability before delivery
2. Check Sales Order linkage for tracking
3. Ensure correct warehouse for stock deduction
4. Handle serial/batch items properly
5. Link to Sales Invoice for billing
```

---

## Delivery Note DocType

### Key Fields
| Field | Type | Description |
|-------|------|-------------|
| customer | Link | Customer reference |
| posting_date | Date | Delivery date |
| items | Table | Delivered items |
| status | Select | Draft/To Bill/Completed |
| is_return | Check | Is this a return |

---

## Creating Delivery Note

### From Sales Order
```python
from erpnext.selling.doctype.sales_order.sales_order import make_delivery_note

dn = make_delivery_note("SO-001")
dn.insert()
dn.submit()
```

### Standalone Delivery Note
```python
dn = frappe.get_doc({
    "doctype": "Delivery Note",
    "customer": "ABC Corp",
    "posting_date": "2024-01-20",
    "items": [{
        "item_code": "LAPTOP-001",
        "qty": 2,
        "warehouse": "Stores - MC",
        "rate": 45000
    }]
})
dn.insert()
dn.submit()
```

---

## Stock Impact

### Stock Ledger Entry
```python
# On submit, creates SLE with negative qty
{
    "item_code": "LAPTOP-001",
    "warehouse": "Stores - MC",
    "actual_qty": -2,  # Negative for issue
    "voucher_type": "Delivery Note",
    "voucher_no": "DN-001"
}
```

### Check Stock Before Delivery
```python
from erpnext.stock.utils import get_stock_balance

for item in dn.items:
    available = get_stock_balance(item.item_code, item.warehouse)
    if available < item.qty:
        frappe.throw(f"Insufficient stock for {item.item_code}")
```

---

## Create Sales Invoice

### From Delivery Note
```python
from erpnext.stock.doc
