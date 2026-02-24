# Tax Setup & Compliance

Comprehensive guide to configuring taxes in ERPNext for global compliance. Covers VAT, GST, sales tax, withholding tax, and regional tax requirements.

---

## 1. Tax Architecture Overview

### Tax Types in ERPNext

```
┌─────────────────────────────────────────────────────────────┐
│                    TAX TYPES IN ERPNEXT                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  DIRECT TAXES              │  INDIRECT TAXES               │
│  ─────────────────        │  ────────────────              │
│  • Corporate Income Tax   │  • VAT/GST (Output/Input)      │
│  • Withholding Tax        │  • Sales Tax                   │
│  • TDS                    │  • Excise Duty                 │
│  • Capital Gains         │  • Customs Duty                │
│                            │  • Service Tax                 │
│                            │  • Reverse Charge             │
│                                                             │
│  configured via:           │  configured via:               │
│  Tax Withholding          │  Tax Templates                 │
│  Category                 │  Item Tax Templates            │
│                            │  Tax Categories               │
└─────────────────────────────────────────────────────────────┘
```

### Tax Configuration Flow

```python
TAX_CONFIGURATION_FLOW = {
    "step_1": {
        "task": "Create Tax Accounts in COA",
        "location": "Chart of Accounts > Duties and Taxes",
        "required": True
    },
    "step_2": {
        "task": "Define Tax Categories",
        "location": "Tax Category list",
        "required": False,
        "purpose": "Different tax rates per customer/item"
    },
    "step_3": {
        "task": "Create Item Tax Templates",
        "location": "Item Tax Template",
        "required": True,
        "purpose": "Tax rates per item or item group"
    },
    "step_4": {
        "task": "Create Sales/Purchase Tax Templates",
        "location": "Sales Taxes and Charges Template",
        "required": True,
        "purpose": "Default tax for transactions"
    },
    "step_5": {
        "task": "Configure Tax Settings",
        "location": "Accounts Settings",
        "required": True,
        "options": ["Validate tax template", "Round tax amount"]
    },
    "step_6": {
        "task": "Set Tax Category in Customer/Supplier",
        "location": "Customer/Supplier doctype",
        "required": False,
        "purpose": "Auto-apply specific tax"
    }
}
```

---

## 2. Regional Tax Configuration

### KSA (Saudi Arabia) - VAT

```python
# KSA VAT Configuration

def setup_ksa_vat():
    """Configure KSA VAT 15%."""
    
    # Step 1: Create Tax Accounts
    tax_accounts = [
        {"account_name": "VAT Output - 15%", "account_type": "Tax"},
        {"account_name": "VAT Input - 15%", "account_type": "Tax"},
        {"account_name": "VAT Suspense", "account_type": "Tax"}
    ]
    
    # Step 2: Create Sales Tax Template
    sales_vat_template = {
        "doctype": "Sales Taxes and Charges Template",
        "title": "KSA VAT 15%",
        "company": "_Test Company",
        "taxes": [
            {
                "charge_type": "On Net Total",
                "account_head": "VAT Output - 15% - _TC",
                "rate": 15,
                "cost_center": "Main - _TC",
                "description": "KSA VAT 15%"
            }
        ]
    }
    
    # Step 3: Create Purchase Tax Template
    purchase_vat_template = {
        "doctype": "Purchase Taxes and Charges Template",
        "title": "KSA VAT 15% - Input",
        "company": "_Test Company",
        "taxes": [
            {
                "charge_type": "On Net Total",
                "account_head": "VAT Input - 15% - _TC",
                "rate": 15,
                "cost_center": "Main - _TC"
            }
        ]
    }
    
    # Step 4: Create Item Tax Templates for different rates
    item_tax_rates = {
        "KSA VAT 0%": [
            {"tax_type": "VAT Output - 0%", "tax_rate": 0}
        ],
        "KSA VAT 5%": [
            {"tax_type": "VAT Output - 15%", "tax_rate": 5}
        ],
        "KSA VAT 15%": [
            {"tax_type": "VAT Output - 15%", "tax_rate": 15}
        ]
    }
    
    return {
        "accounts": tax_accounts,
        "sales_template": sales_vat_template,
        "purchase_template": purchase_vat_template,
        "item_taxes": item_tax_rates
    }
```

### UAE - VAT 5%

