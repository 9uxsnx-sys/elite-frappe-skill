# Journal Entry

## Quick Reference
Journal Entry creates manual accounting entries. Use for adjustments, opening balances, and non-standard transactions. Must balance (debit = credit).

## AI Prompt
```
When creating journal entries:
1. Ensure debit = credit
2. Set correct accounts and parties
3. Use for adjustments only
4. Add reference for audit trail
5. Check fiscal year validity
```

---

## Journal Entry DocType

### Key Fields
| Field | Type | Description |
|-------|------|-------------|
| posting_date | Date | Entry date |
| accounts | Table | Debit/Credit accounts |
| user_remark | Text | Description |
| voucher_type | Select | Journal Entry/Opening Entry/etc |

### Voucher Types
- Journal Entry
- Opening Entry
- Depreciation Entry
- Credit Note
- Debit Note
- Exchange Rate Revaluation

---

## Creating Journal Entry

### Basic Entry
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
    ],
    "user_remark": "Cash sales entry"
})
je.insert()
je.submit()
```

### With Party
```python
je = frappe.get_doc({
    "doctype": "Journal Entry",
    "posting_date": "2024-01-15",
    "accounts": [
        {
            "account": "Debtors - MC",
            "party_type": "Customer",
            "party": "ABC Corp",
            "debit": 5000,
            "credit": 0
        },
        {
            "account": "Sales - MC",
            "debit": 0,
            "credit": 5000
        }
    ]
})
je.insert()
je.submit()
```

### Opening Entry
```python
je = frappe.get_doc({
    "doctype": "Journal Entry",
    "voucher_type": "Opening Entry",
    "posting_date": "2024-01-01",
    "accounts": [
        {"account": "Cash - MC", "debit": 50000},
        {"account": "Bank - MC", "debit": 100000},
        {"account": "Capital - MC", "credit": 150000}
    ]
})
je.insert()
je.submit()
```

---

## Validation

### Check Balance
```python
def validate_balance(je):
    total_debit = sum(acc.debit for acc in je.accounts)
    total_credit = sum(acc.credit for acc in je.accounts)
    
    if total_debit != total_credit:
        frappe.throw(f"Entry not balanced: Dr={total_debit}, Cr={total_credit}")
```

---

## Related Topics
- [Chart of Accounts](./01_chart-of-accounts.md)
- [GL Entry](./04_gl-entry.md)
