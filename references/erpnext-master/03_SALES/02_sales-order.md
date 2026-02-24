# Sales Order

## Quick Reference
Sales Order is a confirmed order from customer. Tracks delivery schedule, billing status, and stock reservation. Links Quotation to Delivery Note and Sales Invoice.

## AI Prompt
```
When working with Sales Orders:
1. Validate stock availability
2. Check credit limits
3. Set delivery dates appropriately
4. Track delivery and billing status
5. Handle partial deliveries/invoices
```

---

## Sales Order DocType

### Key Fields
| Field | Type | Description |
|-------|------|-------------|
| customer | Link | Customer reference |
| transaction_date | Date | Order date |
| delivery_date | Date | Expected delivery |
| items | Table | Order items |
| grand_total | Currency | Total amount |
| status | Select | Draft/To Deliver/To Bill/Completed |

### Status Values
- Draft
- On Hold
- To Deliver and Bill
- To Bill
- To Deliver
- Completed
- Cancelled
- Closed

---

## Creating Sales Order

### Basic Sales Order
```python
so = frappe.get_doc({
    "doctype": "Sales Order",
    "customer": "ABC Corp",
    "transaction_date": "2024-01-15",
    "delivery_date": "2024-01-25",
    "items": [{
        "item_code": "LAPTOP-001",
        "qty": 2,
        "rate": 45000,
        "warehouse": "Stores - MC"
    }]
})
so.insert()
so.submit()
```

### From Quotation
```python
from erpnext.selling.doctype.quotation.quotation import make_sales_order

so = make_sales_order("QT-001")
so.insert()
so.submit()
```

---

## Delivery and Billing Tracking

### Check Delivery Status
```python
so = frappe.get_doc("Sales Order", "SO-001")

for item in so.items:
    delivered_qty = frappe.db.get_value("Delivery Note Item",
        {"against_sales_order": so.name, "item_code": item.item_code},
        "SUM(qty)") or 0
    print(f"{item.item_code}: Ordered={item.qty}, Delivered={delivered_qty}")
```

### Check Billing Status
```python
so = frappe.get_doc("Sales Order", "SO-001")

for item in so.items:
    billed_qty = frappe.db.get_value("Sales Invoice Item",
        {"sales_order": so.name, "item_code": item.item_code},
        "SUM(qty)") or 0
    print(f"{item.item_code}: Ordered={item.qty}, Billed={billed_qty}")
```

---

## Create Deliveries and Invoices

### Create Delivery Note
```python
from erpnext.selling.doctype.sales_order.sales_order import make_delivery_note

dn = make_delivery_note("SO-001")
dn.insert()
dn.submit()
```

### Create Sales Invoice
```python
from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice

si = make_sales_invoice("SO-001")
si.insert()
si.submit()
```

### Partial Delivery
```python
dn = make_delivery_note("SO-001")
# Modify quantities before submitting
dn.items[0].qty = 1  # Partial delivery
dn.insert()
dn.submit()
```

---

## Stock Reservation

### Reserve Stock on Submit
```python
# Sales Order reserves stock when submitted
# Check reserved stock
for item in so.items:
    reserved = frappe.db.get_value("Stock Reservation Entry",
        {"sales_order": so.name, "item_code": item.item_code},
        "SUM(qty)") or 0
```

### Release Reserved Stock
```python
# On cancel or close
so = frappe.get_doc("Sales Order", "SO-001")
so.cancel()  # Releases reservations
```

---

## Related Topics
- [Quotation](./01_quotation.md)
- [Delivery Note](./03_delivery-note.md)
- [Sales Invoice](./04_sales-invoice.md)