```python
# UAE VAT Configuration

UAE_VAT_CONFIG = {
    "standard_rate": 5,
    "zero_rated": 0,
    "exempt": -1,
    "accounts": {
        "output_vat_5": "VAT Output 5% - AC",
        "input_vat_5": "VAT Input 5% - AC",
        "vat_recoverable": "VAT Recoverable - AC",
        "vat_liability": "VAT Liability - AC"
    },
    "tax_templates": {
        "sales": {
            "title": "UAE VAT 5%",
            "taxes": [
                {
                    "charge_type": "On Net Total",
                    "account_head": "VAT Output 5% - AC",
                    "rate": 5,
                    "description": "UAE VAT - Standard Rate"
                }
            ]
        },
        "purchase": {
            "title": "UAE VAT 5% - Input",
            "taxes": [
                {
                    "charge_type": "On Net Total",
                    "account_head": "VAT Input 5% - AC",
                    "rate": 5
                }
            ]
        }
    },
    "tax_categories": [
        {"name": "UAE Standard Rated", "tax_rate": 5},
        {"name": "UAE Zero Rated", "tax_rate": 0},
        {"name": "UAE Exempt", "tax_rate": 0, "is_exempt": 1}
    ]
}
```

### EU - VAT MOSS

```python
# EU VAT MOSS Configuration

EU_VAT_RATES = {
    "Austria": 20,
    "Belgium": 21,
    "Bulgaria": 20,
    "Croatia": 25,
    "Cyprus": 19,
    "Czech Republic": 21,
    "Denmark": 25,
    "Estonia": 22,
    "Finland": 24,
    "France": 20,
    "Germany": 19,
    "Greece": 24,
    "Hungary": 27,
    "Ireland": 23,
    "Italy": 22,
    "Latvia": 21,
    "Lithuania": 21,
    "Luxembourg": 17,
    "Malta": 18,
    "Netherlands": 21,
    "Poland": 23,
    "Portugal": 23,
    "Romania": 19,
    "Slovakia": 20,
    "Slovenia": 22,
    "Spain": 21,
    "Sweden": 25
}

def setup_eu_vat_moss(company):
    """Configure EU VAT MOSS for digital services."""
    
    # Create one template per country
    templates = []
    
    for country, rate in EU_VAT_RATES.items():
        template = frappe.get_doc({
            "doctype": "Sales Taxes and Charges Template",
            "title": f"EU VAT {rate}% - {country}",
            "company": company,
            "taxes": [
                {
                    "charge_type": "On Net Total",
                    "account_head": f"VAT Output {rate}% - {company}",
                    "rate": rate,
                    "cost_center": f"Main - {company}",
                    "description": f"EU VAT {rate}% - {country}"
                }
            ]
        })
        templates.append(template)
    
    return templates

# VAT MOSS Special Configuration
VAT_MOSS_CONFIG = {
    "required_for": "B2C digital services to EU consumers",
    "registration": "One registration for all EU countries",
    "rates": "Based on consumer country",
    "quarterly_filing": "MOSS return required",
    "mini_one_stop_shop": True
}
```

### India - GST

```python
# India GST Configuration

GST_TAX_RATES = {
    "nil": 0,
    "0.25": 0.25,
    "3": 3,
    "5": 5,
    "12": 12,
    "18": 18,
    "28": 28
}

GST_TAX_TYPES = {
    "igst": "Integrated GST",
    "cgst": "Central GST",
    "sgst": "State GST",
    "cess": "GST CESS"
}

def setup_india_gst(company):
    """Configure India GST."""
    
    # Create GST Accounts
    gst_accounts = [
        f"IGST Output - {company}",
        f"IGST Input - {company}",
        f"CGST Output - {company}",
        f"CGST Input - {company}",
        f"SGST Output - {company}",
        f"SGST Input - {company}",
        f"CESS Output - {company}",
        f"CESS Input - {company}"
    ]
    
    # Create GST Tax Templates for interstate
    igst_template = {
        "title": "GST 18% - Inter State",
        "taxes": [
            {
                "charge_type": "On Net Total",
                "account_head": f"IGST Output - {company}",
                "rate": 18,
                "tax_collection_account": f"IGST Output - {company}"
            }
        ]
    }
    
    # Create GST Tax Templates for intrastate
    intra_state_template = {
        "title": "GST 18% - Intra State",
        "taxes": [
            {
                "charge_type": "On Net Total",
                "account_head": f"CGST Output - {company}",
                "rate": 9
            },
            {
                "charge_type": "On Net Total",
                "account_head": f"SGST Output - {company}",
                "rate": 9
            }
        ]
    }
    
    # GST Calculation Method
    return {
        "igst": igst_template,
        "intra_state": intra_state_template,
        "hsn_codes_required": True,
        "gstin_required": True,
        "e_waybill_enabled": True
    }
```

