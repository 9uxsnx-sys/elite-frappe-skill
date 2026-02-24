---
description: Generate a professional, itemized ERP proposal and accurate price estimate for any region. Includes compliance modules for KSA (ZATCA), UAE (FTA), EU (VAT), and more.
---

# ERPNext Elite — Global Proposal Generator

Use this workflow every single time a new client brief is provided.
Follow all 5 steps in sequence. Do NOT skip any step.

**Region Mode:** Select the primary region for compliance requirements, or use GLOBAL for generic proposals.

// turbo-all

---

## STEP 0 — REGION SELECTION

**Select the primary compliance region:**

| Region | Compliance Modules | Default Currency |
|--------|------------------|------------------|
| KSA (Saudi Arabia) | ZATCA, GOSI, Mudad | SAR/USD |
| UAE (Dubai/UAE) | FTA e-invoicing, VAT | AED/USD |
| EU (Europe) | GDPR, VAT MOSS | EUR/USD |
| UK | Making Tax Digital (MTD) | GBP/USD |
| USA | Sales tax, SOX compliance | USD |
| GLOBAL | Generic (no region-specific) | USD |

> **Note:** For multi-region clients, add $2,000 per additional region compliance module.

---

## STEP 1 — CLIENT INTAKE & CLARIFICATION

Before calculating anything, collect ALL of the following.
If any item is missing, ask the user before proceeding to Step 2.

**Required Information Checklist:**
- [ ] **Users** — Exact number or estimated range of named system users
- [ ] **Industry** — (Trading, Retail, Manufacturing, Services, Contracting, Real Estate, Healthcare, etc.)
- [ ] **Modules** — List every module the client mentioned needing
- [ ] **Region** — Primary country/region for compliance
- [ ] **Tax Compliance** — VAT/GST registered? Tax authority requirements?
- [ ] **Customization** — Any custom workflows, automation, calculations, or unique business logic?
- [ ] **Integrations** — Third-party systems to connect? (bank feeds, payment gateways, e-commerce, government portals, shipping, POS)
- [ ] **Data migration** — Migrating FROM what? (Excel, QuickBooks, legacy ERP, SAP, paper, etc.)
- [ ] **Deployment** — Frappe Cloud, client's VPS, or on-premise server?
- [ ] **Language** — Arabic only, English only, or Bilingual (Arabic + English)?
- [ ] **Timeline** — Target go-live date or urgency level
- [ ] **Multi-company/Branch** — Does the client have subsidiaries or branches needing consolidation?

---

## STEP 2 — PRICING ENGINE

Calculate each component separately and explicitly.
Never merge components into a single number.

---

### A — BASE IMPLEMENTATION FEE

Covers project management, system architecture, core setup, and configuration overhead.

| User Count  | Rate per User |
|-------------|---------------|
| 1 – 10      | $600 / user   |
| 11 – 25     | $520 / user   |
| 26 – 50     | $450 / user   |
| 51 – 100    | $380 / user   |
| 101 – 200   | $320 / user   |
| 201 – 500   | $270 / user   |
| 500+        | $230 / user   |

> **Minimum base fee = $8,000** regardless of user count.
> **Multi-branch / multi-company**: Add **$3,500 per additional company or branch**.

---

### B — MODULE SETUP FEES

One-time setup fee per module. Includes configuration, standard reports, and testing.

| Module                                                       | Fee    |
|--------------------------------------------------------------|--------|
| Accounting & Finance (CoA, GL, reconciliation, fin. reports) | $3,500 |
| Sales & CRM (Quotation, Sales Order, Invoice, pipeline)      | $2,500 |
| Purchasing (PO, receipts, supplier management, 3-way match)  | $2,000 |
| Stock & Inventory (warehouses, transfers, valuation)         | $2,800 |
| Manufacturing (BOM, Work Orders, Job Cards, routing)         | $4,500 |
| HR & Payroll (employees, attendance, leave, salary slips)    | $4,000 |
| Projects & Timesheets (task mgmt, project billing)           | $2,000 |
| Website / eCommerce (catalog, cart, online orders)           | $3,500 |
| Fixed Assets Management                                      | $1,800 |
| Quality Management                                           | $2,200 |
| Point of Sale (POS)                                          | $2,500 |
| Maintenance & Service Management                             | $2,200 |
| Subscriptions & Recurring Billing                            | $1,800 |

