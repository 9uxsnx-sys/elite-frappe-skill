# Opportunity

## Quick Reference
Opportunity represents a qualified sales lead. Tracks items of interest, expected close date, and probability. Creates Quotation for proposals.

## AI Prompt
```
When managing opportunities:
1. Qualify lead before creating
2. Track expected close date
3. Set probability for forecasting
4. Link to sales cycle
5. Create quotation when ready
```

---

## Opportunity DocType

### Key Fields
| Field | Type | Description |
|-------|------|-------------|
| opportunity_from | Select | Lead/Customer |
| party_name | Dynamic Link | Lead or Customer |
| status | Select | Open/Replied/Quotation/Won/Lost |
| expected_close_date | Date | Expected close |
| opportunity_type | Link | Type of opportunity |
| items | Table | Items of interest |

---

## Creating Opportunity

### From Lead
```python
from erpnext.crm.doctype.lead.lead import make_opportunity

opp = make_opportunity("LEAD-001")
opp.insert()
```

### Direct Creation
```python
opp = frappe.get_doc({
    "doctype": "Opportunity",
    "opportunity_from": "Customer",
    "party_name": "ABC Corp",
    "status": "Open",
    "expected_close_date": "2024-02-28",
    "items": [{
        "item_code": "LAPTOP-001",
        "qty": 2
    }]
})
opp.insert()
```

---

## Create Quotation

```python
from erpnext.crm.doctype.opportunity.opportunity import make_quotation

qt = make_quotation("OPP-001")
qt.insert()
```

---

## Related Topics
- [Lead](./01_lead.md)
- [Quotation](../03_SALES/01_quotation.md)
