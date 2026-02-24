# Requirement Analysis Framework

## Quick Reference
Structured approach to gather, analyze, and document ERPNext requirements. Use this framework to translate business needs into ERPNext configurations.

## AI Prompt
```
When analyzing requirements:
1. Use the 5W1H method (Who, What, When, Where, Why, How)
2. Map requirements to ERPNext modules
3. Identify standard vs custom features
4. Estimate effort for customizations
5. Document assumptions and constraints
```

---

## Requirement Gathering Template

### 1. Business Overview
```
Client: [Company Name]
Industry: [Industry]
Current System: [Legacy system or manual]
Users: [Number and roles]
Timeline: [Expected go-live date]
Budget: [Budget range]
```

### 2. Module Requirements

#### Sales & CRM
| Requirement | Priority | ERPNext Feature | Gap |
|-------------|----------|-----------------|-----|
| Lead capture | High | Lead DocType | Standard |
| Quotation | High | Quotation | Standard |
| Order management | High | Sales Order | Standard |
| Delivery tracking | Medium | Delivery Note | Standard |
| Custom pricing | High | Pricing Rule | Config |

#### Purchase
| Requirement | Priority | ERPNext Feature | Gap |
|-------------|----------|-----------------|-----|
| Supplier RFQ | Medium | Supplier Quotation | Standard |
| PO approval | High | Workflow | Config |
| Goods receipt | High | Purchase Receipt | Standard |

#### Inventory
| Requirement | Priority | ERPNext Feature | Gap |
|-------------|----------|-----------------|-----|
| Multiple warehouses | High | Warehouse | Standard |
| Stock tracking | High | Stock Entry | Standard |
| Batch tracking | Medium | Batch | Standard |
| Serial tracking | Medium | Serial No | Standard |

#### Accounting
| Requirement | Priority | ERPNext Feature | Gap |
|-------------|----------|-----------------|-----|
| Multi-currency | High | Standard | Standard |
| Tax compliance | High | Tax Template | Config |
| Bank reconciliation | High | Bank Reco | Standard |

---

## Analysis Checklist

### Functional Requirements
- [ ] Master data requirements
- [ ] Transaction workflows
- [ ] Approval processes
- [ ] Reports needed
- [ ] Integrations required
- [ ] User roles and permissions
- [ ] Notifications and alerts

### Technical Requirements
- [ ] Number of users
- [ ] Data volume
- [ ] Performance expectations
- [ ] Security requirements
- [ ] Integration APIs
- [ ] Custom DocTypes needed
- [ ] Custom reports needed

### Non-Functional Requirements
- [ ] Availability (uptime %)
- [ ] Response time
- [ ] Backup strategy
- [ ] Disaster recovery
- [ ] Compliance requirements

---

## Effort Estimation

### Complexity Levels
| Level | Description | Effort |
|-------|-------------|--------|
| Standard | Use as-is | 0 days |
| Configuration | Settings, workflows | 0.5-2 days |
| Low Custom | Custom fields, scripts | 2-5 days |
| Medium Custom | New DocTypes, reports | 5-15 days |
| High Custom | Complex workflows, integrations | 15-30 days |

### Estimation Template
```
Module: Sales
├── Lead Management (Standard): 0 days
├── Custom pricing rules (Config): 2 days
├── Sales workflow (Config): 1 day
├── Custom sales report (Low): 3 days
└── Total: 6 days

Module: Stock
├── Warehouse setup (Config): 1 day
├── Stock workflows (Config): 2 days
├── Custom stock report (Low): 3 days
└── Total: 6 days

Total Estimated: 12 days
Buffer (20%): 2.4 days
Final Estimate: 15 days
```

---

## Gap Analysis Matrix

| Requirement | Standard | Config | Custom | Priority | Effort |
|-------------|----------|--------|--------|----------|--------|
| Feature 1 | ✓ | | | High | 0 |
| Feature 2 | | ✓ | | High | 2 |
| Feature 3 | | | ✓ | Medium | 5 |
| Feature 4 | | | ✓ | Low | 3 |

---

## Questions to Ask

### Business Questions
1. What are the main business processes?
2. Who are the key stakeholders?
3. What reports are essential?
4. What are the pain points with current system?
5. What integrations are needed?

### Technical Questions
1. How many concurrent users?
2. What is the expected data volume?
3. Are there existing systems to integrate?
4. What are the security requirements?
5. What is the infrastructure available?

### Process Questions
1. Walk me through a sales cycle
2. How do you handle returns?
3. How do you manage inventory?
4. How do you process payments?
5. How do you close financial periods?

---

## Deliverables

1. **Requirement Document**
   - Business overview
   - Functional requirements
   - Non-functional requirements
   - Assumptions and constraints

2. **Gap Analysis Document**
   - Feature mapping
   - Gap identification
   - Effort estimation

3. **Solution Design**
   - ERPNext configuration
   - Custom DocTypes design
   - Workflow design
   - Integration architecture

4. **Implementation Plan**
   - Phase breakdown
   - Timeline
   - Resource allocation
   - Risk mitigation

---

## Related Topics
- [Implementation Checklist](./01_implementation-checklist.md)
- [Gap Analysis](./03_gap-analysis.md)
- [ERP Design Approach](../24_ENGINEERING/01_erp-design-approach.md)