### UK - VAT

```python
# UK VAT Configuration

UK_VAT_RATES = {
    "standard": 20,
    "reduced": 5,
    "zero": 0
}

UK_VAT_CONFIG = {
    "rates": UK_VAT_RATES,
    "accounts": {
        "vat_output_standard": "VAT Output 20% - AC",
        "vat_input_standard": "VAT Input 20% - AC",
        "vat_output_reduced": "VAT Output 5% - AC",
        "vat_input_reduced": "VAT Input 5% - AC",
        "vat_output_zero": "VAT Output 0% - AC",
        "vat_input_zero": "VAT Input 0% - AC"
    },
    "mtd": {
        "enabled": True,
        "requirements": "Quarterly digital reporting",
        "api_integration": "HMRC Making Tax Digital"
    },
    "flat_rate_scheme": {
        "available": True,
        "rates": {
            "consultancy": 14.5,
            "retailing_food": 4,
            "retailing_other": 7.5,
            "construction": 5.5
        }
    }
}
```

---

## 3. Withholding Tax Configuration

```python
# Withholding Tax Setup

def setup_withholding_tax():
    """Configure withholding tax."""
    
    # Step 1: Create Tax Withholding Category
    tds_category = frappe.get_doc({
        "doctype": "Tax Withholding Category",
        "name": "TDS - Contractor",
        "category_name": "Tax Deducted at Source - Contractor",
        "rate": 10,
        "threshold": 30000,
        "from_date": "2024-04-01",
        "to_date": "2025-03-31"
    })
    
    # Step 2: Create accounts
    withholding_accounts = [
        {"account_name": "TDS Payable - AC", "account_type": "Tax"},
        {"account_name": "TDS Receivable - AC", "account_type": "Tax"}
    ]
    
    # Step 3: Apply to supplier
    # In Supplier doctype, set:
    # - tax_withholding_category: "TDS - Contractor"
    # This will auto-calculate TDS on purchase invoices
    
    return tds_category

# Common Withholding Tax Scenarios
WITHHOLDING_TAX_SCENARIOS = {
    "india": {
        "tds_contractor": {"rate": 10, "section": "194C"},
        "tds_professional": {"rate": 10, "section": "194J"},
        "tds_rent": {"rate": 5, "section": "194I"},
        "tds_interest": {"rate": 10, "section": "194A"}
    },
    "usa": {
        "backup_withholding": {"rate": 24, "form": "W-2/1099"},
        "nra_withholding": {"rate": 30, "form": "1042"}
    },
    "europe": {
        "reverse_charge": {"mechanism": "VAT reverse charge"},
        "splits": {"mechanism": "VAT split payment"}
    }
}
```

---

## 4. Tax Validation & Compliance

### Tax Validation Rules

```python
TAX_VALIDATION_RULES = {
    "required_checks": [
        {
            "rule": "Tax account exists",
            "check": "Account is linked in tax template",
            "severity": "CRITICAL"
        },
        {
            "rule": "Tax rate valid",
            "check": "Rate is between 0-100",
            "severity": "CRITICAL"
        },
        {
            "rule": "Tax category set",
            "check": "Customer/supplier has tax category",
            "severity": "HIGH"
        },
        {
            "rule": "HST/GST number valid",
            "check": "Format matches country requirements",
            "severity": "HIGH"
        },
        {
            "rule": "Tax calculation correct",
            "check": "Tax = Base Amount × Rate",
            "severity": "HIGH"
        },
        {
            "rule": "Tax reversal eligible",
            "check": "Input tax can be claimed",
            "severity": "MEDIUM"
        }
    ],
    "compliance_checks": [
        {
            "country": "KSA",
            "requirement": "ZATCA e-invoicing",
            "fields_required": ["qr_code", "invoice_hash", "uuid"]
        },
        {
            "country": "UAE", 
            "requirement": "FTA e-invoicing",
            "fields_required": ["tax_number", "issuer_details", "qr_code"]
        },
        {
            "country": "EU",
            "requirement": "VAT MOSS",
            "fields_required": ["customer_country", "vat_number"]
        },
        {
            "country": "India",
            "requirement": "GST e-invoice",
            "fields_required": ["gstin", "hsn_code", "place_of_supply"]
        }
    ]
}
```

