# Sales Invoice

## Quick Reference
Sales Invoice is the billing document. Creates GL Entry (receivables + income), optionally Stock Ledger Entry. Flow: Sales Order → Delivery Note → Sales Invoice → Payment Entry.

## AI Prompt
\`\`\`
When working with Sales Invoice:
1. Validate customer exists and has credit
2. Check item rates and taxes
3. Verify warehouse for stock items
4. Understand GL Entry creation (debit receivables, credit income)
5. Link to Sales Order/Delivery Note for tracking
\`\`\`

---

## Sales Invoice DocType

### Key Fields
| Field | Type | Description |
|-------|------|-------------|
| customer | Link | Customer reference |
| company | Link | Company |
| posting_date | Date | Invoice date |
| due_date | Date | Payment due date |
| items | Table | Invoice items |
| taxes | Table | Tax details |
| grand_total | Currency | Total amount |
| outstanding_amount | Currency | Amount due |
| update_stock | Check | Update stock on submit |

### Document Status
\`\`\`
docstatus = 0  # Draft
docstatus = 1  # Submitted (GL Entry created)
docstatus = 2  # Cancelled (Reversing GL Entry created)
\`\`\`

---

## Creating Sales Invoice

### Basic Creation
\`\`\`python
si = frappe.get_doc({
    "doctype": "Sales Invoice",
    "customer": "ABC Corp",
    "company": "My Company Ltd",
    "posting_date": "2024-01-15",
    "due_date": "2024-02-15",
    "items": [{
        "item_code": "LAPTOP-001",
        "qty": 2,
        "rate": 45000,
        "warehouse": "Stores - MC"
    }]
})
si.insert()
si.submit()
\`\`\`

### With Taxes
\`\`\`python
si = frappe.get_doc({
    "doctype": "Sales Invoice",
    "customer": "ABC Corp",
    "company": "My Company Ltd",
    "items": [{
        "item_code": "LAPTOP-001",
        "qty": 2,
        "rate": 45000
    }],
    "taxes": [{
        "charge_type": "On Net Total",
        "account_head": "GST - MC",
        "description": "GST 18%",
        "rate": 18
    }]
})
si.insert()
si.submit()
\`\`\`

### From Sales Order
\`\`\`python
# Get Sales Order
so = frappe.get_doc("Sales Order", "SO-001")

# Create Sales Invoice from Sales Order
from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
si = make_sales_invoice("SO-001")
si.insert()
si.submit()
\`\`\`

### From Delivery Note
\`\`\`python
from erpnext.stock.doctype.delivery_note.delivery_note import make_sales_invoice
si = make_sales_invoice("DN-001")
si.insert()
si.submit()
\`\`\`

---

## GL Entry Creation

### On Submit
\`\`\`
Sales Invoice (Grand Total: ₹90,000 + GST ₹16,200 = ₹1,06,200)

GL Entries:
┌─────────────────────┬────────┬────────┐
│ Account             │ Debit  │ Credit │
├─────────────────────┼────────┼────────┤
│ Debtors - MC        │ 1,06,200│       │
│ Sales - MC          │        │ 90,000 │
│ GST Output - MC     │        │ 16,200 │
└─────────────────────┴────────┴────────┘
\`\`\`

### Code Reference
\`\`\`python
# In Sales Invoice controller
def on_submit(self):
    self.make_gl_entries()
    if self.update_stock:
        self.update_stock_ledger()

def make_gl_entries(self):
    gl_entries = []
    
    # Debit Receivable
    gl_entries.append({
        "account": self.debit_to,
        "party_type": "Customer",
        "party": self.customer,
        "debit": self.grand_total,
        "credit": 0,
        "against": self.get_income_accounts()
    })
    
    # Credit Income
    for item in self.items:
        gl_entries.append({
            "account": item.income_account,
            "debit": 0,
            "credit": item.amount,
            "against": self.customer
        })
    
    # Credit Taxes
    for tax in self.taxes:
        gl_entries.append({
            "account": tax.account_head,
            "debit": 0,
            "credit": tax.tax_amount,
            "against": self.customer
        })
    
    from erpnext.accounts.general_ledger import make_gl_entries
    make_gl_entries(gl_entries)
\`\`\`

---

## Stock Update

### Update Stock on Submit
\`\`\`python
si = frappe.get_doc({
    "doctype": "Sales Invoice",
    "customer": "ABC Corp",
    "update_stock": 1,  # Enable stock update
    "items": [{
        "item_code": "LAPTOP-001",
        "qty": 2,
        "warehouse": "Stores - MC"
    }]
})
si.insert()
si.submit()  # Creates Stock Ledger Entry
\`\`\`

### Stock Ledger Entry Created
\`\`\`
Item: LAPTOP-001
Warehouse: Stores - MC
Qty: -2 (outward)
Voucher: SI-001
\`\`\`

---

## Payment Application

### Create Payment Entry
\`\`\`python
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry

# Create payment entry from Sales Invoice
pe = get_payment_entry("Sales Invoice", "SI-001")
pe.reference_no = "CHEQUE-123"
pe.reference_date = "2024-01-20"
pe.insert()
pe.submit()
\`\`\`

### Manual Payment Entry
\`\`\`python
pe = frappe.get_doc({
    "doctype": "Payment Entry",
    "payment_type": "Receive",
    "party_type": "Customer",
    "party": "ABC Corp",
    "paid_amount": 50000,
    "received_amount": 50000,
    "paid_to": "HDFC Bank - MC",
    "references": [{
        "reference_doctype": "Sales Invoice",
        "reference_name": "SI-001",
        "allocated_amount": 50000
    }]
})
pe.insert()
pe.submit()
\`\`\`

---

## Sales Invoice API

### Get Outstanding Amount
\`\`\`python
from erpnext.accounts.utils import get_balance_on

outstanding = frappe.db.get_value("Sales Invoice", "SI-001", "outstanding_amount")

# Or via customer
total_outstanding = get_balance_on(
    "Debtors - MC",
    party_type="Customer",
    party="ABC Corp"
)
\`\`\`

### Get Sales Invoice Details
\`\`\`python
si = frappe.get_doc("Sales Invoice", "SI-001")

# Grand total
print(si.grand_total)

# Outstanding
print(si.outstanding_amount)

# Status
print(si.status)  # Overdue, Paid, Unpaid, Cancelled

# Customer details
print(si.customer_name)
\`\`\`

### Cancel Sales Invoice
\`\`\`python
si = frappe.get_doc("Sales Invoice", "SI-001")
si.cancel()  # Creates reversing GL Entry
\`\`\`

---

## Hooks for Sales Invoice

### hooks.py
\`\`\`python
doc_events = {
    "Sales Invoice": {
        "validate": "custom_app.validation.validate_sales_invoice",
        "before_submit": "custom_app.hooks.before_sales_invoice_submit",
        "on_submit": "custom_app.hooks.on_sales_invoice_submit",
        "on_cancel": "custom_app.hooks.on_sales_invoice_cancel"
    }
}
\`\`\`

### Handler Examples
\`\`\`python
# custom_app/hooks.py

def on_sales_invoice_submit(doc, method):
    # Send email notification
    frappe.sendmail(
        recipients=doc.contact_email,
        subject=f"Invoice {doc.name}",
        message=f"Dear {doc.customer_name}, your invoice is ready."
    )
    
    # Update external system
    sync_to_external_system(doc)

def on_sales_invoice_cancel(doc, method):
    # Notify accounts team
    frappe.sendmail(
        recipients="accounts@company.com",
        subject=f"Invoice {doc.name} Cancelled",
        message=f"Invoice {doc.name} has been cancelled."
    )
\`\`\`

---

## Common Patterns

### Bulk Invoice Creation
\`\`\`python
def create_bulk_invoices(customers):
    for customer in customers:
        si = frappe.get_doc({
            "doctype": "Sales Invoice",
            "customer": customer,
            "company": "My Company Ltd",
            "items": [{
                "item_code": "SVC-001",
                "qty": 1,
                "rate": get_customer_rate(customer)
            }]
        })
        si.insert()
        si.submit()
    frappe.db.commit()
\`\`\`

### Check Credit Limit
\`\`\`python
from erpnext.selling.doctype.customer.customer import check_credit_limit

def validate_before_invoice(customer, amount):
    check_credit_limit(customer, "My Company Ltd")
    
    outstanding = get_balance_on("Debtors - MC", party=customer)
    credit_limit = frappe.db.get_value("Customer", customer, "credit_limit")
    
    if outstanding + amount > credit_limit:
        frappe.throw("Credit limit exceeded")
\`\`\`

---

## Related Topics
- [Sales Order](./02_sales-order.md)
- [Delivery Note](./03_delivery-note.md)
- [Payment Entry](../02_ACCOUNTING/03_payment-entry.md)
- [GL Entry](../02_ACCOUNTING/04_gl-ent
