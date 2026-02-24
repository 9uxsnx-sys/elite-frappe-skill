# Warehouse

## Quick Reference
Warehouse is a storage location for inventory. Can be hierarchical (parent-child). Linked to accounts for stock valuation. Each company has its own warehouses.

## AI Prompt
```
When setting up warehouses:
1. Plan hierarchy (Stores, FG, RM, WIP)
2. Link to correct stock account
3. Set default for items
4. Consider multi-location setup
5. Configure transfer rules
```

---

## Warehouse DocType

### Key Fields
| Field | Type | Description |
|-------|------|-------------|
| warehouse_name | Data | Warehouse name |
| company | Link | Company |
| parent_warehouse | Link | Parent in hierarchy |
| account | Link | Stock account |
| is_group | Check | Has children |

---

## Creating Warehouse

### Basic Warehouse
```python
wh = frappe.get_doc({
    "doctype": "Warehouse",
    "warehouse_name": "Stores",
    "company": "My Company Ltd",
    "account": "Stock Assets - MC"
})
wh.insert()
```

### Hierarchical Structure
```python
# Parent
parent = frappe.get_doc({
    "doctype": "Warehouse",
    "warehouse_name": "All Warehouses",
    "company": "My Company Ltd",
    "is_group": 1
})
parent.insert()

# Children
stores = frappe.get_doc({
    "doctype": "Warehouse",
    "warehouse_name": "Stores",
    "parent_warehouse": "All Warehouses - MC",
    "account": "Stock Assets - MC"
})
stores.insert()

fg = frappe.get_doc({
    "doctype": "Warehouse",
    "warehouse_name": "Finished Goods",
    "parent_warehouse": "All Warehouses - MC",
    "account": "Stock Assets - MC"
})
fg.insert()
```

---

## Common Patterns

### Get Stock in Warehouse
```python
from erpnext.stock.utils import get_stock_balance

balance = get_stock_balance("ITEM-001", "Stores - MC")
```

### Get All Warehouses for Company
```python
warehouses = frappe.get_all("Warehouse",
    filters={"company": "My Company Ltd", "is_group": 0},
    fields=["name", "warehouse_name"]
)
```

---

## Related Topics
- [Stock Entry](./02_stock-entry.md)
- [Stock Ledger](./03_stock-ledger.md)
