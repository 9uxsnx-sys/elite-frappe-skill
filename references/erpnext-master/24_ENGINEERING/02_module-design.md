# Module Design

## Quick Reference
Design custom modules for ERPNext. Follow standard patterns for DocTypes, controllers, and hooks.

## AI Prompt
```
When designing a module:
1. Identify all entities and relationships
2. Design DocTypes with proper fields
3. Plan workflows and validations
4. Consider reporting needs
5. Plan for integrations
```

---

## Module Structure

```
custom_app/
├── custom_app/
│   ├── fleet/                    # Custom module
│   │   ├── doctype/
│   │   │   ├── vehicle/
│   │   │   │   ├── vehicle.py
│   │   │   │   ├── vehicle.json
│   │   │   │   └── vehicle.js
│   │   │   └── trip_log/
│   │   ├── report/
│   │   │   └── vehicle_cost/
│   │   └── page/
│   │       └── fleet_dashboard/
│   └── hooks.py
```

---

## DocType Design

### Master DocType
```python
# vehicle.json
{
    "item_code": "Data",
    "vehicle_type": "Link",
    "registration_no": "Data",
    "status": "Select",
    "current_km": "Float"
}
```

### Transaction DocType
```python
# trip_log.json
{
    "vehicle": "Link",
    "trip_date": "Date",
    "start_km": "Float",
    "end_km": "Float",
    "items": "Table"  # Child table
}
```

---

## Module Registration

```python
# In hooks.txt (for module discovery)
custom_app.fleet
```

---

## Related Topics
- [ERP Design Approach](./01_erp-design-approach.md)
- [Customization Strategy](./04_customization-strategy.md)
