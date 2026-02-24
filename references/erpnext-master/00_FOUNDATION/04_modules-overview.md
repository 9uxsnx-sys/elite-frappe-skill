# ERPNext Modules Overview

## Quick Reference
ERPNext has 12+ core modules: Setup, CRM, Selling, Buying, Stock, Accounts, HR, Payroll, Manufacturing, Projects, Quality, Website. Each module contains related DocTypes and workflows.

## AI Prompt
\`\`\`
When designing a feature:
1. Identify which module(s) the feature belongs to
2. Check for existing DocTypes that can be extended
3. Understand inter-module dependencies
4. Consider document flow between modules
\`\`\`

---

## Module Map

\`\`\`
┌──────────────────────────────────────────────────────────────┐
│                        ERPNext Modules                        │
├──────────────┬──────────────┬──────────────┬─────────────────┤
│    Setup     │     CRM      │   Selling    │     Buying      │
├──────────────┼──────────────┼──────────────┼─────────────────┤
│    Stock     │   Accounts   │      HR      │    Payroll      │
├──────────────┼──────────────┼──────────────┼─────────────────┤
│Manufacturing │   Projects   │   Quality    │    Website      │
└──────────────┴──────────────┴──────────────┴─────────────────┘
\`\`\`

---

## Module Details

### 1. Setup
Core configuration for the system.

| DocType | Purpose |
|---------|---------|
| Company | Company master data |
| Fiscal Year | Financial periods |
| Cost Center | Cost allocation |
| Naming Series | Document numbering |
| Workflow | Approval workflows |

### 2. CRM (Customer Relationship Management)
Manage leads and opportunities.

| DocType | Purpose |
|---------|---------|
| Lead | Potential customers |
| Opportunity | Sales opportunities |
| Campaign | Marketing campaigns |
| Customer | Customer master |

**Flow**: Lead → Opportunity → Quotation

### 3. Selling (Sales)
Sales transactions and delivery.

| DocType | Purpose |
|---------|---------|
| Quotation | Price quotes |
| Sales Order | Confirmed orders |
| Delivery Note | Goods delivery |
| Sales Invoice | Billing |

**Flow**: Quotation → Sales Order → Delivery Note → Sales Invoice

### 4. Buying (Purchase)
Procurement and purchasing.

| DocType | Purpose |
|---------|---------|
| Supplier Quotation | Vendor quotes |
| Purchase Order | Purchase orders |
| Purchase Receipt | Goods receipt |
| Purchase Invoice | Vendor billing |

**Flow**: Supplier Quotation → Purchase Order → Purchase Receipt → Purchase Invoice

### 5. Stock (Inventory)
Warehouse and inventory management.

| DocType | Purpose |
|---------|---------|
| Item | Product master |
| Warehouse | Storage locations |
| Stock Entry | Stock movements |
| Serial No | Serial tracking |
| Batch | Batch tracking |

**Operations**:
- Material Receipt (inward)
- Material Issue (outward)
- Material Transfer (between warehouses)
- Manufacture (production)

### 6. Accounts (Accounting)
Financial accounting and reporting.

| DocType | Purpose |
|---------|---------|
| Account | Chart of accounts |
| Journal Entry | Manual entries |
| Payment Entry | Payments |
| GL Entry | General ledger |

**Key Concepts**:
- Double-entry bookkeeping
- Debit/Credit balancing
- Fiscal periods

### 7. HR (Human Resources)
Employee management.

| DocType | Purpose |
|---------|---------|
| Employee | Employee master |
| Attendance | Attendance tracking |
| Leave Application | Leave management |
| Expense Claim | Employee expenses |

### 8. Payroll
Salary and compensation.

| DocType | Purpose |
|---------|---------|
| Salary Structure | Pay structure |
| Salary Slip | Paycheck |
| Salary Component | Earnings/deductions |

### 9. Manufacturing
Production and BOM.

| DocType | Purpose |
|---------|---------|
| BOM | Bill of Materials |
| Work Order | Production order |
| Job Card | Shop floor work |
| Production Plan | Planning |

**Flow**: BOM → Production Plan → Work Order → Job Card → Stock Entry

### 10. Projects
Project and task management.

| DocType | Purpose |
|---------|---------|
| Project | Project master |
| Task | Project tasks |
| Timesheet | Time tracking |

### 11. Quality Management
Quality control.

| DocType | Purpose |
|---------|---------|
| Quality Inspection | QC checks |
| Quality Goal | Quality targets |
| Quality Feedback | Customer feedback |

### 12. Website
Website and e-commerce.

| DocType | Purpose |
|---------|---------|
| Item (published) | Product catalog |
| Web Form | Public forms |
| Shopping Cart | E-commerce |

---

## Inter-Module Dependencies

### Sales + Stock
\`\`\`
Sales Order → Delivery Note → Stock Ledger Entry
\`\`\`

### Sales + Accounts
\`\`\`
Sales Invoice → GL Entry → Account Balance
\`\`\`

### Purchase + Stock
\`\`\`
Purchase Receipt → Stock Ledger Entry
\`\`\`

### Manufacturing + Stock
\`\`\`
Work Order → Stock Entry → Stock Ledger Entry
\`\`\`

### HR + Payroll + Accounts
\`\`\`
Employee → Salary Slip → GL Entry (Salary Payable)
\`\`\`

---

## Module Directory Structure

\`\`\`
erpnext/
├── accounts/           # Accounting
├── buying/             # Purchase
├── crm/                # CRM
├── hr/                 # HR
├── manufacturing/      # Manufacturing
├── payroll/            # Payroll
├── projects/           # Projects
├── quality_management/ # Quality
├── selling/            # Sales
├── setup/              # Setup
├── stock/              # Inventory
└── website/            # Website
\`\`\`

---

## Common Module Patterns

### Getting Items from a Module
\`\`\`python
# Sales module
from erpnext.selling.doctype.sales_order.sales_order import SalesOrder

# Stock module
from erpnext.stock.doctype.stock_entry.stock_entry import StockEntry

# Accounts module
from erpnext.accounts.doctype.payment_entry.payment_entry import PaymentEntry
\`\`\`

### Cross-Module Operations
\`\`\`python
# Create Delivery Note from Sales Order
so = frappe.get_doc("Sales Order", "SO-001")
dn = make_delivery_note(so.name)
dn.insert()
dn.submit()

# Create Sales Invoice from Delivery Note
dn = frappe.get_doc("Delivery Note", "DN-001")
si = make_sales_invoice(dn.name)
si.insert()
si.submit()
\`\`\`

---

## Related Topics
- [ERPNext Overview](./01_erpnext-overview.md)
- [Architecture](./02_architecture.md)
