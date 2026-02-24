# Work Order

## Quick Reference
Work Order initiates production. Creates material transfer requests, job cards, and stock entry for finished goods. Tracks production progress.

## AI Prompt
```
When creating Work Orders:
1. Validate BOM exists and is active
2. Check material availability
3. Set correct production quantity
4. Monitor WIP and FG warehouses
5. Track job card completion
```

---

## Work Order DocType

### Key Fields
| Field | Type | Description |
|-------|------|-------------|
| production_item | Link | Item to produce |
| bom_no | Link | BOM reference |
| qty | Float | Production quantity |
| wip_warehouse | Link | Work in progress warehouse |
| fg_warehouse | Link | Finished goods warehouse |
| status | Select | Draft/Submitted/In Progress/Completed |

---

## Creating Work Order

### Basic Work Order
```python
wo = frappe.get_doc({
    "doctype": "Work Order",
    "production_item": "FINISHED-001",
    "bom_no": "BOM-001",
    "qty": 10,
    "wip_warehouse": "WIP - MC",
    "fg_warehouse": "Finished Goods - MC",
    "company": "My Company Ltd"
})
wo.insert()
wo.submit()
```

### Transfer Materials
```python
wo = frappe.get_doc("Work Order", "WO-001")

# Create material transfer
from erpnext.manufacturing.doctype.work_order.work_order import make_stock_entry
se = make_stock_entry("WO-001", "Material Transfer for Manufacture", 10)
se.insert()
se.submit()
```

### Complete Production
```python
# Create manufacture entry
se = make_stock_entry("WO-001", "Manufacture", 10)
se.insert()
se.submit()
```

---

## Work Order Status

```
Draft → Submitted → In Progress → Completed
                     ↓
                   Stopped
```

---

## Related Topics
- [BOM](./01_bom.md)
- [Job Card](./04_job-card.md)
