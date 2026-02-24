# System Design Approach

## Quick Reference
When designing Frappe applications: identify entities → design DocTypes → define relationships → implement controllers → add permissions.

## AI Prompt
```
When designing a system:
1. Identify all entities and relationships
2. Design DocTypes with proper field types
3. Configure permissions and workflows
4. Implement business logic in controllers
5. Plan for scale and maintenance
```

---

## Design Process

### Step 1: Requirements Analysis
```
Questions:
- What entities need to be tracked?
- What are the relationships between entities?
- What workflows are needed?
- Who are the users and their roles?
- What reports are required?
```

### Step 2: Entity Modeling
```
For each entity:
1. Is it a master (configuration) or transaction?
2. What fields does it need?
3. What validations are required?
4. What relationships does it have?
```

### Step 3: DocType Design
```
Design decisions:
- Single vs Hierarchical (is_tree)
- Submittable vs Simple (is_submittable)
- Child table vs Separate DocType
- Naming strategy
```

### Step 4: Relationship Design
```
Relationship types:
- Link field (foreign key)
- Child table (one-to-many)
- Dynamic Link (polymorphic)
```

---

## DocType Design Patterns

### Master DocType
```python
# Configuration/reference data
# Example: Customer, Item, Warehouse

{
    "is_submittable": 0,
    "is_tree": 0,
    "naming_series": None,
    "fields": [
        {"fieldname": "name", "fieldtype": "Data"},
        {"fieldname": "is_active", "fieldtype": "Check"}
    ]
}
```

### Transaction DocType
```python
# Business transactions
# Example: Sales Invoice, Purchase Order

{
    "is_submittable": 1,
    "fields": [
        {"fieldname": "posting_date", "fieldtype": "Date"},
        {"fieldname": "items", "fieldtype": "Table"},
        {"fieldname": "grand_total", "fieldtype"
