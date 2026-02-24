# Lead

## Quick Reference
Lead is a potential customer. First stage in sales pipeline. Can be converted to Customer or Opportunity. Track source, status, and follow-ups.

## AI Prompt
```
When managing leads:
1. Capture lead source for reporting
2. Set up automated follow-ups
3. Track communication history
4. Qualify before conversion
5. Link to campaigns for ROI tracking
```

---

## Lead DocType

### Key Fields
| Field | Type | Description |
|-------|------|-------------|
| lead_name | Data | Contact name |
| company_name | Data | Company name |
| source | Link | Lead source |
| status | Select | Lead/Open/Replied/Opportunity/Converted/Lost |
| email_id | Data | Email |
| mobile_no | Data | Phone |

### Status Values
- Lead
- Open
- Replied
- Opportunity
- Quotation
- Lost
- Interested
- Converted

---

## Creating Lead

```python
lead = frappe.get_doc({
    "doctype": "Lead",
    "lead_name": "John Doe",
    "company_name": "ABC Corp",
    "source": "Website",
    "status": "Lead",
    "email_id": "john@abccorp.com",
    "mobile_no": "+1234567890"
})
lead.insert()
```

---

## Lead Conversion

### To Customer
```python
lead = frappe.get_doc("Lead", "LEAD-001")
customer = lead.make_customer()
customer.insert()

lead.status = "Converted"
lead.customer = customer.name
lead.save()
```

### To Opportunity
```python
lead = frappe.get_doc("Lead", "LEAD-001")
opp = lead.make_opportunity()
opp.insert()
```

---

## Lead API

### Get Open Leads
```python
leads = frappe.get_all("Lead",
    filters={"status": ["in", ["Lead", "Open", "Replied"]]},
    fields=["name", "lead_name", "company_name", "email_id"]
)
```

### Get Lead Communication
```python
from frappe.email.inbox import get_communication_data

communications = get_communication_data("Lead", "LEAD-001")
```

---

## Related Topics
- [Opportunity](./02_opportunity.md)
- [Customer](../01_CORE_DOCTYPES/01_party-master.md)