---

### C — REGIONAL COMPLIANCE (Based on Region Selection)

#### C1. Region-Specific Tax Compliance

**KSA (Saudi Arabia):**

| Tier                                  | Scope                                                   | Fee     |
|---------------------------------------|---------------------------------------------------------|---------|
| Phase 1 Only                          | QR code generation, simplified XML invoice format       | $4,500  |
| Phase 2 Only                          | Full Fatoora API integration, real-time reporting        | $9,500  |
| **Phase 1 + Phase 2 (Full)**          | Complete end-to-end ZATCA compliance                    | $12,000 |
| Phase 1 + Phase 2 + GOSI/MIDAD        | Full invoice compliance + payroll protection compliance | $16,500 |

> Non-compliance risk: up to **$13,000 per invoice violation** + bank account freeze + trade license revocation.

**UAE (Dubai/FTA):**

| Tier | Scope | Fee |
|------|-------|-----|
| Basic e-invoicing | PDF/A3 compliance, QR codes | $3,500 |
| Full FTA integration | Real-time reporting API | $8,500 |
| e-Tax + VAT audit | Tax audit trail, e-Waybill | $12,000 |

**EU (VAT MOSS):**

| Tier | Scope | Fee |
|------|-------|-----|
| VAT registration | Intra-EU B2B compliance | $2,500 |
| VAT MOSS | Digital services to consumers | $5,000 |
| GDPR + VAT | Full data protection + tax | $9,000 |

**UK (MTD - Making Tax Digital):**

| Tier | Scope | Fee |
|------|-------|-----|
| MTD Basic | Quarterly reporting compliance | $3,500 |
| MTD Full | API integration with HMRC | $7,500 |
| VAT + CT | Corporation Tax digital | $12,000 |

**USA:**

| Tier | Scope | Fee |
|------|-------|-----|
| Sales tax nexus | State-by-state compliance | $4,000 |
| Avalara/Vertex integration | Automated tax calculation | $8,000 |
| SOX compliance | Audit trail + controls | $15,000+ |

**GLOBAL (No specific region):**

| Tier | Scope | Fee |
|------|-------|-----|
| Generic tax setup | Basic VAT/GST configuration | $1,500 |
| Multi-currency | 150+ currencies, exchange rates | $3,500 |

#### C2. GOSI Integration (KSA only)
**$5,000** — Only for KSA payroll compliance

#### C3. MUDAD / WPS (KSA only)
**$3,500** — Wage Protection System for KSA

---

### D — CUSTOMIZATION LEVEL

Assess based on client's business logic needs beyond standard module features.

| Level      | What It Includes                                                                         | Fee       |
|------------|------------------------------------------------------------------------------------------|-----------|
| **None**   | Pure standard configuration — no code written                                            | $0        |
| **Light**  | 1–4 simple scripts (client or server), minor field additions, 1 basic workflow           | $3,500    |
| **Medium** | Custom DocTypes (1–3 new), complex validations, approval chains, custom reports          | $9,000    |
| **Heavy**  | Custom Frappe app, complex business logic engine, multi-step automations, domain rules   | $20,000   |
| **Elite**  | Full custom module, deep ERP extension (contractor billing, pharma, real estate, etc.)   | $35,000+  |

> If client says "just a few tweaks" → always assess as at least **Light**.
> Non-standard industry process → always assess as at least **Medium**.

---

### E — THIRD-PARTY INTEGRATIONS (per integration)

Each requires: API analysis, mapping, error handling, testing, and documentation.

| Integration Type                                      | Fee              |
|-------------------------------------------------------|------------------|
| Simple REST API / Webhook (one-directional)           | $2,500           |
| Bidirectional Data Sync (two-way API)                 | $4,000           |
| Payment Gateway (Moyasar, HyperPay, PayTabs, Stripe)  | $4,500           |
| Bank Account Feed / Statement Reconciliation API       | $5,000           |
| E-commerce Platform (Shopify, WooCommerce, Salla)      | $6,000           |
| Shipping / Logistics (Aramex, DHL, SMSA, Naqel)       | $3,500           |
| POS Hardware Integration                              | $3,000           |
| Legacy System (requires reverse engineering)          | $8,000 – $15,000 |
| Gov. Portals (ZATCA, GOSI, MUDAD)                     | → See Section C  |

---

### F — DATA MIGRATION

