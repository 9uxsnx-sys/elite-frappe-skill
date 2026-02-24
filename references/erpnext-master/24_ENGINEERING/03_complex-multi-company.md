# Complex Multi-Company Implementation Guide

## Quick Reference
Enterprise-grade guide for implementing ERPNext across multiple companies, subsidiaries, and complex organizational structures.

## AI Prompt
```
When implementing multi-company ERPNext:
1. Design company hierarchy first
2. Plan inter-company transactions
3. Configure consolidated reporting
4. Set up proper role access
5. Test inter-company workflows
```

---

## 1. Company Structure Design

### Hierarchical Structure
```python
# Example: Group Structure in KSA
Parent Company (Holding)
├── Trading Division
│   ├── Trading LLC - Riyadh
│   ├── Trading LLC - Jeddah
│   └── Trading LLC - Dammam
├── Manufacturing Division
│   ├── Manufacturing LLC
│   └── Factory Operations
├── Retail Division
│   ├── Retail Store 1
│   ├── Retail Store 2
│   └── Retail Store N
└── Services Division
    ├── Services LLC
    └── Consulting
```

### Company Setup Configuration
```python
# Parent Company Settings
{
    "company_name": "Al Mutawa Group Holding",
    "abbr": "AMG",
    "default_currency": "SAR",
    "country": "Saudi Arabia",
    "is_group": 1,  # This is a holding company
    "group_company": ""  # No parent
}

# Subsidiary Settings
{
    "company_name": "Trading LLC - Riyadh",
    "abbr": "TLR",
    "default_currency": "SAR",
    "country": "Saudi Arabia",
    "is_group": 0,
    "group_company": "Al Mutawa Group Holding - AMG"
}
```

---

## 2. Inter-Company Transactions

### Setup Inter-Company Transaction
```python
# Enable Inter-Company Transaction
# Go to: Selling Settings > Allow Inter-Company Transaction

# Or via code
selling_settings = frappe.get_doc("Selling Settings")
selling_settings.allow_inter_company_transaction = 1
selling_settings.save()
```

### Inter-Company Transaction Flow
```python
# Company A (Seller) → Company B (Buyer)

# Step 1: Sales Invoice in Company A
invoice = frappe.get_doc({
    "doctype": "Sales Invoice",
    "company": "Trading LLC - Riyadh",
    "customer": "Trading LLC - Jeddah",  # Another company in group
    "inter_company_invoice_reference": "",
    "items": [{
        "item_code": "Product A",
        "qty": 100,
        "rate": 50,
        "company": "Trading LLC - Riyadh"
    }]
})
invoice.insert()
invoice.submit()

# Step 2: Auto-create Purchase Invoice in Company B
# This happens automatically if inter-company settings configured
```

### Custom Inter-Company Workflow
```python
# my_app/utils/intercompany.py

def create_inter_company_transfer(source_company, target_company, items):
    """Create inter-company transfer"""
    
    # Get internal customer (the other company)
    internal_customer = frappe.db.get_value(
        "Customer",
        {"name": ["like", f"%{target_company}%"], "is_internal_customer": 1},
        "name"
    )
    
    # Create Sales Order
    so = frappe.get_doc({
        "doctype": "Sales Order",
        "company": source_company,
        "customer": internal_customer,
        "transaction_type": "Internal Transfer",
        "items": items
    })
    so.insert()
    so.submit()
    
    return so
```

---

## 3. Consolidated Financial Reporting

### Setup Company Consolidation
```python
# In hooks.py for custom consolidation report
def get_consolidated_pnl(companies, from_date, to_date):
    """Get consolidated P&L for all companies"""
    
    all_income = frappe.db.sql("""
        SELECT 
            company,
            SUM(credit) - SUM(debit) as income
        FROM `tabGL Entry`
        WHERE company IN ({})
        AND posting_date BETWEEN %s AND %s
        AND account IN (
            SELECT name FROM `tabAccount` 
            WHERE account_type = 'Income Account'
        )
        GROUP BY company
    """.format(", ".join(["%s"] * len(companies))), 
    companies + [from_date, to_date], as_dict=True)
    
    return all_income
```