### Tax Report Generation

```python
# Tax Summary Report

def generate_tax_summary(company, from_date, to_date):
    """Generate tax liability summary."""
    
    # Get all sales invoices in period
    sales_invoices = frappe.get_all(
        "Sales Invoice",
        filters={
            "company": company,
            "posting_date": ["between", [from_date, to_date]],
            "docstatus": 1
        },
        fields=["name", "total", "total_taxes_and_charges", "base_total_taxes_and_charges"]
    )
    
    # Get all purchase invoices
    purchase_invoices = frappe.get_all(
        "Purchase Invoice",
        filters={
            "company": company,
            "posting_date": ["between", [from_date, to_date]],
            "docstatus": 1
        },
        fields=["name", "total", "total_taxes_and_charges", "base_total_taxes_and_charges"]
    )
    
    # Calculate totals
    total_sales = sum(inv["total"] for inv in sales_invoices)
    total_input_tax = sum(inv["total_taxes_and_charges"] for inv in purchase_invoices)
    total_output_tax = sum(inv["total_taxes_and_charges"] for inv in sales_invoices)
    
    net_tax_liability = total_output_tax - total_input_tax
    
    return {
        "period": f"{from_date} to {to_date}",
        "company": company,
        "total_sales": total_sales,
        "total_purchases": sum(inv["total"] for inv in purchase_invoices),
        "output_tax": total_output_tax,
        "input_tax": total_input_tax,
        "net_liability": net_tax_liability,
        "tax_rate_used": "Standard",
        "filing_due_date": get_tax_filing_date(to_date)
    }
```

---

## 5. Tax Troubleshooting

### Common Tax Issues & Solutions

```python
TAX_TROUBLESHOOTING = {
    "issue_1": {
        "problem": "Tax not auto-calculating on invoice",
        "causes": [
            "Tax template not set on transaction",
            "Tax template disabled",
            "Item tax template missing",
            "Tax category not set on customer"
        ],
        "solutions": [
            "Set default tax template in Selling Settings",
            "Enable tax template",
            "Create item tax template with tax rate",
            "Set tax category in customer master"
        ]
    },
    "issue_2": {
        "problem": "Wrong tax rate applied",
        "causes": [
            "Wrong tax template selected",
            "Tax category mismatch",
            "Hsn code mapping wrong",
            "Tax rate changed mid-period"
        ],
        "solutions": [
            "Verify correct tax template for transaction type",
            "Check customer tax category matches",
            "Update HSN code mapping",
            "Review tax rate change impact"
        ]
    },
    "issue_3": {
        "problem": "Reverse charge not working",
        "causes": [
            "Reverse charge not enabled",
            "Supplier not marked as unregistered",
            "Tax template for reverse charge not set"
        ],
        "solutions": [
            "Enable reverse charge in Accounts Settings",
            "Set supplier as reverse charge applicable",
            "Create separate reverse charge tax template"
        ]
    },
    "issue_4": {
        "problem": "Tax reconciliation mismatch",
        "causes": [
            "Missing tax entries",
            "Posted to wrong account",
            "Timing differences",
            "Credit notes not accounted"
        ],
        "solutions": [
            "Run tax audit report",
            "Reconcile tax payable account",
            "Check credit note journal entries",
            "Verify period cut-off"
        ]
    }
}
```

---

## Summary: Tax Configuration Checklist

**Foundation:**
- [ ] Tax accounts created in Chart of Accounts
- [ ] Tax accounts linked to correct company
- [ ] Default tax template set in settings

**Regional Setup:**
- [ ] Country-specific tax rates configured
- [ ] Tax categories created
- [ ] Item tax templates created
- [ ] HSN/SAC codes mapped (if applicable)

**Compliance:**
- [ ] E-invoicing configured (if required)
- [ ] Tax numbers validated (GSTIN, VAT, etc.)
- [ ] Tax reporting templates created
- [ ] Filing schedule configured

**Testing:**
- [ ] Test tax calculation on sales invoice
- [ ] Test tax calculation on purchase invoice
- [ ] Test credit note tax reversal
- [ ] Test inter-state vs intra-state tax

**Validation:**
- [ ] Tax reconciliation report runs clean
- [ ] Tax liability matches GL
- [ ] Input tax credit matches purchases
