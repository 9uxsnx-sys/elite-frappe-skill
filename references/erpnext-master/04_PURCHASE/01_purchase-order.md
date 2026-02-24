# Purchase Order

## Quick Reference
Purchase Order is a confirmed order to a supplier. Tracks goods receipt and billing. Creates no accounting entries until goods received or invoiced.

## AI Prompt
```
When working with Purchase Orders:
1. Verify supplier exists and is active
2. Check item purchase rates
3. Set expected delivery date
4. Track receipt and billing status
5. Handle partial receipts/invoices
```

---

## Purchase Order DocType

### Key Fields
| Field | Type | Description |
|-------|------|-------------|
| supplier | Link | Supplier reference |
| transaction_date | Date | Order date |
| schedule_date | Date | Expected delivery |
| items | Table | Order items |
| grand_total | Currency | Total amount |
| status | Select | Draft/To Receive/To Bill/Completed |

### Status Values
- Draft
- On Hold
- To Receive and Bill
- To Bill
- To Receive
- Completed
- Cancelled
- Closed

---

## Creating Purchase Order

### Basic Purchase Order
```python
po = frappe.get_doc({
    "doctype": "Purchase Order",
    "supplier": "XYZ Ltd",
    "transaction_date": "2024-01-15",
    "schedule_date": "2024-01-25",
    "items": [{
        "item_code": "LAPTOP-001",
        "qty": 10,
        "rate": 35000,
        "warehouse": "Stores - MC"
    }]
})
po.insert()
po.submit()
```

### From Supplier Quotation
```python
from erpnext.buying.doctype.supplier_quotation.supplier_quotation import make_purchase_order

po = make_purchase_order("SQ-001")
po.insert()
po.submit()
```

---

## Receipt and Billing

### Create Purchase Receipt
```python
from erpnext.buying.doctype.purchase_order.purchase_order import make_purchase_receipt

pr = make_purchase_receipt("PO-001")
pr.insert()
pr.submit()
```

### Create Purchase Invoice
```python
from erpnext.buying.doctype.purchase_order.purchase_order import make_purchase_invoice

pi = make_purchase_invoice("PO-001")
pi.insert()
pi.submit()
```

---

## Tracking

### Check Receipt Status
```python
po = frappe.get_doc("Purchase Order", "PO-001")

for item in po.items:
    received_qty = frappe.db.get_value("Purchase Receipt Item",
        {"purchase_order": po.name, "item_code": item.item_code},
        "SUM(qty)") or 0
```

### Check Billing Status
```python
for item in po.items:
    billed_qty = frappe.db.get_value("Purchase Invoice Item",
        {"purchase_order": po.name, "item_code": item.item_code},
        "SUM(qty)") or 0
```

---

## Related Topics
- [Purchase Receipt](./02_purchase-receipt.md)
- [Purchase Invoice](./03_purchase-invoice.md)