### Consolidated Balance Sheet
```python
def generate_consolidated_balance_sheet(companies, as_on_date):
    """Generate balance sheet across all companies"""
    
    # Get all asset accounts
    assets = get_accounts_by_type(companies, "Asset")
    liabilities = get_accounts_by_type(companies, "Liability")
    equity = get_accounts_by_type(companies, "Equity")
    
    # Calculate totals
    total_assets = sum(get_balance(as_on_date, assets))
    total_liabilities = sum(get_balance(as_on_date, liabilities))
    total_equity = sum(get_balance(as_on_date, equity))
    
    return {
        "total_assets": total_assets,
        "total_liabilities": total_liabilities,
        "total_equity": total_equity,
        "check": total_assets - (total_liabilities + total_equity)
    }
```

---

## 4. Cross-Company Permissions

### Role Structure
```python
# Group Level Roles
group_roles = [
    "Group Manager",
    "Group Accountant", 
    "Group Viewer"
]

# Company Specific Roles
company_roles = [
    "Company Manager - TLR",
    "Company Accountant - TLR",
    "Operations Manager - TLR"
]
```

### Permission Configuration
```python
# Set up company-based permissions
def setup_company_permissions():
    """Configure permissions for multi-company access"""
    
    # Group manager sees all
    group_manager = frappe.get_doc("User", "group.manager@company.com")
    for role in ["Group Manager", "Group Accountant"]:
        group_manager.append("roles", {"role": role})
    
    # Company manager sees only their company
    company_manager = frappe.get_doc("User", "tlr.manager@company.com")
    for role in ["Company Manager - TLR"]:
        company_manager.append("roles", {"role": role})
    
    # Add user permission for company
    frappe.get_doc({
        "doctype": "User Permission",
        "user": "tlr.manager@company.com",
        "allow": "Company",
        "for_value": "Trading LLC - Riyadh",
        "apply_to_all_doctypes": 1
    }).insert()
```

### Document Sharing
```python
# Share documents across companies
def share_across_companies(doc, companies, read=1, write=0):
    """Share document with users from other companies"""
    
    users = frappe.get_all(
        "User", 
        filters={"company": ["in", companies]},
        pluck="name"
    )
    
    for user in users:
        frappe.share.add_docshare(
            doc.doctype,
            doc.name,
            user,
            read=read,
            write=write
        )
```

---

## 5. Data Isolation vs Sharing

### Scenario 1: Complete Isolation
```python
# Each company has separate data
# Only group-level users can see all

def isolate_company_data(user):
    """Restrict user to their company only"""
    
    user_permissions = []
    
    # Get user's assigned companies
    companies = get_user_companies(user)
    
    for company in companies:
        user_permissions.append({
            "allow": "Company",
            "for_value": company,
            "apply_to_all_doctypes": 1
        })
    
    return user_permissions
```

### Scenario 2: Selective Sharing
```python
# Some data shared, some isolated
# Example: Shared item master, isolated transactions

def setup_selective_sharing():
    # Items are shared across group
    frappe.share.add_docshare(
        "Item", 
        "Product A",
        user="jeddah.user@company.com",
        read=1, 
        write=1
    )
    
    # But sales are company-specific (no share)
    # Each company has their own Sales Invoice
```

---

## 6. Inventory Across Companies

### Warehouse Structure
```python
# Al Mutawa Group Holding - AMG
# ├── Trading - TLR
# │   ├── Main Warehouse - TLR
# │   ├── Riyadh Store - TLR
# │   └── Jeddah Store - TLR (for inter-company)
# └── Manufacturing - MFG
#     ├── Raw Materials - MFG
#     └── Finished Goods - MFG
```

