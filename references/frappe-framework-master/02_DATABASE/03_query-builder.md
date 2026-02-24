# Query Builder

## Quick Reference
Frappe Query Builder (frappe.qb) provides a fluent interface for building SQL queries. Type-safe and cleaner than raw SQL.

## AI Prompt
```
When using Query Builder:
1. Import from frappe.query_builder
2. Use DocType to reference tables
3. Chain methods for complex queries
4. Use .run() to execute
5. Pass as_dict=True for dict results
```

---

## Basic Usage

```python
from frappe.query_builder import DocType

Task = DocType("Task")

# Select all
query = frappe.qb.from_(Task).select("*")
results = query.run(as_dict=True)

# Select specific fields
query = (
    frappe.qb.from_(Task)
    .select(Task.name, Task.subject, Task.status)
    .where(Task.status == "Open")
)
results = query.run(as_dict=True)
```

---

## Where Clauses

```python
from frappe.query_builder import DocType

Task = DocType("Task")

# Simple where
query = frappe.qb.from_(Task).select("*").where(Task.status == "Open")

# Multiple conditions (AND)
query = (
    frappe.qb.from_(Task)
    .select("*")
    .where(Task.status == "Open")
    .where(Task.priority == "High")
)

# OR condition
query = (
    frappe.qb.from_(Task)
    .select("*")
    .where(
        (Task.status == "Open") | (Task.status == "In Progress")
    )
)

# IN condition
query = (
    frappe.qb.from_(Task)
    .select("*")
    .where(Task.status.isin(["Open", "In Progress"]))
)

# LIKE condition
query = (
    frappe.qb.from_(Task)
    .select("*")
    .where(Task.subject.like("%important%"))
)

# Comparison
query = (
    frappe.qb.from_(Task)
    .select("*")
    .where(Task.due_date > "2024-01-01")
)
```

---

## Joins

```python
Task = DocType("Task")
Project = DocType("Project")

# Inner join
query = (
    frappe.qb.from_(Task)
    .join(Project)
    .on(Task.project == Project.name)
    .select(Task.name, Task.subject, Project.project_name)
)

# Left join
query = (
    frappe.qb.from_(Task)
    .left_join(Project)
    .on(Task.project == Project.name)
    .select(Task.name, Project.project_name)
)
```

---

## Aggregation

```python
from frappe.query_builder import Count, Sum, Avg

Task = DocType("Task")

# Count
query = (
    frappe.qb.from_(Task)
    .select(Count("*").as_("total"))
    .where(Task.status == "Open")
)

# Group by
query = (
    frappe.qb.from_(Task)
    .select(Task.status, Count("*").as_("count"))
    .groupby(Task.status)
)

# Sum
query = (
    frappe.qb.from_(Task)
    .select(Sum(Task.estimated_hours).as_("total_hours"))
)
```

---

## Order By and Limit

```python
Task = DocType("Task")

# Order by
query = (
    frappe.qb.from_(Task)
    .select("*")
    .orderby(Task.creation, order=frappe.qb.desc)
)

# Limit
query = (
    frappe.qb.from_(Task)
    .select("*")
    .limit(10)
    .offset(20)
)
```

---

## Subqueries

```python
Task = DocType("Task")
Project = DocType("Project")

# Subquery
subquery = (
    frappe.qb.from_(Project)
    .select(Project.name)
    .where(Project.status == "Active")
)

query = (
    frappe.qb.from_(Task)
    .select("*")
    .where(Task.project.isin(subquery))
)
```

---

## Related Topics
- [ORM Basics](./01_orm-basics.md)
