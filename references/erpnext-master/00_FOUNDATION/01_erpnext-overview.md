# ERPNext Overview

## Quick Reference
ERPNext is a full-featured, open-source ERP built on Frappe Framework. It covers accounting, inventory, manufacturing, HR, sales, purchase, and more out of the box.

## What is ERPNext?

ERPNext is an enterprise resource planning (ERP) system developed by Frappe Technologies. It is:
- **Open Source**: GPL-3.0 licensed, fully accessible source code
- **Full-Stack**: Built on Frappe Framework (Python + JavaScript + MariaDB)
- **Modular**: Each business function is a separate module
- **Customizable**: Extend via custom apps, scripts, or configuration

## Core Philosophy

1. **Convention over Configuration**: Standard business flows work out of the box
2. **Meta-Driven**: DocTypes define data models and UI simultaneously
3. **Event-Driven**: Hooks and events for extending functionality
4. **Multi-Company**: Support for multiple companies in one instance
5. **Multi-Currency**: Native multi-currency support

---

## AI Prompt

\`\`\`
When analyzing an ERPNext requirement:
1. Identify which standard modules apply (Sales, Purchase, Stock, etc.)
2. Check if standard DocTypes can be extended vs creating new ones
3. Map business processes to document flows
4. Consider integration points with existing ERPNext features
\`\`\`

---

## Module Overview

### 1. Setup & Administration
- Company, Fiscal Year, Cost Center
- User, Role, Permission
- Naming Series, Workflow

### 2. Party Management
- **Customer**: Customer master, credit limits, groups
- **Supplier**: Supplier master, rating, groups
- **Lead**: Sales leads, qualification

### 3. Item & Pricing
- **Item**: Product/Service master with variants
- **Price List**: Multiple price lists (Selling/Buying)
- **Pricing Rules**: Discounts, schemes

### 4. Sales Cycle
\`\`\`
Lead → Opportunity → Quotation → Sales Order → Delivery Note → Sales Invoice → Payment
\`\`\`

### 5. Purchase Cycle
\`\`\`
Supplier Quotation → Purchase Order → Purchase Receipt → Purchase Invoice → Payment
\`\`\`

### 6. Stock & Inventory
- Warehouse management
- Stock Entry (receipt/issue/transfer/manufacture)
- Serial No & Batch management
- Stock valuation (FIFO/Moving Average)

### 7. Accounting
- Chart of Accounts
- Journal Entry, Payment Entry
- General Ledger, P&L, Balance Sheet

### 8. Manufacturing
- Bill of Materials (BOM)
- Work Order, Job Card
- Production Plan

### 9. Human Resources
- Employee master
- Attendance, Leave
- Payroll, Salary Structure

### 10. Projects
- Project, Task, Timesheet
- Project billing

---

## Key Concepts

### DocTypes (Document Types)
Every entity in ERPNext is a DocType. Examples:
- Master: Customer, Supplier, Item, Account
- Transaction: Sales Invoice, Purchase Order
- Child: Sales Invoice Item, Journal Entry Account

### Document Status (docstatus)
\`\`\`python
docstatus = 0  # Draft - editable
docstatus = 1  # Submitted - locked, accounting entries created
docstatus = 2  # Cancelled - reversing entries created
\`\`\`

### Naming Series
Auto-generated document names:
\`\`\`
SI-2024-00001  # Sales Invoice
PO-2024-00001  # Purchase Order
\`\`\`

### Ledgers
Three main ledgers:
1. **GL Entry**: Financial accounting
2. **Stock Ledger Entry**: Inventory tracking
3. **Payment Ledger Entry**: Payment tracking

---

## Common Operations

### Get Customer
\`\`\`python
customer = frappe.get_doc("Customer", "CUST-001")
print(customer.customer_name, customer.credit_limit)
\`\`\`

### Create Sales Invoice
\`\`\`python
si = frappe.get_doc({
    "doctype": "Sales Invoice",
    "customer": "CUST-001",
    "company": "My Company",
    "posting_date": "2024-01-15",
    "items": [{
        "item_code": "ITEM-001",
        "qty": 2,
        "rate": 100
    }]
})
si.insert()
si.submit()  # Creates GL Entry, Stock Ledger Entry
\`\`\`

### Get Stock Balance
\`\`\`python
from erpnext.stock.utils import get_stock_balance
balance = get_stock_balance("ITEM-001", "Stores - MC")
\`\`\`

---

## Integration Points

### Internal Integrations
- Sales Invoice ↔ Stock Ledger (stock update)
- Sales Invoice ↔ GL Entry (accounting)
- Payment Entry ↔ Sales Invoice (payment reconciliation)

### External Integrations
- REST API for external systems
- Webhooks for event notifications
- Payment gateways (Razorpay, Stripe)
- E-commerce (WooCommerce, Shopify)

---

## Related Topics
- [Architecture](./02_architecture.md)
- [Installation Setup](./03_installation-setup.md)
- [Modules Overview](./04_modules-overview.md)
