# Purchase Receipt

## Quick Reference
Purchase Receipt records goods received from supplier. Creates Stock Ledger Entry (positive) and pending liability. Links to Purchase Invoice for billing.

## AI Prompt
```
When working with Purchase Receipts:
1. Validate against Purchase Order
2. Check warehouse for stock addition
3. Handle serial/batch for tracked items
4. Track billing status
5. Handle rejections/returns
```

---

## Purchase Receipt DocType

### Key Fields
| Field | Type | Description |
|-------|------|-------------|
| supplier | Link | Supplier reference |
| posting_date | Date | Receipt date |
| items | Table | Received items |
| status | Select | Draft/To Bill/Completed |
| is_return | Check | Is this a return |

---

## Creating Purchase Receipt

### From Purchase Order
```python
from erpnext.buying.doctype.purchase_order.purchase_order import make_purchase_receipt

pr = make_purchase_receipt("PO-001")
pr.insert()
pr.submit()
```

### Standalone Receipt
```python
pr = frappe.get_doc({
    "doctype": "Purchase Receipt",
    "supplier": "XYZ Ltd",
    "posting_date": "2024-01-20",
    "items": [{
        "item_code": "LAPTOP-001",
        "qty": 10,
        "warehouse": "Stores - MC",
        "rate": 35000
    }]
})
pr.insert()
pr.submit()
```

---

## Stock Impact

### Stock Ledger Entry
```python
# On submit, creates SLE with positive qty
{
    "item_code": "LAPTOP-001",
    "warehouse": "Stores - MC",
    "actual_qty": 10,  # Positive for receipt
    "voucher_type": "Purchase Receipt",
    "voucher_no": "PR-001"
}
```

### GL Entry (Pending Liability)
```python
# Debit Stock, Credit Supplier
{
    "account": "Stock Assets - MC",
    "debit": 350000
},
{
    "account": "Creditors - MC",
    "credit": 350000
}
```

---

## Create Purchase Invoice

```python
from erpnext.stock.doctype.purchase_receipt.purchase_receipt import make_purchase_invoice

pi = make_purchase_invoice("PR-001")
pi.insert()
pi.submit()
```

---

## Purchase Return

```python
from erpnext.stock.doctype.purchase_receipt.purchase_receipt import make_purchase_return

return_pr = make_purchase_return("PR-001")
return_pr.insert()
return_pr.submit()
```

---

## Related Topics
- [Purchase Order](./01_purchase-order.md)
- [Purchase Invoice](./03_purchase-invoice.md)
