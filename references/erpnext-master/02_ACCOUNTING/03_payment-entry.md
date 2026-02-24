# Payment Entry

## Quick Reference
Payment Entry records all payments (receive/pay). Creates GL Entry. Links to invoices for reconciliation. Supports advances and multi-currency.

## AI Prompt
```
When creating payment entries:
1. Set correct payment type (Receive/Pay)
2. Link to invoices for reconciliation
3. Verify account balances
4. Handle advances separately
5. Check currency and exchange rate
```

---

## Payment Entry DocType

### Key Fields
| Field | Type | Description |
|-------|------|-------------|
| payment_type | Select | Receive/Pay/Internal Transfer |
| party_type | Select | Customer/Supplier/Employee |
| party | Dynamic Link | Party reference |
| paid_amount | Currency | Payment amount |
| paid_to | Link | Account credited (Receive) |
| paid_from | Link | Account debited (Pay) |
| references | Table | Invoice references |

---

## Creating Payment Entry

### Receive Payment
```python
pe = frappe.get_doc({
    "doctype": "Payment Entry",
    "payment_type": "Receive",
    "party_type": "Customer",
    "party": "ABC Corp",
    "paid_amount": 10000,
    "received_amount": 10000,
    "paid_to": "HDFC Bank - MC",
    "references": [{
        "reference_doctype": "Sales Invoice",
        "reference_name": "SI-001",
        "allocated_amount": 10000
    }]
})
pe.insert()
pe.submit()
```

### Pay to Supplier
```python
pe = frappe.get_doc({
    "doctype": "Payment Entry",
    "payment_type": "Pay",
    "party_type": "Supplier",
    "party": "XYZ Ltd",
    "paid_amount": 50000,
    "paid_from": "HDFC Bank - MC",
    "references": [{
        "reference_doctype": "Purchase Invoice",
        "reference_name": "PI-001",
        "allocated_amount": 50000
    }]
})
pe.insert()
pe.submit()
```

### From Invoice
```python
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry

pe = get_payment_entry("Sales Invoice", "SI-001")
pe.insert()
pe.submit()
```

---

## Advance Payment

```python
# Payment without invoice reference
pe = frappe.get_doc({
    "doctype": "Payment Entry",
    "payment_type": "Receive",
    "party_type": "Customer",
    "party": "ABC Corp",
    "paid_amount": 50000,
    "paid_to": "HDFC Bank - MC"
    # No references - this is an advance
})
pe.insert()
pe.submit()
```

---

## GL Entry

```
Payment Entry: Receive 10000 from ABC Corp

GL Entries:
┌─────────────────────┬─────────┬─────────┐
│ Account             │ Debit   │ Credit  │
├─────────────────────┼─────────┼─────────┤
│ HDFC Bank - MC      │ 10000   │ 0       │
│ Debtors - MC        │ 0       │ 10000   │
└─────────────────────┴─────────┴─────────┘
```

---

## Related Topics
- [Sales Invoice](../03_SALES/04_sales-invoice.md)
- [Purchase Invoice](../04_PURCHASE/03_purchase-invoice.md)
- [GL Entry](./04_gl-entry.md)
