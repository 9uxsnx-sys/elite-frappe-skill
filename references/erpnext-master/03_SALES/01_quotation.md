# Quotation

## Quick Reference
Quotation is the first formal sales document. Contains customer, items, rates, and validity. Can be created from Lead/Opportunity and converted to Sales Order.

## AI Prompt
```
When working with Quotations:
1. Check customer validity and credit
2. Ensure correct price list and rates
3. Set validity date appropriately
4. Track conversion to Sales Order
5. Handle revision workflow properly
```

---

## Quotation DocType

### Key Fields
| Field | Type | Description |
|-------|------|-------------|
| quotation_to | Select | Customer/Lead |
| party_name | Dynamic Link | Customer or Lead |
| transaction_date | Date | Quotation date |
| valid_till | Date | Validity date |
| items | Table | Quoted items |
| grand_total | Currency | Total amount |
| status | Select | Draft/Sent/Ordered/Lost |

### Status Flow
```
Draft → Open → Ordered → (converted to SO)
                → Lost → (closed)
                → Expired → (auto on valid_till)
```

---

## Creating Quotation

### Basic Quotation
```python
qt = frappe.get_doc({
    "doctype": "Quotation",
    "quotation_to": "Customer",
    "party_name": "ABC Corp",
    "transaction_date": "2024-01-15",
    "valid_till": "2024-02-15",
    "items": [{
        "item_code": "LAPTOP-001",
        "qty": 2,
        "rate": 45000
    }]
})
qt.insert()
```

### From Lead
```python
from erpnext.crm.doctype.lead.lead import make_quotation

qt = make_quotation("LEAD-001")
qt.items = [{"item_code": "ITEM-001", "qty": 1, "rate": 100}]
qt.insert()
qt.submit()
```

### From Opportunity
```python
from erpnext.crm.doctype.opportunity.opportunity import make_quotation

qt = make_quotation("OPP-001")
qt.insert()
qt.submit()
```

---

## Conversion to Sales Order

### Via Python
```python
from erpnext.selling.doctype.quotation.quotation import make_sales_order

so = make_sales_order("QT-001")
so.delivery_date = "2024-02-01"
so.insert()
so.submit()

# Update quotation status
frappe.db.set_value("Quotation", "QT-001", "status", "Ordered")
```

---

## Quotation API

### Get Quotation Details
```python
qt = frappe.get_doc("Quotation", "QT-001")
print(qt.party_name, qt.grand_total, qt.status)
```

### Check if Ordered
```python
def is_quotation_ordered(quotation):
    so = frappe.db.get_value("Sales Order Item",
        {"prevdoc_docname": quotation}, "parent")
    return so
```

### Mark as Lost
```python
qt = frappe.get_doc("Quotation", "QT-001")
qt.status = "Lost"
qt.order_lost_reason = "Price too high"
qt.save()
```

---

## Related Topics
- [Sales Order](./02_sales-order.md)
- [Lead](../07_CRM/01_lead.md)
- [Opportunity](../07_CRM/02_opportunity.md)
