# ERPNext Master Skill

## Purpose
This skill folder contains comprehensive knowledge for mastering ERPNext - an open-source ERP system built on the Frappe Framework. It enables AI agents to engineer, design, debug, and implement any ERPNext-based solution.

## Quick Navigation

### Foundation
- [00_FOUNDATION](./00_FOUNDATION/) - Overview, architecture, installation, modules

### Core Business Modules
- [01_CORE_DOCTYPES](./01_CORE_DOCTYPES/) - Party, Item, Price Lists, Address/Contact
- [02_ACCOUNTING](./02_ACCOUNTING/) - Chart of Accounts, Journal, Payments, GL
- [03_SALES](./03_SALES/) - Quotation, Sales Order, Delivery Note, Invoice
- [04_PURCHASE](./04_PURCHASE/) - Purchase Order, Receipt, Invoice
- [05_STOCK_INVENTORY](./05_STOCK_INVENTORY/) - Warehouse, Stock Entry, Serial/Batch
- [06_MANUFACTURING](./06_MANUFACTURING/) - BOM, Work Order, Production
- [07_CRM](./07_CRM/) - Lead, Opportunity, Customer lifecycle
- [08_HR_PAYROLL](./08_HR_PAYROLL/) - Employee, Attendance, Payroll
- [09_PROJECTS](./09_PROJECTS/) - Project, Task, Timesheet
- [10_TAX_COMPLIANCE](./10_TAX_COMPLIANCE/) - Tax setup, GST, VAT
- [11_ASSETS](./11_ASSETS/) - Asset management, depreciation
- [12_QUALITY_MANAGEMENT](./12_QUALITY_MANAGEMENT/) - Quality inspection

### Web & Commerce
- [13_WEBSITE_ECOMMERCE](./13_WEBSITE_ECOMMERCE/) - Website, Shopping Cart
- [14_SECTOR_MODULES](./14_SECTOR_MODULES/) - Education, Healthcare, Hotels

### Customization & Development
- [15_CUSTOMIZATION](./15_CUSTOMIZATION/) - Custom Fields, Scripts, Property Setters
- [16_EXTENDING_ERPNEXT](./16_EXTENDING_ERPNEXT/) - Override controllers, hooks
- [17_MULTI_COMPANY](./17_MULTI_COMPANY/) - Multi-company, inter-company
- [18_DATA_MANAGEMENT](./18_DATA_MANAGEMENT/) - Import, Export, Migration
- [19_API_INTEGRATIONS](./19_API_INTEGRATIONS/) - REST API, integrations
- [20_WORKFLOWS_AUTOMATION](./20_WORKFLOWS_AUTOMATION/) - Workflows, automation

### Operations
- [21_REPORTING](./21_REPORTING/) - Reports, Dashboards, Analytics
- [22_DEBUGGING](./22_DEBUGGING/) - Errors, troubleshooting
- [23_PATTERNS](./23_PATTERNS/) - Design patterns, best practices
- [24_ENGINEERING](./24_ENGINEERING/) - System design, architecture
- [25_ELITE_SKILLS](./25_ELITE_SKILLS/) - Advanced skills, checklists
- [26_TEMPLATES](./26_TEMPLATES/) - Code templates

---

## AI System Prompt

\`\`\`
You are an ERPNext expert with deep knowledge of:
1. All ERPNext modules and their interconnections
2. Accounting, inventory, and business process flows
3. Frappe Framework (the foundation of ERPNext)
4. Best practices for customization and extension
5. Debugging and troubleshooting ERPNext systems

When given a system idea:
1. Analyze business requirements
2. Design DocTypes and data models
3. Plan workflows and automation
4. Identify integration points
5. Consider scalability and performance

Always reference Frappe Framework concepts when working with ERPNext internals.
\`\`\`

## Document Flow Reference

### Sales Flow
\`\`\`
Lead → Opportunity → Quotation → Sales Order → Delivery Note → Sales Invoice → Payment Entry
\`\`\`

### Purchase Flow
\`\`\`
Supplier Quotation → Purchase Order → Purchase Receipt → Purchase Invoice → Payment Entry
\`\`\`

### Stock Flow
\`\`\`
Stock Entry (Material Receipt/Issue/Transfer) → Stock Ledger Entry → GL Entry
\`\`\`

### Manufacturing Flow
\`\`\`
BOM → Production Plan → Work Order → Job Card → Stock Entry (Manufacture)
\`\`\`

## Key Tables

| DocType | Table Name | Purpose |
|---------|------------|---------|
| Company | tabCompany | Company master |
| Customer | tabCustomer | Customer master |
| Supplier | tabSupplier | Supplier master |
| Item | tabItem | Item master |
| Account | tabAccount | Chart of Accounts |
| Warehouse | tabWarehouse | Warehouse master |

## Version Compatibility

This skill covers ERPNext Version 14-15+ (2024-2026).

## Related Skills
- **Frappe Framework**: C:\skills\frappe-framework-master\ - Core framework knowledge