### Inter-Company Stock Transfer
```python
def create_inter_company_stock_transfer(
    source_company, target_company, items
):
    """Transfer stock between companies"""
    
    # Step 1: Delivery Note (Source Company)
    dn = frappe.get_doc({
        "doctype": "Delivery Note",
        "company": source_company,
        "target_warehouse": "Inter-Company Transit - S",
        "items": items
    })
    dn.insert()
    dn.submit()
    
    # Step 2: Create Purchase Receipt in Target Company
    # (Manual or automated based on workflow)
    pr = frappe.get_doc({
        "doctype": "Purchase Receipt",
        "company": target_company,
        "supplier": source_company,  # Internal supplier
        "items": [{
            "item_code": item.item_code,
            "qty": item.qty,
            "rate": item.rate,
            "warehouse": f"Main Warehouse - {target_company[:3]}"
        } for item in dn.items]
    })
    pr.insert()
    
    return dn, pr
```

---

## 7. Common Pitfalls & Solutions

### Pitfall 1: Circular Transactions
```
Problem: Company A sells to B, B sells to A
Solution: Configure transaction limits and audit trails
```
```python
# Add validation
def validate_inter_company_transaction(doc):
    if doc.is_internal_customer:
        # Check if this would create circular transaction
        existing = frappe.db.exists("Sales Invoice", {
            "customer": doc.company,
            "docstatus": ["!=", 2]
        })
        if existing:
            frappe.throw("Circular inter-company transaction detected")
```

### Pitfall 2: Currency Mismatch
```
Problem: Different companies have different currencies
Solution: Set up proper exchange rates
```
```python
# Configure in Currency Settings
# Go to: Setup > Currency > Exchange Rate
# Add rates for each currency pair
```

### Pitfall 3: Consolidated Report Errors
```
Problem: Balance sheet doesn't balance across companies
Solution: Ensure inter-company accounts are properly eliminated
```
```python
# Use elimination entries
def create_elimination_entry(companies, period):
    """Create elimination entry for inter-company transactions"""
    
    # Get inter-company receivables/payables
    ic_receivables = get_inter_company_amount(companies, "Receivable")
    ic_payables = get_inter_company_amount(companies, "Payable")
    
    elimination = frappe.get_doc({
        "doctype": "Journal Entry",
        "posting_date": period,
        "company": companies[0],  # Parent company
        "accounts": [
            {
                "account": "Inter-Company Receivables - AMG",
                "debit_in_account_currency": ic_receivables
            },
            {
                "account": "Inter-Company Payables - AMG", 
                "credit_in_account_currency": ic_payables
            }
        ]
    })
    elimination.insert()
    elimination.submit()
```

---

## 8. Enterprise Checklist

### Phase 1: Design
- [ ] Map organizational hierarchy
- [ ] Define inter-company transaction types
- [ ] Plan consolidated reporting requirements
- [ ] Define data isolation requirements

### Phase 2: Configuration
- [ ] Set up parent/child company structure
- [ ] Configure Chart of Accounts per company
- [ ] Set up warehouse hierarchy
- [ ] Configure inter-company settings

### Phase 3: Permissions
- [ ] Create role structure
- [ ] Set up user permissions
- [ ] Configure document sharing rules
- [ ] Test access controls

### Phase 4: Transactions
- [ ] Test inter-company sales flow
- [ ] Test stock transfers
- [ ] Validate consolidated reports
- [ ] Test payment flows

### Phase 5: Go-Live
- [ ] Migrate data with company tags
- [ ] Train users on company-specific views
- [ ] Monitor inter-company reconciliation
- [ ] Set up audit procedures

---

## Related Topics
- [Module Design](./02_module-design.md)
- [Implementation Checklist](../25_ELITE_SKILLS/01_implementation-checklist.md)
- [GAP Analysis](../25_ELITE_SKILLS/03_gap-analysis.md)
