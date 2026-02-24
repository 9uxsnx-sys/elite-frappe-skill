# ERPNext Implementation Checklist

## Quick Reference
A comprehensive go-live checklist covering setup, master data, transactions, integrations, and testing. Use this to ensure smooth ERPNext implementation.

## AI Prompt
\`\`\`
When planning ERPNext implementation:
1. Follow checklist phases sequentially
2. Validate each phase before proceeding
3. Document customizations and configurations
4. Plan for data migration and testing
5. Train users before go-live
\`\`\`

---

## Phase 1: Foundation Setup

### 1.1 System Installation
- [ ] Install ERPNext (bench/easy-install/docker)
- [ ] Configure site settings
- [ ] Set up SSL certificate
- [ ] Configure email settings
- [ ] Set up backup schedule
- [ ] Configure background workers

### 1.2 Company Setup
- [ ] Create Company
- [ ] Set company abbreviation
- [ ] Configure default currency
- [ ] Set fiscal year
- [ ] Import/Configure Chart of Accounts
- [ ] Create Cost Centers

### 1.3 Warehouses
- [ ] Create warehouses hierarchy
- [ ] Set default warehouse for items
- [ ] Configure warehouse types
- [ ] Link warehouses to accounts

### 1.4 Users & Roles
- [ ] Create user accounts
- [ ] Assign roles
- [ ] Configure role permissions
- [ ] Set up user defaults (company, warehouse)

---

## Phase 2: Master Data

### 2.1 Customers
- [ ] Import customer list
- [ ] Configure customer groups
- [ ] Set up territories
- [ ] Add customer contacts
- [ ] Configure credit limits
- [ ] Set up customer-specific price lists

### 2.2 Suppliers
- [ ] Import supplier list
- [ ] Configure supplier groups
- [ ] Add supplier contacts
- [ ] Set up payment terms

### 2.3 Items
- [ ] Import item list
- [ ] Configure item groups
- [ ] Set up UOMs
- [ ] Configure item variants (if applicable)
- [ ] Set up item prices
- [ ] Configure tax templates
- [ ] Set default accounts per item

### 2.4 Chart of Accounts
- [ ] Review and customize COA
- [ ] Set default accounts for company
- [ ] Configure tax accounts
- [ ] Set up expense accounts
- [ ] Configure stock accounts

---

## Phase 3: Configuration

### 3.1 Sales Settings
- [ ] Configure selling settings
- [ ] Set default price list
- [ ] Configure sales team/commission
- [ ] Set up naming series
- [ ] Configure sales workflows

### 3.2 Purchase Settings
- [ ] Configure buying settings
- [ ] Set default supplier settings
- [ ] Configure purchase workflows
- [ ] Set up naming series

### 3.3 Stock Settings
- [ ] Configure stock settings
- [ ] Set valuation method
- [ ] Configure negative stock rules
- [ ] Set up serial no/batch settings
- [ ] Configure stock permissions

### 3.4 Accounts Settings
- [ ] Configure accounts settings
- [ ] Set up payment terms
- [ ] Configure tax categories
- [ ] Set up withholding taxes
- [ ] Configure round-off accounts

---

## Phase 4: Opening Balances

### 4.1 Chart of Accounts Opening
- [ ] Enter opening balances for assets
- [ ] Enter opening balances for liabilities
- [ ] Balance equity accounts
- [ ] Verify trial balance matches legacy system

### 4.2 Stock Opening
- [ ] Import opening stock quantities
- [ ] Set opening stock values
- [ ] Reconcile stock with physical count
- [ ] Verify stock valuation report

### 4.3 Party Opening
- [ ] Import customer opening balances (receivables)
- [ ] Import supplier opening balances (payables)
- [ ] Verify against legacy system

---

## Phase 5: Testing

### 5.1 Transaction Testing
- [ ] Test sales flow: Quotation → Order → Invoice
- [ ] Test purchase flow: PO → Receipt → Invoice
- [ ] Test stock entry types
- [ ] Test payment entry
- [ ] Test journal entry
- [ ] Verify GL entries are correct

### 5.2 Report Testing
- [ ] Test financial statements (P&L, Balance Sheet)
- [ ] Test stock reports
- [ ] Test sales reports
- [ ] Test purchase reports
- [ ] Verify calculations are correct

### 5.3 Integration Testing
- [ ] Test email notifications
- [ ] Test payment gateway (if applicable)
- [ ] Test external integrations
- [ ] Test webhooks

---

## Phase 6: Customization

### 6.1 Custom Fields
- [ ] Add required custom fields
- [ ] Configure field properties
- [ ] Export fixtures for version control

### 6.2 Custom Scripts
- [ ] Implement client scripts
- [ ] Implement server scripts
- [ ] Test custom validations

### 6.3 Workflows
- [ ] Configure approval workflows
- [ ] Set up notification rules
- [ ] Test workflow transitions

### 6.4 Print Formats
- [ ] Create custom print formats
- [ ] Configure standard print formats
- [ ] Test PDF generation

---

## Phase 7: Training & Go-Live

### 7.1 User Training
- [ ] Train admin users
- [ ] Train sales team
- [ ] Train purchase team
- [ ] Train accounts team
- [ ] Train warehouse team
- [ ] Create user guides

### 7.2 Pre Go-Live
- [ ] Final data reconciliation
- [ ] Clear test transactions
- [ ] Reset sequences (if needed)
- [ ] Final backup
- [ ] Notify users

### 7.3 Post Go-Live
- [ ] Monitor error logs
- [ ] Support users
- [ ] Address issues
- [ ] Document learnings

---

## Quick Verification Scripts

### Check Master Data Count
\`\`\`python
# Run in bench console
counts = {
    "Customers": frappe.db.count("Customer"),
    "Suppliers": frappe.db.count("Supplier"),
    "Items": frappe.db.count("Item"),
    "Accounts": frappe.db.count("Account", {"is_group": 0}),
    "Warehouses": frappe.db.count("Warehouse")
}
for k, v in counts.items():
    print(f"{k}: {v}")
\`\`\`

### Check Opening Balances
\`\`\`python
from erpnext.accounts.utils import get_balance_on

# Check GL balances
accounts = frappe.get_all("Account", filters={"is_group": 0}, fields=["name"])
for acc in accounts:
    balance = get_balance_on(acc.name)
    if balance != 0:
        print(f"{acc.name}: {balance}")
\`\`\`

### Check Stock Balance
\`\`\`python
from erpnext.stock.utils import get_stock_balance

items = frappe.get_all("Item", filters={"is_stock_item": 1}, fields=["name", "item_name"])
for item in items:
    balance = get_stock_balance(item.name)
    if balance != 0:
        print(f"{item.item_name}: {balance}")
\`\`\`

---

## Related Topics
- [Gap Analysis](./03_gap-analysis.md)
- [User Training](./04_user-training.md)
- [Upgrade Guide](./06_upgrade-guide.md)
