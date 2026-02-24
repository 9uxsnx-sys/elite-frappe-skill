# Company Setup

## Quick Reference
Company is the primary entity in ERPNext. Setup involves: Company creation → Chart of Accounts → Cost Centers → Warehouses → Default settings. All transactions require a Company.

## AI Prompt
\`\`\`
When setting up a new company:
1. Plan Chart of Accounts structure
2. Define Cost Centers for cost allocation
3. Create Warehouses for inventory
4. Set default accounts for auto-accounting
5. Configure fiscal years and periods
\`\`\`

---

## Company DocType

### Key Fields
| Field | Description | Required |
|-------|-------------|----------|
| company_name | Legal name of company | Yes |
| abbreviation | Short code (e.g., MC) | Yes |
| country | Country of operation | Yes |
| default_currency | Base currency | Yes |
| is_group | Parent company flag | No |

### Creating Company
\`\`\`python
company = frappe.get_doc({
    "doctype": "Company",
    "company_name": "My Company Ltd",
    "abbr": "MC",
    "country": "India",
    "default_currency": "INR",
    "chart_of_accounts": "Standard"
})
company.insert()
\`\`\`

---

## Chart of Accounts Setup

### Standard Charts Available
- Standard (Default)
- Standard with Numbers
- Chart based on country

### Account Types
| Type | Purpose |
|------|---------|
| Accumulated Depreciation | Asset depreciation |
| Asset | Fixed/current assets |
| Bank | Bank accounts |
| Cash | Cash accounts |
| Chargeable | Service items |
| Cost of Goods Sold | COGS |
| Depreciation | Depreciation expense |
| Equity | Owner's equity |
| Expense | Operating expenses |
| Fixed Asset | Long-term assets |
| Income | Revenue |
| Liability | Debts/obligations |
| Payable | Amounts owed |
| Receivable | Amounts due |
| Stock | Inventory valuation |
| Tax | Tax accounts |
| Temporary | Temporary accounts |

### Creating Account
\`\`\`python
account = frappe.get_doc({
    "doctype": "Account",
    "account_name": "Sales",
    "company": "My Company Ltd",
    "parent_account": "Income - MC",
    "account_type": "Income",
    "root_type": "Income"
})
account.insert()
\`\`\`

---

## Default Accounts

These accounts are auto-set during document submission.

| Default | Purpose |
|---------|---------|
| default_receivable_account | Customer receivables |
| default_payable_account | Supplier payables |
| default_income_account | Sales income |
| default_expense_account | Purchase expense |
| default_cash_account | Cash transactions |
| default_bank_account | Bank transactions |
| default_round_off_account | Rounding adjustments |

### Setting via Python
\`\`\`python
# Get company
company = frappe.get_doc("Company", "My Company Ltd")

# Set default accounts
company.default_receivable_account = "Debtors - MC"
company.default_payable_account = "Creditors - MC"
company.default_income_account = "Sales - MC"
company.default_expense_account = "Cost of Goods Sold - MC"
company.save()
\`\`\`

---

## Cost Centers

For cost allocation and departmental accounting.

### Structure
\`\`\`
My Company Ltd (Root)
├── Operations (Division)
│   ├── Production (Department)
│   └── Quality (Department)
├── Sales (Division)
│   ├── Domestic (Region)
│   └── Export (Region)
└── Administration (Division)
    ├── HR (Department)
    └── Finance (Department)
\`\`\`

### Creating Cost Center
\`\`\`python
cc = frappe.get_doc({
    "doctype": "Cost Center",
    "cost_center_name": "Production",
    "company": "My Company Ltd",
    "parent_cost_center": "Operations - MC"
})
cc.insert()
\`\`\`

---

## Warehouses

Storage locations for inventory.

### Types
- **Stores**: Main storage
- **Finished Goods**: Produced items
- **Raw Materials**: Input materials
- **Work in Progress**: Manufacturing WIP

### Creating Warehouse
\`\`\`python
wh = frappe.get_doc({
    "doctype": "Warehouse",
    "warehouse_name": "Stores",
    "company": "My Company Ltd",
    "account": "Stock Assets - MC"
})
wh.insert()
\`\`\`

---

## Fiscal Year Setup

### Creating Fiscal Year
\`\`\`python
fy = frappe.get_doc({
    "doctype": "Fiscal Year",
    "year": "2024",
    "year_start_date": "2024-01-01",
    "year_end_date": "2024-12-31",
    "company": "My Company Ltd"
})
fy.insert()
\`\`\`

### Fiscal Year Operations
\`\`\`python
# Get current fiscal year
current_fy = frappe.db.get_value("Fiscal Year", 
    {"year_start_date": ["<=", today], "year_end_date": [">=", today]},
    "name"
)

# Check if date is in valid fiscal year
from erpnext.accounts.utils import get_fiscal_year
fy = get_fiscal_year("2024-06-15", company="My Company Ltd")
\`\`\`

---

## Company Abbreviation

Used throughout ERPNext:
- Account names: `Sales - MC`
- Warehouse names: `Stores - MC`
- Cost Center names: `Operations - MC`

### Changing Abbreviation
\`\`\`python
# WARNING: This updates all related records
company = frappe.get_doc("Company", "My Company Ltd")
company.abbr = "NEW"
company.save()  # Triggers abbreviation update
\`\`\`

---

## Multi-Company Setup

### Scenario
Multiple companies in one ERPNext instance.

### Setup
\`\`\`python
# Company 1
company1 = frappe.get_doc({
    "doctype": "Company",
    "company_name": "Company A",
    "abbr": "CA",
    "is_group": 1
}).insert()

# Company 2 (child)
company2 = frappe.get_doc({
    "doctype": "Company",
    "company_name": "Company B",
    "abbr": "CB",
    "parent_company": "Company A"
}).insert()
\`\`\`

---

## Common Issues

### Issue: Accounts Not Created
\`\`\`python
# Recreate chart of accounts
from erpnext.accounts.doctype.account.chart_of_accounts.chart_of_accounts import create_charts
create_charts("My Company Ltd", "Standard")
\`\`\`

### Issue: Default Accounts Missing
\`\`\`python
# Set via Company settings
company = frappe.get_doc("Company", "My Company Ltd")
frappe.db.set_value("Company", company.name, {
    "default_receivable_account": "Debtors - MC",
    "default_payable_account": "Creditors - MC"
})
\`\`\`

---

## Related Topics
- [Installation Setup](./03_installation-setup.md)
- [Accounting](../02_ACCOUNTING/01_chart-of-accounts.md)
