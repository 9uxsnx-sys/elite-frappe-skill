# GL Entry (General Ledger Entry)

## Quick Reference
GL Entry records every financial transaction. Created automatically on document submit. Debit = Credit must always balance. Key fields: account, party, debit, credit, voucher.

## AI Prompt
```
When debugging GL issues:
1. Check debit = credit per voucher
2. Verify account types are correct
3. Check party linking (Customer/Supplier)
4. Validate fiscal year and posting date
5. Trace voucher_no to source document
```

---

## GL Entry Structure

### Key Fields
| Field | Type | Description |
|-------|------|-------------|
| account | Link | Account (with company abbreviation) |
| company | Link | Company |
| posting_date | Date | Transaction date |
| fiscal_year | Link | Fiscal year |
| debit | Currency | Debit amount |
| credit | Currency | Credit amount |
| party_type | Select | Customer/Supplier/Employee |
| party | Dynamic Link | Party reference |
| voucher_type | Link | Source DocType |
| voucher_no | Data | Source document name |
| against | Data | Contra account/party |
| cost_center | Link | Cost center |
| project | Link | Project reference |

---

## GL Entry Creation

### Sales Invoice GL Entries
```
Sales Invoice: SI-001, Customer: ABC Corp, Amount: 10,000 + 1,800 GST = 11,800

GL Entries:
┌────────────────────┬──────────┬────────┬────────┐
│ Account            │ Debit    │ Credit │ Against │
├────────────────────┼──────────┼────────┼─────────┤
│ Debtors - MC       │ 11,800   │ 0      │ Sales   │
│ Sales - MC         │ 0        │ 10,000 │ Customer│
│ GST Output - MC    │ 0        │ 1,800  │ Customer│
└────────────────────┴──────────┴────────┴─────────┘
```

### Purchase Invoice GL Entries
```
Purchase Invoice: PI-001, Supplier: XYZ Ltd, Amount: 5,000 + 900 GST = 5,900

GL Entries:
┌────────────────────┬──────────┬────────┬─────────┐
│ Account            │ Debit    │ Credit │ Against │
├────────────────────┼──────────┼────────┼─────────┤
│ COGS - MC          │ 5,000    │ 0      │ Supplier│
│ GST Input - MC     │ 900      │ 0      │ Supplier│
│ Creditors - MC     │ 0        │ 5,900  │ Expenses│
└────────────────────┴──────────┴────────┴─────────┘
```

### Payment Entry GL Entries
```
Payment Entry: PE-001, Customer: ABC Corp, Amount: 5,000

GL Entries:
┌────────────────────┬──────────┬────────┬─────────┐
│ Account            │ Debit    │ Credit │ Against │
├────────────────────┼──────────┼────────┼─────────┤
│ HDFC Bank - MC     │ 5,000    │ 0      │ Customer│
│ Debtors - MC       │ 0        │ 5,000  │ Bank    │
└────────────────────┴──────────┴────────┴─────────┘
```

---

## Creating GL Entries

### Manual GL Entry (Journal Entry)
```python
je = frappe.get_doc({
    "doctype": "Journal Entry",
    "posting_date": "2024-01-15",
    "accounts": [
        {
            "account": "Cash - MC",
            "debit": 10000,
            "credit": 0
        },
        {
            "account": "Sales - MC",
            "debit": 0,
            "credit": 10000
        }
    ]
})
je.insert()
je.submit()
```

### Programmatic GL Entry
```python
from erpnext.accounts.general_ledger import make_gl_entries

gl_entries = [
    {
        "account": "Debtors - MC",
        "party_type": "Customer",
        "party": "ABC Corp",
        "debit": 10000,
        "credit": 0,
        "against": "Sales - MC",
        "voucher_type": "Sales Invoice",
        "voucher_no": "SI-001",
        "company": "My Company Ltd",
        "posting_date": "2024-01-15"
    },
    {
        "account": "Sales - MC",
        "debit": 0,
        "credit": 10000,
        "against": "ABC Corp",
        "voucher_type": "Sales Invoice",
        "voucher_no": "SI-001",
        "company": "My Company Ltd",
        "posting_date": "2024-01-15"
    }
]

make_gl_entries(gl_entries)
```

---

## Querying GL Entries

### Get GL Entries for Account
```python
entries = frappe.get_all("GL Entry",
    filters={
        "account": "Debtors - MC",
        "docstatus": 1
    },
    fields=["name", "debit", "credit", "posting_date", "voucher_no"],
    order_by="posting_date desc"
)
```

### Get Account Balance
```python
from erpnext.accounts.utils import get_balance_on

# Current balance
balance = get_balance_on("Debtors - MC")

# Balance at date
balance = get_balance_on("Debtors - MC", "2024-01-31")

# With party filter
balance = get_balance_on(
    "Debtors - MC",
    party_type="Customer",
    party="ABC Corp"
)
```

### Get Outstanding for Customer
```python
# Total receivable for customer
total = frappe.db.sql("""
    SELECT SUM(debit) - SUM(credit) as balance
    FROM `tabGL Entry`
    WHERE account = %s
    AND party_type = 'Customer'
    AND party = %s
    AND docstatus = 1
""", ("Debtors - MC", "ABC Corp"))[0][0]
```

---

## Canceling GL Entries

### On Document Cancel
```python
# Called automatically when document is cancelled
from erpnext.accounts.general_ledger import make_gl_entries

def on_cancel(self):
    make_gl_entries(self.get_gl_entries(), cancel=1)
```

### Manual Cancel
```python
# Cancel and reverse GL entries
doc = frappe.get_doc("Sales Invoice", "SI-001")
doc.cancel()
```

---

## Common Issues

### Debit != Credit
```python
# Check if entries balance
entries = frappe.get_all("GL Entry",
    filters={"voucher_no": "SI-001"},
    fields=["debit", "credit"]
)

total_debit = sum(e.debit for e in entries)
total_credit = sum(e.credit for e in entries)

if total_debit != total_credit:
    frappe.throw(f"Not balanced: Debit={total_debit}, Credit={total_credit}")
```

### Missing Party
```python
# Always set party_type and party for receivable/payable accounts
gl_entry = {
    "account": "Debtors - MC",  # Receivable account
    "party_type": "Customer",    # Required
    "party": "ABC Corp",         # Required
    "debit": 10000
}
```

### Wrong Account Type
```python
# Check account type before posting
account_type = frappe.db.get_value("Account", "Debtors - MC", "account_type")

if account_type == "Receivable":
    # Must have party_type and party
    pass
```

---

## Reports

### Trial Balance
```python
def get_trial_balance(company, date=None):
    accounts = frappe.get_all("Account",
        filters={"company": company, "is_group": 0},
        fields=["name", "account_name"]
    )
    
    result = []
    for acc in accounts:
        balance = get_balance_on(acc.name, date)
        if balance != 0:
            result.append({
                "account": acc.name,
                "account_name": acc.account_name,
                "balance": balance
            })
    
    return result
```

### General Ledger Report
```python
def get_general_ledger(account, from_date, to_date):
    return frappe.get_all("GL Entry",
        filters={
            "account": account,
            "posting_date": ["between", [from_date, to_date]],
            "docstatus": 1
        },
        fields=["posting_date", "voucher_type", "voucher_no", 
                "debit", "credit", "against"],
        order_by="posting_date"
    )
```

---

## Related Topics
- [Chart of Accounts](./01_chart-of-accounts.md)
- [Journal Entry](./02_journal-entry.md)
- [Payment Entry](./03_payment-entry.md)
