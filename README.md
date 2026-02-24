# Frappe Skill Repository

This repository contains comprehensive documentation, engineering references, and workflows for mastering the Frappe Framework, ERPNext, and KSA ERP consulting.

## Structure

```
frappe-skill/
├── SKILL.md                          ← Skill definition & routing logic
├── README.md                         ← This file
├── references/
│   ├── frappe-framework-master/      ← Core Frappe Framework documentation
│   │   ├── 00_FOUNDATION/
│   │   ├── 01_CORE_SYSTEM/
│   │   ├── 02_DATABASE/
│   │   ├── 03_API/
│   │   ├── 04_HOOKS_SYSTEM/
│   │   ├── 05_FRONTEND/
│   │   ├── 08_PERMISSIONS_SECURITY/
│   │   ├── 09_BACKGROUND_JOBS/
│   │   ├── 12_CACHING/
│   │   ├── 18_ENGINEERING/
│   │   ├── 20_TEMPLATES/
│   │   ├── QUICK_REFERENCE.md
│   │   └── README.md
│   └── erpnext-master/               ← ERPNext module documentation
│       ├── 00_FOUNDATION/
│       ├── 02_ACCOUNTING/
│       ├── 03_SALES/
│       ├── 04_PURCHASE/
│       ├── 05_STOCK_INVENTORY/
│       ├── 06_MANUFACTURING/
│       ├── 07_CRM/
│       ├── 08_HR_PAYROLL/
│       ├── 10_TAX_COMPLIANCE/
│       ├── 15_CUSTOMIZATION/
│       ├── 16_EXTENDING_ERPNEXT/
│       ├── 19_API_INTEGRATIONS/
│       ├── 20_WORKFLOWS_AUTOMATION/
│       ├── 22_DEBUGGING/
│       ├── 23_PATTERNS/
│       ├── 24_ENGINEERING/
│       ├── 25_ELITE_SKILLS/
│       ├── 26_TEMPLATES/
│       ├── QUICK_REFERENCE.md
│       └── README.md
└── .agent/
    └── workflows/
        └── erp-proposal.md           ← KSA ERP Proposal & Pricing Generator
```

## Capabilities

### 1. Engineering Mode
Used for all Frappe/ERPNext development tasks:
- Custom DocType design and implementation
- Server-side & client-side scripts
- Hooks, background jobs, permissions
- REST API development and integrations
- Bench commands and site management
- Debugging and performance optimization

### 2. Proposal & Pricing Mode
Used when a new client brief is received:
- Triggers `.agent/workflows/erp-proposal.md` automatically
- Runs a 5-step structured process: Intake → Pricing Engine → Price Table → Full Proposal → Sanity Check
- Produces a professional, itemized client proposal ready to send
- Includes KSA-specific compliance pricing (ZATCA, VAT, GOSI, MUDAD)

## Purpose

This skill transforms the AI into a **dual-mode expert**:
- A senior Frappe engineer for all technical implementation work
- A KSA ERP consultant that generates accurate, professional proposals in minutes
