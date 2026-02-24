# Party Master (Customer, Supplier, Lead)

## Quick Reference
Parties are entities you do business with. Customer = buyers, Supplier = vendors, Lead = potential customers. All have addresses, contacts, credit limits, and group hierarchies.

## AI Prompt
\`\`\`
When working with parties:
1. Check party exists before creating transactions
2. Validate credit limits before sales
3. Ensure default accounts are set
4. Link addresses and contacts properly
5. Handle party groups for reporting
\`\`\`

---

## Customer DocType

### Key Fields
| Field | Type | Description |
|-------|------|-------------|
| customer_name | Data | Name of customer |
| customer_type | Select | Company/Individual |
| customer_group | Link | Group categorization |
| territory | Link | Geographic territory |
| credit_limit | Currency | Max credit allowed |
| default_price_list | Link | Default pricing |
| default_currency | Link | Default currency |

### Creating Customer
\`\`\`python
customer = frappe.get_doc({
    "doctype": "Customer",
    "customer_name": "ABC Corp",
    "customer_type": "Company",
    "customer_group": "Commercial",
    "territory": "India",
    "credit_limit": 100000,
    "default_currency": "INR"
})
customer.insert()
\`\`\`

### Customer API
\`\`\`python
# Get customer
customer = frappe.get_doc("Customer", "ABC Corp")

# Get customer details
details = frappe.db.get_value("Customer", "ABC Corp", 
    ["customer_name", "credit_limit", "customer_group"], as_dict=True)

# Get outstanding amount
from erpnext.accounts.utils import get_balance_on
outstanding = get_balance_on(
    account="Debtors - MC",
    party_type="Customer",
    party="ABC Corp"
)

# Get total sales
total = frappe.db.sql("""
    SELECT SUM(grand_total) 
    FROM `tabSales Invoice` 
    WHERE customer = %s AND docstatus = 1
""", ("ABC Corp",))[0][0]
\`\`\`

---

## Supplier DocType

### Key Fields
| Field | Type | Description |
|-------|------|-------------|
| supplier_name | Data | Name of supplier |
| supplier_type | Select | Company/Individual |
| supplier_group | Link | Group categorization |
| country | Link | Country |
| default_currency | Link | Default currency |
| payment_terms | Link | Payment terms |

### Creating Supplier
\`\`\`python
supplier = frappe.get_doc({
    "doctype": "Supplier",
    "supplier_name": "XYZ Ltd",
    "supplier_type": "Company",
    "supplier_group": "Local",
    "country": "India",
    "default_currency": "INR"
})
supplier.insert()
\`\`\`

### Supplier API
\`\`\`python
# Get supplier
supplier = frappe.get_doc("Supplier", "XYZ Ltd")

# Get purchase history
total = frappe.db.sql("""
    SELECT SUM(grand_total) 
    FROM `tabPurchase Invoice` 
    WHERE supplier = %s AND docstatus = 1
""", ("XYZ Ltd",))[0][0]

# Get outstanding
outstanding = get_balance_on(
    account="Creditors - MC",
    party_type="Supplier",
    party="XYZ Ltd"
)
\`\`\`

---

## Lead DocType

### Key Fields
| Field | Type | Description |
|-------|------|-------------|
| lead_name | Data | Name of lead |
| source | Link | Lead source |
| status | Select | Lead status |
| company_name | Data | Company name |
| email_id | Data | Email |
| mobile_no | Data | Mobile number |

### Lead Status Values
- Lead
- Open
- Replied
- Opportunity
- Quotation
- Lost
- Interested
- Converted

### Creating Lead
\`\`\`python
lead = frappe.get_doc({
    "doctype": "Lead",
    "lead_name": "John Doe",
    "source": "Website",
    "status": "Lead",
    "email_id": "john@example.com",
    "mobile_no": "+1234567890"
})
lead.insert()
\`\`\`

### Converting Lead to Customer
\`\`\`python
lead = frappe.get_doc("Lead", "LEAD-001")
customer = lead.make_customer()
customer.customer_group = "Commercial"
customer.territory = "India"
customer.insert()

# Update lead status
lead.status = "Converted"
lead.customer = customer.name
lead.save()
\`\`\`

### Lead to Opportunity
\`\`\`python
lead = frappe.get_doc("Lead", "LEAD-001")
opportunity = lead.make_opportunity()
opportunity.insert()
\`\`\`

---

## Address & Contact

### Address DocType
\`\`\`python
address = frappe.get_doc({
    "doctype": "Address",
    "address_title": "ABC Corp Office",
    "address_type": "Office",
    "address_line1": "123 Main Street",
    "city": "Mumbai",
    "state": "Maharashtra",
    "country": "India",
    "pincode": "400001",
    "links": [{
        "link_doctype": "Customer",
        "link_name": "ABC Corp"
    }]
})
address.insert()
\`\`\`

### Contact DocType
\`\`\`python
contact = frappe.get_doc({
    "doctype": "Contact",
    "first_name": "John",
    "last_name": "Doe",
    "email_ids": [{
        "email_id": "john@abccorp.com",
        "is_primary": 1
    }],
    "phone_nos": [{
        "phone": "+1234567890",
        "is_primary_phone": 1
    }],
    "links": [{
        "link_doctype": "Customer",
        "link_name": "ABC Corp"
    }]
})
contact.insert()
\`\`\`

### Getting Party Address/Contact
\`\`\`python
# Get primary address
address = frappe.db.get_value("Address", 
    {"links": ["link_doctype", "Customer", "link_name", "ABC Corp"], 
     "is_primary_address": 1},
    "name"
)

# Get primary contact
contact = frappe.db.get_value("Contact",
    {"links": ["link_doctype", "Customer", "link_name", "ABC Corp"],
     "is_primary_contact": 1},
    "name"
)

# Using ERPNext utility
from erpnext.accounts.party import get_party_shipping_address
shipping_address = get_party_shipping_address("Customer", "ABC Corp")
\`\`\`

---

## Customer/Supplier Groups

### Creating Groups
\`\`\`python
group = frappe.get_doc({
    "doctype": "Customer Group",
    "customer_group_name": "Wholesale",
    "parent_customer_group": "All Customer Groups"
})
group.insert()
\`\`\`

### Group Hierarchy
\`\`\`
All Customer Groups
├── Individual
├── Commercial
│   ├── Wholesale
│   └── Retail
└── Government
\`\`\`

---

## Credit Management

### Checking Credit Limit
\`\`\`python
from erpnext.selling.doctype.customer.customer import check_credit_limit

# Check before creating Sales Invoice
check_credit_limit("ABC Corp", "My Company Ltd")

# Get credit info
customer = frappe.get_doc("Customer", "ABC Corp")
credit_limit = customer.credit_limit
outstanding = get_balance_on("Debtors - MC", party="ABC Corp")
available_credit = credit_limit - outstanding
\`\`\`

### Setting Credit Limit
\`\`\`python
# At customer level
customer = frappe.get_doc("Customer", "ABC Corp")
customer.credit_limit = 500000
customer.save()

# At company level (default)
company = frappe.get_doc("Company", "My Company Ltd")
company.credit_limit = 1000000
company.save()
\`\`\`

---

## Common Patterns

### Get or Create Customer
\`\`\`python
def get_or_create_customer(customer_name):
    exists = frappe.db.exists("Customer", customer_name)
    if exists:
        return frappe.get_doc("Customer", customer_name)
    
    customer = frappe.get_doc({
        "doctype": "Customer",
        "customer_name": customer_name,
        "customer_type": "Company",
        "customer_group": frappe.db.get_single_value("Selling Settings", "customer_group"),
        "territory": frappe.db.get_single_value("Selling Settings", "territory")
    })
    customer.insert()
    return customer
\`\`\`

### Bulk Customer Import
\`\`\`python
import csv

with open('customers.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if not frappe.db.exists("Customer", row['name']):
            customer = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": row['name'],
                "customer_type": row.get('type', 'Company'),
                "customer_group": row.get('group', 'All Customer Groups'),
                "territory": row.get('territory', 'All Territories')
            })
            customer.insert()
\`\`\`

---

## Related Topics
- [Address Contact](./04_address-contact.md)
- [Sales Invoice](../03_SALES/04_sales-invoice.md)
- [CRM Lead](../07_CRM/01_lead.md)
