# Purchase Invoice

## Quick Reference
Purchase Invoice records supplier billing. Creates GL Entry (liability + expense). Can update stock if received with invoice. Payment Entry links for payment.

## AI Prompt
```
When working with Purchase Invoice:
1. Verify supplier and rates
2. Check stock update setting
3. Validate taxes
4. Track payment status
5. Handle advance payments
```

---

## Purchase Invoice DocType

### Key Fields
| Field | Type | Description |
|-------|------|-------------|
| supplier | Link | Supplier reference |
| posting_date | Date | Invoice date |
| due_date | Date | Payment due date |
| items | Table | Invoice items |
| grand_total | Currency | Total amount |
| outstanding_amount | Currency | Amount due |
| update_stock | Check | Update stock on submit |

---

## Creating Purchase Invoice

### From Purchase Order
```python
from erpnext.buying.doctype.purchase_order.purchase_order import make_purchase_invoice

pi = make_purchase_invoice("PO-001")
pi.insert()
pi.submit()
```

### From Purchase Receipt
```python
from erpnext.stock.doctype.purchase_receipt.purchase_receipt import make_purchase_invoice

pi = make_purchase_invoice("PR-001")
pi.insert()
pi.submit()
```

### Standalone Invoice
```python
pi = frappe.get_doc({
    "doctype": "Purchase Invoice",
    "supplier": "XYZ Ltd",
    "posting_date": "2024-01-20",
    "due_date": "2024-02-20",
    "items": [{
        "item_code": "LAPTOP-001",
        "qty": 10,
        "rate": 35000,
        "warehouse": "Stores - MC"
    }]
})
pi.insert()
pi.submit()
```

---

## GL Entry

### On Submit
```
Purchase Invoice: 10 items @ 35000 = 350000 + 63000 GST = 413000

GL Entries:
┌─────────────────────┬─────────┬─────────┐
│ Account             │ Debit   │ Credit  │
├─────────────────────┼─────────┼─────────┤
│ COGS - MC           │ 350000  │ 0       │
│ GST Input - MC      │ 63000   │ 0       │
│ Creditors - MC      │ 0       │ 413000  │
└─────────────────────┴─────────┴─────────┘
```

---

## Payment

### Create Payment Entry
```python
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry

pe = get_payment_entry("Purchase Invoice", "PI-001")
pe.insert()
pe.submit()
```

---

## Related Topics
- [Purchase Order](./01_purchase-order.md)
- [Purchase Receipt](./02_purchase-receipt.md)
- [Payment Entry](../02_ACCOUNTING/03_payment-entry.md)