One-time fee. Scope based on the complexity of their existing data.

| Level            | Description                                                          | Fee     |
|------------------|----------------------------------------------------------------------|---------|
| **Simple**       | Clean Excel/CSV, <10,000 records, 1–2 entity types                  | $2,200  |
| **Standard**     | Multiple entities, >10,000 records, some data cleaning needed        | $5,500  |
| **Complex**      | Legacy ERP export, inconsistent data, full opening balances needed   | $12,000 |
| **Very Complex** | Multiple legacy systems, full accounting reconciliation required      | $18,000 |

> Always scope data migration separately. Clients reliably underestimate how messy their data is.

---

### G — PRINT FORMATS & DOCUMENT TEMPLATES

Custom-branded, bilingual-ready document templates.

| Scope                              | Documents Included                                           | Fee    |
|------------------------------------|--------------------------------------------------------------|--------|
| **Basic** (2–3 formats)            | Sales Invoice + Quotation                                    | $1,500 |
| **Standard** (4–6 formats)         | Invoice, Quotation, PO, Delivery Note, Payment Voucher       | $3,500 |
| **Full Bilingual Suite** (7–10+)   | All above + HR Letters, Credit Note, statements, Arabic RTL  | $6,500 |

> KSA clients: always recommend Full Bilingual Suite.

---

### H — TRAINING & DOCUMENTATION

| Scope                                     | What Is Included                                                     | Fee    |
|-------------------------------------------|----------------------------------------------------------------------|--------|
| **Basic** (up to 15 users, 1 day)         | Hands-on training session                                            | $1,800 |
| **Standard** (16–60 users, 2–3 days)      | Training sessions + role-based user guides (PDF)                     | $4,000 |
| **Enterprise** (60+ users, full program)  | Dept.-by-dept. training + admin manual + user manuals per role       | $8,500 |

---

### I — DEPLOYMENT & INFRASTRUCTURE SETUP

