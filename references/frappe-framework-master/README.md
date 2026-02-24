# Frappe Framework Master Skill

## Purpose
This skill folder contains comprehensive knowledge for mastering Frappe Framework - a full-stack web framework for building database-driven applications. It enables AI agents to design, develop, debug, and deploy Frappe-based applications.

## Quick Navigation

### Foundation
- [00_FOUNDATION](./00_FOUNDATION/) - Architecture, Installation, Directory Structure

### Core System
- [01_CORE_SYSTEM](./01_CORE_SYSTEM/) - DocTypes, Controllers, Hooks, Modules

### Database
- [02_DATABASE](./02_DATABASE/) - ORM, Queries, Migrations, Relationships

### API
- [03_API](./03_API/) - REST API, Python API, JavaScript API, Whitelisted Methods

### Frontend
- [04_HOOKS_SYSTEM](./04_HOOKS_SYSTEM/) - All hooks and events
- [05_FRONTEND](./05_FRONTEND/) - Desk UI, Form Scripts, Controls

### Web
- [06_WEB_PORTAL](./06_WEB_PORTAL/) - Portal, Web Forms, Website
- [07_PRINTING](./07_PRINTING/) - Print Formats, PDF Generation

### Security
- [08_PERMISSIONS_SECURITY](./08_PERMISSIONS_SECURITY/) - Roles, Permissions, Authentication

### Operations
- [09_BACKGROUND_JOBS](./09_BACKGROUND_JOBS/) - Scheduler, Workers, Queues
- [10_INTEGRATIONS](./10_INTEGRATIONS/) - Webhooks, OAuth, External APIs
- [11_REPORTING](./11_REPORTING/) - Query Reports, Script Reports
- [12_CACHING](./12_CACHING/) - Redis, Cache Strategies

### Development
- [13_WORKFLOWS](./13_WORKFLOWS/) - Workflow configuration
- [14_TESTING](./14_TESTING/) - Unit, Integration, UI Testing
- [15_DEPLOYMENT](./15_DEPLOYMENT/) - Production, SSL, Multitenancy

### Advanced
- [16_DEBUGGING](./16_DEBUGGING/) - Errors, Troubleshooting
- [17_PATTERNS](./17_PATTERNS/) - Design Patterns, Best Practices
- [18_ENGINEERING](./18_ENGINEERING/) - System Design, Scalability
- [19_ELITE_SKILLS](./19_ELITE_SKILLS/) - Architecture Decisions, Security Audit

### Templates
- [20_TEMPLATES](./20_TEMPLATES/) - Code templates

---

## AI System Prompt

```
You are a Frappe Framework expert with deep knowledge of:
1. DocType system and meta-programming
2. Controller hooks and document lifecycle
3. ORM and database operations
4. REST API and whitelisted methods
5. Frontend (Desk, Form Scripts, Vue.js)
6. Permissions and security
7. Background jobs and caching
8. Best practices for scalable applications

When given a system idea:
1. Design DocTypes with proper relationships
2. Implement controllers with lifecycle hooks
3. Create APIs with proper authentication
4. Add validations and business logic
5. Consider permissions and security
```

## Prerequisite Knowledge

- Python 3.10+
- JavaScript/ES6
- MariaDB/MySQL
- Redis
- Basic web development

## Key Concepts

### DocType
The core building block. Defines:
- Database schema (fields, types)
- Form UI (layout, controls)
- Controller (Python class)
- Permissions

### Document Lifecycle
```
before_insert → validate → before_save → on_update → after_insert
                                    ↓
                              on_submit (if submittable)
                                    ↓
                              on_cancel
```

### Hooks
Extend framework behavior without modifying core:
```python
# hooks.py
doc_events = {
    "Sales Invoice": {
        "on_submit": "app.handlers.invoice_submitted"
    }
}
```

### ORM
```python
# Create
doc = frappe.get_doc({"doctype": "Task", "subject": "Test"})
doc.insert()

# Read
doc = frappe.get_doc("Task", "TASK-001")

# Update
doc.status = "Completed"
doc.save()

# Delete
doc.delete()

# Query
tasks = frappe.get_all("Task", fields=["name", "subject"])
```

---

## How to Use This Skill

1. **For Learning**: Start with `00_FOUNDATION/`, then explore specific topics
2. **For Development**: Reference specific files for patterns and examples
3. **For Debugging**: Use `16_DEBUGGING/` for troubleshooting
4. **For Architecture**: Use `18_ENGINEERING/` for system design

## Version Compatibility

This skill covers Frappe Framework Version 14-15+ (2024-2026).

## Related Skills
- **ERPNext**: `C:\skills\erpnext-master\` - ERP application built on Frappe
