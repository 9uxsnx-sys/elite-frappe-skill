# Bill of Materials (BOM)

## Quick Reference
BOM defines the components and operations needed to manufacture a product. Contains raw materials, quantities, and routing through workstations.

## AI Prompt
```
When creating BOMs:
1. Define correct quantities and units
2. Set up routing and operations
3. Calculate cost accurately
4. Consider multiple BOMs for variants
5. Set default BOM for production
```

---

## BOM DocType

### Key Fields
| Field | Type | Description |
|-------|------|-------------|
| item | Link | Finished product |
| quantity | Float | Output quantity |
| uom | Link | Unit of measure |
| items | Table | Raw materials |
| operations | Table | Manufacturing operations |
| is_active | Check | Active BOM |
| is_default | Check | Default for item |

---

## Creating BOM

### Basic BOM
```python
bom = frappe.get_doc({
    "doctype": "BOM",
    "item": "FINISHED-001",
    "quantity": 1,
    "uom": "Nos",
    "items": [
        {"item_code": "RAW-001", "qty": 2, "rate": 100},
        {"item_code": "RAW-002", "qty": 1, "rate": 50}
    ]
})
bom.insert()
```

### BOM with Operations
```python
bom = frappe.get_doc({
    "doctype": "BOM",
    "item": "FINISHED-001",
    "quantity": 1,
    "items": [
        {"item_code": "RAW-001", "qty": 2}
    ],
    "operations": [
        {"operation": "Cutting", "workstation": "WS-001", "time_in_mins": 30},
        {"operation": "Assembly", "workstation": "WS-002", "time_in_mins": 60}
    ]
})
bom.insert()
```

---

## BOM Costing

### Get BOM Cost
```python
bom = frappe.get_doc("BOM", "BOM-001")
print(f"Material Cost: {bom.total_rm_cost}")
print(f"Operation Cost: {bom.total_op_cost}")
print(f"Total Cost: {bom.total_cost}")
```

### Update BOM Rates
```python
bom = frappe.get_doc("BOM", "BOM-001")
bom.update_cost()
bom.save()
```

---

## BOM API

### Get Default BOM
```python
default_bom = frappe.db.get_value("BOM",
    {"item": "FINISHED-001", "is_default": 1, "is_active": 1},
    "name"
)
```

### Get BOM Items
```python
bom = frappe.get_doc("BOM", "BOM-001")
for item in bom.items:
    print(f"{item.item_code}: {item.qty} {item.uom}")
```

---

## Related Topics
- [Work Order](./02_work-order.md)
- [Production Plan](./03_production-plan.md)