| Deployment Type                                | Included                                             | Fee    |
|------------------------------------------------|------------------------------------------------------|--------|
| Frappe Cloud (managed hosting)                 | Account setup, site creation, domain config, SSL     | $1,200 |
| Client's VPS (DigitalOcean, AWS, Hetzner, etc.) | Ubuntu, Nginx, Bench, SSL, firewall, backup automation | $2,000 |
| On-premise Server (client's own hardware)      | OS coordination, bench install, network config        | $3,500 |

---

### J — COMPLEXITY BUFFER RULE

**Add +10% on the subtotal if ANY of the following apply:**
- 4 or more modules in the project
- Customization is Heavy or Elite
- 3 or more third-party integrations
- Multi-company or multi-branch setup
- Very Complex data migration

**Add +15% (urgency fee) instead if:**
- Client requires go-live in under 6 weeks

This buffer is non-negotiable. It protects against scope creep and edge cases that occur in every real enterprise implementation.

---

### K — ANNUAL SUPPORT RETAINER (Recurring from Year 1)

| Level        | What Is Covered                                                        | Rate               | Minimum    |
|--------------|------------------------------------------------------------------------|--------------------|------------|
| **Basic**    | Email support, max 5 tickets/mo, security patches, ERPNext updates     | 12% of project/yr  | $3,600/yr  |
| **Standard** | Email + WhatsApp, max 15 tickets/mo, minor enhancements, monthly report | 17% of project/yr | $6,000/yr  |
| **Premium**  | Dedicated engineer, 24h SLA, monthly calls, enhancements included      | 22% of project/yr  | $10,000/yr |

> 100+ users → always **Premium**.
> 20–100 users → always **Standard**.
> Under 20 users → **Basic** or **Standard** based on ZATCA complexity.

---

## STEP 3 — BUILD THE ITEMIZED PRICE TABLE

Output this exact table with all applicable line items filled in:

```
╔══════════════════════════════════════════╦══════════════════════════════╦══════════════╗
║ Component                                ║ Details                      ║ Cost (USD)   ║
╠══════════════════════════════════════════╬══════════════════════════════╬══════════════╣
║ Base Implementation Fee                  ║ XX users × $YYY/user         ║ $X,XXX       ║
║ Module: Accounting & Finance             ║                              ║ $3,500       ║
║ Module: [Next Module]                    ║                              ║ $X,XXX       ║
║ Module: [Next Module]                    ║                              ║ $X,XXX       ║
║ ZATCA Compliance                         ║ Phase 1 + 2 (Full)           ║ $12,000      ║
║ Customization                            ║ [Level] — [brief desc]       ║ $X,XXX       ║
║ Integration: [Name]                      ║ [brief desc]                 ║ $X,XXX       ║
║ Data Migration                           ║ [Complexity]                 ║ $X,XXX       ║
║ Print Formats                            ║ [Scope]                      ║ $X,XXX       ║
║ Training & Documentation                 ║ [Scope]                      ║ $X,XXX       ║
║ Deployment Setup                         ║ [Type]                       ║ $X,XXX       ║
╠══════════════════════════════════════════╬══════════════════════════════╬══════════════╣
║ Subtotal                                 ║                              ║ $XX,XXX      ║
║ Complexity Buffer (+10% / +15%)          ║ [reason if applied]          ║ $X,XXX       ║
╠══════════════════════════════════════════╬══════════════════════════════╬══════════════╣
║ ★ TOTAL PROJECT COST                     ║                              ║ $XX,XXX      ║
╠══════════════════════════════════════════╬══════════════════════════════╬══════════════╣
║ Annual Support Retainer (Year 1)         ║ [Level] — X% of project      ║ $X,XXX/yr    ║
╚══════════════════════════════════════════╩══════════════════════════════╩══════════════╝
```

---

## STEP 4 — WRITE THE FULL CLIENT PROPOSAL

Generate a complete, professional proposal using the exact structure below.
This document must be polished enough to send directly to a client or print as a PDF.

---

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    ERP IMPLEMENTATION PROPOSAL
              Prepared exclusively for: [Client Company]
                         Date: [Date]
                    Quote valid for: 30 Days
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

──────────────────────────────────────────────────────────────
1. EXECUTIVE SUMMARY
──────────────────────────────────────────────────────────────
We are a specialized ERP implementation agency with deep
expertise in ERPNext and the Saudi regulatory landscape
(ZATCA, VAT 15%, GOSI, MUDAD, Vision 2030 compliance).

This proposal outlines our complete delivery plan for [Client
Name]: a fully compliant, customized ERP system covering
[X modules] for [X users], with ZATCA Phase 1 & 2 compliance
engineered in from day one — not bolted on as an afterthought.

Our solution eliminates [Client's pain point], replaces
[current system], and protects [Client Name] from ZATCA
non-compliance risks (fines up to SAR 187,000 per violation,
bank freezes, and license revocations).


──────────────────────────────────────────────────────────────
2. PROJECT SCOPE
──────────────────────────────────────────────────────────────
WHAT IS INCLUDED:
  ✅ [Module 1] — [one-line description of what it does]
  ✅ [Module 2] — [one-line description]
  ✅ [Module 3] — [one-line description]
  ✅ ZATCA Phase [X] — Full e-invoicing compliance
  ✅ [Custom development item — be specific]
  ✅ [Integration name] — [what it connects and why]
  ✅ Data migration from [current system]
  ✅ [Print format scope] — Arabic/English bilingual documents
  ✅ [Training scope]
  ✅ [Deployment type]

EXPLICITLY OUT OF SCOPE (not included in this quote):
  ❌ [E.g. Mobile app development]
  ❌ [E.g. Hardware procurement or server hardware]
  ❌ [E.g. Any modules not listed above]
  ❌ Scope changes after project sign-off (billed separately)
  ❌ Third-party software license costs (e.g. server costs)


──────────────────────────────────────────────────────────────
3. DELIVERY TIMELINE — [X] WEEKS TO GO-LIVE
──────────────────────────────────────────────────────────────
Phase 1: Discovery & System Design            Week 1 – 2
  • Requirements validation workshop
  • System architecture finalization
  • Data migration field mapping
  • Custom development specification sign-off

Phase 2: Configuration & Development         Week 3 – [X]
  • Core module configuration
  • Custom DocTypes and scripts development
  • ZATCA integration and testing
  • Third-party integrations
  • Bilingual print format design

Phase 3: Data Migration & UAT Testing        Week [X] – [X]
  • Data cleanse, import, and validation
  • User Acceptance Testing (UAT) sessions
  • Bug fixes and adjustments
  • Performance verification

Phase 4: Training & Go-Live                  Week [X] – [X]
  • Department-by-department training
  • User and admin documentation delivery
  • Production go-live
  • 2-week post-launch monitoring and support

TARGET GO-LIVE: [Projected date]


──────────────────────────────────────────────────────────────
4. INVESTMENT SUMMARY
──────────────────────────────────────────────────────────────
[Insert full itemized price table from Step 3 here]

PAYMENT SCHEDULE:
  40% — Project Kickoff (upon contract signing)
         Amount: $[X,XXX]
  40% — Phase 2 Completion Milestone
         Amount: $[X,XXX]
  20% — Go-Live Sign-Off
         Amount: $[X,XXX]

All prices in USD. Equivalent SAR invoices available
at the confirmed exchange rate on invoice date.


──────────────────────────────────────────────────────────────
5. WHY CHOOSE US
─────────────────────────────────────────────────────────────
⚡ SPEED — Weeks, Not Months
   What SAP/Oracle partners deliver in 12–18 months,
   we deliver in 6–12 weeks. No bloated teams. No overhead.
   Direct engineering with guaranteed deadlines.

💰 ZERO SOFTWARE LICENSE FEES — FOREVER
   ERPNext is open source. You own the system outright.
   No per-user monthly fees. No vendor lock-in.
   Estimated savings vs SAP/Oracle: $30,000–$200,000/year.

🌍 GLOBAL COMPLIANCE EXPERTISE
   We build compliance into the foundation from day one:
   - KSA: ZATCA, GOSI, MUDAD
   - UAE: FTA e-invoicing
   - EU: VAT MOSS, GDPR
   - UK: Making Tax Digital
   - USA: Sales tax nexus, SOX
   Never retrofit compliance — build it right the first time.

📋 DOCUMENTATION THAT ACTUALLY EXISTS
   Most ERP agencies deliver a system and disappear.
   We deliver: user manuals, admin guides, technical docs,
   and training materials — all included.

🛡️ COMPLIANCE PROTECTION — Your Insurance Policy
   Tax authority non-compliance can result in:
   - KSA: Up to SAR 187,000 per violation
   - UAE: Fines + trade license issues
   - EU: VAT penalties up to 100%
   - USA: Sales tax nexus penalties
   Our implementations ensure full compliance from go-live.


──────────────────────────────────────────────────────────────
6. TERMS & CONDITIONS
──────────────────────────────────────────────────────────────
• Quote validity: 30 days from the date above
• Scope changes post-project sign-off: billed at $120/hr
• Client obligations:
    – Designate a single point of contact for decisions
    – Provide all source data by Week 1 deadline
    – Participate in UAT sessions during Phase 3
    – Provide server/IT access within 48h of project start
• Annual support retainer invoiced 30 days after go-live
• Timeline SLA excludes force majeure and infrastructure
  delays outside our control
• This proposal is confidential and intended solely for
  [Client Company Name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## STEP 5 — FINAL SANITY CHECK

Before presenting the proposal, confirm every item:

- [ ] Total cost competitive vs market tier this client belongs to?
- [ ] 10% buffer applied if 4+ modules OR Heavy/Elite customization?
- [ ] 15% urgency fee applied if timeline is under 6 weeks?
- [ ] ZATCA section included for any VAT-registered client?
- [ ] Out-of-scope items explicitly and specifically listed?
- [ ] Payment milestones clearly stated with amounts?
- [ ] Support retainer level matches client size?
- [ ] Executive summary is jargon-free and client-friendly?
- [ ] Timeline phases are realistic for the stated scope?

---

## HARD PRICING RULES — NEVER BREAK THESE

| Rule | Requirement |
|------|------------|
| **Floor price** | Never quote below **$10,000 total** under any circumstances |
| **Trading company** | Accounting + Sales + Stock + ZATCA → minimum **$20,000** |
| **Manufacturing** | Always adds Manufacturing module → minimum **+$4,500** |
| **HR in KSA** | Always bundle with GOSI/MUDAD compliance |
| **"Simple setup" clients** | Always scope at minimum **Light** customization |
| **100+ users** | Always quote **Premium** support retainer |
| **Urgency (<6 weeks)** | Always apply **+15% urgency fee** |
| **Multi-company/branch** | Always add **$3,500 per additional entity** |
| **VAT-registered clients** | ZATCA is never optional — always include it |
| **Legacy system migration** | Always scope data migration separately, never bundle |
