# ERPNext Architecture

## Quick Reference
ERPNext extends Frappe Framework with business logic. Core architecture: Frappe (ORM, UI, API) + ERPNext (Business Modules) + MariaDB (Database) + Redis (Cache/Queue).

## AI Prompt
\`\`\`
When debugging or extending ERPNext:
1. Check if issue is Frappe-level (ORM, hooks) or ERPNext-level (business logic)
2. Trace document lifecycle: validate → on_update → on_submit
3. Check ledger creation: make_gl_entry(), make_sl_entry()
4. Verify company/account/warehouse mappings
\`\`\`

---

## Architecture Layers

### Layer 1: Frappe Framework (Foundation)
\`\`\`
┌─────────────────────────────────────┐
│         Frappe Framework            │
├─────────────────────────────────────┤
│ • ORM (Document, DB API)            │
│ • Desk UI (Vue.js)                  │
│ • REST API                          │
│ • Auth & Permissions                │
│ • Hooks System                      │
│ • Background Jobs                   │
└─────────────────────────────────────┘
\`\`\`

### Layer 2: ERPNext (Business Logic)
\`\`\`
┌─────────────────────────────────────┐
│           ERPNext                   │
├─────────────────────────────────────┤
│ • Sales & CRM                       │
│ • Purchase                          │
│ • Stock & Inventory                 │
│ • Accounting                        │
│ • Manufacturing                     │
│ • HR & Payroll                      │
│ • Projects                          │
└─────────────────────────────────────┘
\`\`\`

### Layer 3: Custom Apps
\`\`\`
┌─────────────────────────────────────┐
│         Custom Apps                 │
├─────────────────────────────────────┤
│ • Extend ERPNext DocTypes           │
│ • Override controllers              │
│ • Add custom fields                 │
│ • Custom workflows                  │
│ • Integrations                      │
└─────────────────────────────────────┘
\`\`\`

---

## Directory Structure

\`\`\`
erpnext/
├── erpnext/
│   ├── accounts/          # Accounting module
│   │   ├── doctype/
│   │   │   ├── sales_invoice/
│   │   │   │   ├── sales_invoice.py      # Controller
│   │   │   │   ├── sales_invoice.json    # DocType definition
│   │   │   │   └── sales_invoice.js      # Client script
│   │   ├── report/
│   │   └── ...
│   ├── stock/             # Stock module
│   ├── buying/            # Purchase module
│   ├── selling/           # Sales module
│   ├── hr/                # HR module
│   ├── manufacturing/     # Manufacturing module
│   ├── projects/          # Projects module
│   ├── setup/             # Setup doctypes
│   └── hooks.py           # ERPNext hooks
└── setup.py
\`\`\`

---

## Key Controllers

### Sales Invoice Controller
\`\`\`python
# erpnext/accounts/doctype/sales_invoice/sales_invoice.py

class SalesInvoice(SellingController):
    def validate(self):
        # Validation logic
        self.validate_posting_date()
        self.validate_due_date()
        
    def on_submit(self):
        # Create ledgers
        self.make_gl_entries()  # Financial accounting
        self.update_stock_ledger()  # If update_stock=1
        
    def on_cancel(self):
        # Reverse entries
        self.make_gl_entries_on_cancel()
\`\`\`

### Stock Entry Controller
\`\`\`python
# erpnext/stock/doctype/stock_entry/stock_entry.py

class StockEntry(StockController):
    def on_submit(self):
        self.make_stock_ledger_entry()
        self.make_gl_entries()  # If valuation
        
    def on_cancel(self):
        self.make_stock_ledger_entry(cancel=1)
\`\`\`

---

## Ledger Flow

### GL Entry Flow (Accounting)
\`\`\`
Document (SI/PI/JE)
    ↓ on_submit()
make_gl_entries()
    ↓
tabGL Entry (debit/credit records)
    ↓
Account balance updated
\`\`\`

### Stock Ledger Flow (Inventory)
\`\`\`
Document (SE/DN/PI)
    ↓ on_submit()
make_stock_ledger_entry()
    ↓
tabStock Ledger Entry
    ↓
Stock balance updated
\`\`\`

---

## Hooks System

### ERPNext hooks.py
\`\`\`python
# erpnext/hooks.py

doc_events = {
    "*": {
        "validate": [
            "erpnext.accounts.doctype.accounting_period.accounting_period.validate_accounting_period"
        ]
    },
    "Sales Invoice": {
        "on_submit": "erpnext.controllers.accounts_controller.on_submit",
        "on_cancel": "erpnext.controllers.accounts_controller.on_cancel"
    }
}

extend_doctype_class = {
    "Address": "erpnext.accounts.custom.address.ERPNextAddress"
}
\`\`\`

### Custom App hooks.py
\`\`\`python
# custom_app/hooks.py

doc_events = {
    "Sales Invoice": {
        "validate": "custom_app.validation.validate_sales_invoice",
        "on_submit": "custom_app.handlers.on_sales_invoice_submit"
    }
}

override_doctype_class = {
    "Sales Invoice": "custom_app.overrides.CustomSalesInvoice"
}
\`\`\`

---

## Data Flow Examples

### Sales Invoice Creation
\`\`\`
1. User fills form → Client validation
2. save() → validate() on server
3. insert() → before_insert(), after_insert()
4. submit() → validate(), on_submit()
5. on_submit() → 
   - make_gl_entries() → GL Entry records
   - update_stock_ledger() → Stock Ledger (if applicable)
   - update_status() → Status change
\`\`\`

### Payment Application
\`\`\`
Payment Entry
    ↓ on_submit()
create_payment_ledger_entry()
    ↓
Link to Sales Invoice
    ↓
Update outstanding amount on SI
\`\`\`

---

## Key Tables

| Purpose | Table | Related DocType |
|---------|-------|-----------------|
| Documents | tab[DocType] | All DocTypes |
| GL | tabGL Entry | All accounts transactions |
| Stock | tabStock Ledger Entry | All stock movements |
| Payment | tabPayment Ledger Entry | All payments |
| Permissions | tabDocPerm | Role-based access |
| Customization | tabCustom Field | Added fields |
| Properties | tabProperty Setter | Modified properties |

---

## Related Topics
- [ERPNext Overview](./01_erpnext-overview.md)
- [Frappe Framework Architecture](../../frappe-framework-master/00_FOUNDATION/01_architecture.md)
