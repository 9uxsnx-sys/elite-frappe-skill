# Gap Analysis Framework

## Quick Reference
Gap Analysis compares business requirements with ERPNext capabilities. Identifies what's standard, configurable, or requires customization.

## AI Prompt
```
When conducting gap analysis:
1. List all requirements
2. Map to ERPNext features
3. Classify gaps (Critical/Important/Nice-to-have)
4. Estimate effort for each gap
5. Propose solutions for gaps
```

---

## Gap Analysis Template

### Requirement Mapping Table
| Requirement | ERPNext Feature | Coverage | Gap | Solution |
|-------------|-----------------|----------|-----|----------|
| Customer Management | Customer DocType | 100% | None | Standard |
| Multiple Price Lists | Price List | 100% | None | Standard |
| Custom Approval | Workflow | 80% | Multiple approvers | Custom workflow |
| Integration with CRM | REST API | 50% | Auto sync | Custom API |

---

## Coverage Classification

| Coverage | Description | Action |
|----------|-------------|--------|
| 100% | Fully supported | Use standard |
| 80-99% | Minor customization | Configure |
| 50-79% | Major customization | Develop |
| 0-49% | Not supported | Third-party or custom |

---

## Gap Priority

| Priority | Criteria | Examples |
|----------|----------|----------|
| Critical | Business cannot operate | Accounting, Invoicing |
| Important | Significant efficiency impact | Workflows, Reports |
| Nice-to-have | Minor convenience | UI tweaks, Extra fields |

---

## Analysis Process

### Step 1: Requirement Collection
```
1. Interview stakeholders
2. Document current processes
3. Identify pain points
4. List must-have features
```

### Step 2: Feature Mapping
```
1. Review ERPNext modules
2. Match requirements to features
3. Document standard behavior
4. Identify deviations
```

### Step 3: Gap Documentation
```
1. Describe the gap
2. Assess impact
3. Propose solutions
4. Estimate effort
```

---

## Common Gaps & Solutions

| Gap | Standard Solution |
|-----|-------------------|
| Custom fields | Custom Field DocType |
| Custom validation | Server Script |
| UI changes | Property Setter |
| Approval workflow | Workflow DocType |
| Custom reports | Query/Script Report |
| Integration | REST API + Webhooks |
| Complex logic | Custom App |

---

## Effort Estimation

| Solution Type | Effort |
|---------------|--------|
| Standard feature | 0 days |
| Configuration | 0.5-2 days |
| Custom fields/scripts | 1-3 days |
| Custom DocType | 3-5 days |
| Custom workflow | 2-4 days |
| Custom report | 2-5 days |
| Integration | 5-15 days |

---

## Deliverable: Gap Analysis Report

```markdown
# Gap Analysis Repo
