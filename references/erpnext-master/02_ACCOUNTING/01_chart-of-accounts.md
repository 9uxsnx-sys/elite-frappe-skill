# Chart of Accounts

## Quick Reference
Chart of Accounts is a hierarchical list of all accounts. Root types: Asset, Liability, Equity, Income, Expense. Each account is tagged with type for automatic posting.

## AI Prompt
\`\`\`
When designing chart of accounts:
1. Follow standard accounting principles
2. Create logical hierarchy for reporting
3. Use correct account types for auto-posting
4. Keep company abbreviation in account names
5. Separate accounts by cost center if needed
\`\`\`

---

## Account DocType

### Key Fields
| Field | Type | Description |
|-------|------|-------------|
| account_name | Data | Account name |
| company | Link | Company |
| parent_account | Link | Parent in hierarchy |
| account_type | Select | Account category |
| root_type | Select | Root category |
| is_group | Check | Has children |
| account_number | Data | Optional number |

### Root Types
| Root Type | Accounts |
|-----------|----------|
| Asset | Cash, Bank, Receivables, Fixed Assets |
| Liability | Payables, Loans, Tax Payable |
| Equity | Capital, Retained Earnings |
| Income | Sales, Other Income |
| Expense | COGS, Operating Expenses |

### Account Types
| Account Type | Auto Behavior |
|--------------|---------------|
| Receivable | Auto-set on Customer creation |
| Payable | Auto-set on Supplier creation |
| Bank | Bank transactions |
| Cash | Cash transactions |
| Stock | Inventory valuation |
| Cost of Goods Sold | Stock transactions |
| Fixed Asset | Asset transactions |

---

## Standard Chart Structure

\`\`\`
Application of Funds (Assets)
├── Current Assets
│   ├── Cash In Hand
│   │   └── Cash - MC
│   ├── Bank Accounts
│   │   └── HDFC Bank - MC
│   ├── Debtors
│   │   └── Debtors - MC
│   └── Stock Assets
│       └── Stock - MC
├── Fixed Assets
│   └── Fixed Assets - MC
│
Source of Funds (Liabilities)
├── Current Liabilities
│   ├── Creditors
│   │   └── Creditors - MC
│   └── Duties and Taxes
│       └── GST Payable - MC
├── Loans (Liabilities)
│
Equity
├── Capital Stock
├── Reserves and Surplus
│
Income
├── Direct Income
│   └── Sales - MC
├── Indirect Income
│
Expense
├── Direct Expenses
│   └── Cost of Goods Sold - MC
├── Indirect Expenses
│   ├── Administrative Expenses
│   └── Selling Expenses
\`\`\`

---

## Creating Accounts

### Root Account
\`\`\`python
root = frappe.get_doc({
    "doctype": "Account",
    "account_name": "Application of Funds",
    "company": "My Company Ltd",
    "root_type": "Asset",
    "is_group": 1
})
root.insert()
\`\`\`

### Child Account
\`\`\`python
account = frappe.get_doc({
    "doctype": "Account",
    "account_name": "HDFC Bank",
    "company": "My Company Ltd",
    "parent_account": "Bank Accounts - MC",
    "account_type": "Bank",
    "root_type": "Asset"
})
account.insert()
\`\`\`

### Creating Full Hierarchy
\`\`\`python
def create_chart_of_accounts(company):
    accounts = [
        {"name": "Current Assets", "parent": None, "root_type": "Asset", "is_group": 1},
        {"name": "Cash In Hand", "parent": "Current Assets", "root_type": "Asset", "is_group": 1},
        {"name": "Cash", "parent": "Cash In Hand", "root_type": "Asset", "account_type": "Cash"},
        {"name": "Bank Accounts", "parent": "Current Assets", "root_type": "Asset", "is_group": 1},
        {"name": "HDFC Bank", "parent": "Bank Accounts", "root_type": "Asset", "account_type": "Bank"},
    ]
    
    for acc in accounts:
        doc = frappe.get_doc({
            "doctype": "Account",
            "account_name": acc["name"],
            "company": company,
            "parent_account": acc.get("parent") + " - MC" if acc.get("parent") else None,
            "root_type": acc["root_type"],
            "is_group": acc.get("is_group", 0),
            "account_type": acc.get("account_type")
        })
        doc.insert()
\`\`\`

---

## Default Accounts

### Setting Company Defaults
\`\`\`python
company = frappe.get_doc("Company", "My Company Ltd")

# Set default accounts
company.default_receivable_account = "Debtors - MC"
company.default_payable_account = "Creditors - MC"
company.default_cash_account = "Cash - MC"
company.default_bank_account = "HDFC Bank - MC"
company.default_income_account = "Sales - MC"
company.default_expense_account = "Cost of Goods Sold - MC"
company.default_round_off_account = "Round Off - MC"
company.write_off_account = "Write Off - MC"
company.save()
\`\`\`

### Item Default Accounts
\`\`\`python
item = frappe.get_doc("Item", "LAPTOP-001")
item.item_defaults = [{
    "company": "My Company Ltd",
    "income_account": "Sales - MC",
    "expense_account": "Cost of Goods Sold - MC"
}]
item.save()
\`\`\`

---

## Account Balance

### Get Balance
\`\`\`python
from erpnext.accounts.utils import get_balance_on

# Current balance
balance = get_balance_on("Debtors - MC")

# Balance at date
balance = get_balance_on("Debtors - MC", "2024-01-31")

# Account with party filter
balance = get_balance_on(
    "Debtors - MC",
    party_type="Customer",
    party="ABC Corp"
)
\`\`\`

### Get GL Entries
\`\`\`python
entries = frappe.get_all("GL Entry",
    filters={"account": "Debtors - MC", "docstatus": 1},
    fields=["name", "debit", "credit", "posting_date", "voucher_no"],
    order_by="posting_date desc"
)
\`\`\`

---

## GL Entry Structure

### Debit Entry
\`\`\`python
{
    "doctype": "GL Entry",
    "account": "Debtors - MC",
    "party_type": "Customer",
    "party": "ABC Corp",
    "debit": 1000,
    "credit": 0,
    "against": "Sales - MC",
    "voucher_type": "Sales Invoice",
    "voucher_no": "SI-001",
    "company": "My Company Ltd",
    "posting_date": "2024-01-15"
}
\`\`\`

### Credit Entry
\`\`\`python
{
    "doctype": "GL Entry",
    "account": "Sales - MC",
    "debit": 0,
    "credit": 1000,
    "against": "Debtors - MC",
    "voucher_type": "Sales Invoice",
    "voucher_no": "SI-001",
    "company": "My Company Ltd",
    "posting_date": "2024-01-15"
}
\`\`\`

---

## Common Patterns

### Get Trial Balance
\`\`\`python
def get_trial_balance(company, date=None):
    accounts = frappe.get_all("Account",
        filters={"company": company, "is_group": 0},
        fields=["name", "account_name", "root_type"]
    )
    
    trial_balance = []
    for acc in accounts:
        balance = get_balance_on(acc.name, date)
        if balance != 0:
            trial_balance.append({
                "account": acc.name,
                "account_name": acc.account_name,
                "root_type": acc.root_type,
                "balance": balance
            })
    
    return trial_balance
\`\`\`

### Reconcile Account
\`\`\`python
def reconcile_account(account):
    total_debit = frappe.db.sql("""
        SELECT SUM(debit) FROM `tabGL Entry`
        WHERE account = %s AND docstatus = 1
    """, (account,))[0][0] or 0
    
    total_credit = frappe.db.sql("""
        SELECT SUM(credit) FROM `tabGL Entry`
        WHERE account = %s AND docstatus = 1
    """, (account,))[0][0] or 0
    
    return total_debit - total_credit
\`\`\`

---

## Common Issues

### Issue: Account Not Found
\`\`\`python
# Check if account exists
if not frappe.db.exists("Account", "Sales - MC"):
    account = frappe.get_doc({
        "doctype": "Account",
        "account_name": "Sales",
        "company": "My Company Ltd",
        "parent_account": "Direct Income - MC",
        "root_type": "Income"
    })
    account.insert()
\`\`\`

### Issue: GL Entry Not Balancing
\`\`\`python
# Check totals
total_debit = sum(entry.debit for entry in gl_entries)
total_credit = sum(entry.credit for entry in gl_entries)

if total_debit != total_credit:
    frappe.throw(f"GL Entry not balancing: Debit={total_debit}, Credit={total_credit}")
\`\`\`

---

## Related Topics
- [Journal Entry](./02_journal-entry.md)
- [Payment Entry](./03_payment-entry.md)
- [GL Entry](./04_gl-entry.md)
