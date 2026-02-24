# ERPNext Quick Reference

## Core DocTypes by Module

| Module | Key DocTypes |
|--------|-------------|
| Setup | Company, Fiscal Year, Cost Center |
| Party | Customer, Supplier, Lead |
| Item | Item, Item Group, Price List, Item Price |
| Sales | Quotation, Sales Order, Delivery Note, Sales Invoice |
| Purchase | Supplier Quotation, Purchase Order, Purchase Receipt, Purchase Invoice |
| Stock | Warehouse, Stock Entry, Stock Reconciliation |
| Accounts | Account, Journal Entry, Payment Entry |
| HR | Employee, Salary Slip, Attendance, Leave Application |
| Manufacturing | BOM, Work Order, Job Card |
| Projects | Project, Task, Timesheet |

---

## Document Status Flow

\`\`\`
Draft → Submitted → Cancelled
  0        1          2
\`\`\`

## Common Code Patterns

### Get Document
\`\`\`python
doc = frappe.get_doc("Sales Invoice", "SI-001")
\`\`\`

### Create Document
\`\`\`python
doc = frappe.get_doc({
    "doctype": "Sales Invoice",
    "customer": "CUST-001"
})
doc.insert()
doc.submit()
\`\`\`

### Query
\`\`\`python
items = frappe.get_all("Item", fields=["name", "item_name"])
\`\`\`

### Get Stock Balance
\`\`\`python
from erpnext.stock.utils import get_stock_balance
balance = get_stock_balance(item_code, warehouse)
\`\`\`

---

## Key Hooks

\`\`\`python
# hooks.py for custom app extending ERPNext

doc_events = {
    "Sales Invoice": {
        "on_submit": "custom_app.handlers.sales_invoice_on_submit",
        "validate": "custom_app.handlers.sales_invoice_validate"
    }
}

override_doctype_class = {
    "Sales Invoice": "custom_app.overrides.CustomSalesInvoice"
}
\`\`\`

---

## Common Field Names

| Purpose | Field Name |
|---------|------------|
| Customer | customer |
| Supplier | supplier |
| Item | item_code |
| Quantity | qty |
| Rate | rate |
| Amount | amount |
| Warehouse | warehouse |
| Account | account |
| Company | company |
| Posting Date | posting_date |
| Grand Total | grand_total |

---

## Bench Commands

\`\`\`bash
bench --site [site] console
bench --site [site] backup
bench --site [site] migrate
bench --site [site] clear-cache
\`\`\`
