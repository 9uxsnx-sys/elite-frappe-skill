# System Design Blueprints

Canonical architecture patterns for enterprise Frappe/ERPNext implementations.

---

## Blueprint 1: Multi-Company ERP Architecture

### Overview
Architecture for managing multiple companies/branches with consolidated reporting while maintaining strict data isolation.

```
┌─────────────────────────────────────────────────────────────────┐
│                    SHARED INFRASTRUCTURE                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │    Redis     │  │  MariaDB     │  │   Assets     │          │
│  │   Cache      │  │   Server     │  │   Storage    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                     FRAPPE FRAMEWORK                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              COMPANY ISOLATION LAYER                    │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│  │  │   Company    │  │   Company    │  │   Company    │  │   │
│  │  │     A        │  │     B        │  │     C        │  │   │
│  │  │  (Tenant 1)  │  │  (Tenant 2)  │  │  (Tenant 3)  │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              CONSOLIDATION LAYER                          │   │
│  │         (Cross-Company Reporting)                        │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Implementation

```python
# Multi-company architecture implementation

class MultiCompanyManager:
    """Manage multi-company ERP architecture."""
    
    def __init__(self):
        self.isolation_fields = ["company", "cost_center", "branch"]
    
    def get_company_scoped_query(self, doctype, filters=None, user=None):
        """Generate company-scoped query."""
        
        user = user or frappe.session.user
        user_companies = self._get_user_companies(user)
        
        # Build filter
        if isinstance(filters, dict):
            filters["company"] = ["in", user_companies]
        elif isinstance(filters, list):
            filters.append(["company", "in", user_companies])
        else:
            filters = {"company": ["in", user_companies]}
        
        return frappe.get_all(doctype, filters=filters)
    
    def validate_cross_company_write(self, doc, user=None):
        """Prevent writes to unauthorized companies."""
        
        user = user or frappe.session.user
        
        if not hasattr(doc, 'company'):
            return True
        
        user_companies = self._get_user_companies(user)
        
        if doc.company not in user_companies:
            frappe.throw(
                f"You cannot modify records for company {doc.company}",
                frappe.PermissionError
            )
    
    def consolidate_report(self, report_name, companies, date_range):
        """Generate consolidated cross-company report."""
        
        consolidated = []
        
        for company in companies:
            # Switch to company context
            frappe.defaults.set_user_default("company", company)
            
            # Generate report
            company_data = self._generate_company_report(
                report_name, company, date_range
            )
            consolidated.append(company_data)
        
        # Merge and aggregate
        return self._aggregate_consolidated(consolidated)
    
    def _get_user_companies(self, user):
        """Get companies user has access to."""
        
        user_doc = frappe.get_doc("User", user)
        
        if user_doc.get("companies"):
            return [c.company for c in user_doc.companies]
        
        default = frappe.db.get_value("User", user, "company")
        return [default] if default else []

# Controller integration
class CompanyIsolatedDocument(Document):
    """Base class for company-isolated documents."""
    
    def validate(self):
        # Enforce company scoping
        if self.is_new() and not self.company:
            self.company = frappe.defaults.get_user_default("company")
        
        MultiCompanyManager().validate_cross_company_write(self)
    
    def get_list_query(self, query):
        """Inject company filter into list queries."""
        
        user_companies = MultiCompanyManager()._get_user_companies(frappe.session.user)
        
        if user_companies:
            query = query.where(
                frappe.qb.Field("company").isin(user_companies)
            )
        
        return query
```

---

## Blueprint 2: Multi-Warehouse Inventory System

### Overview
Distributed inventory management across multiple warehouses with transfer capabilities and consolidated stock visibility.

```
┌─────────────────────────────────────────────────────────────────┐
│                    WAREHOUSE HIERARCHY                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────────────────────────────────────────┐     │
│   │                  ROOT (All Warehouses)               │     │
│   └─────────────────────┬───────────────────────────────┘     │
│                         │                                       │
│         ┌───────────────┼───────────────┐                     │
│         │               │               │                     │
│   ┌─────┴─────┐  ┌────┴────┐  ┌─────┴──────┐               │
│   │  Region A  │  │Region B │  │  Region C   │               │
│   └─────┬─────┘  └────┬────┘  └─────┬──────┘               │
│         │             │              │                        │
│   ┌─────┴─────┐  ┌────┴────┐  ┌─────┴──────┐               │
│   │ Warehouse │  │Warehouse│  │  Warehouse  │               │
│   │   A1      │  │   B1    │  │    C1       │               │
│   └───────────┘  └─────────┘  └─────────────┘               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    STOCK TRANSFER FLOW                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Source Warehouse ──► Transfer Order ──► In Transit ──►        │
│       (Stock Out)         (Draft)         (Submitted)           │
│                                                           │     │
│   Destination Warehouse ◄── Receipt ◄── Delivery ◄───────┘     │
│       (Stock In)                                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Implementation

```python
class MultiWarehouseInventoryManager:
    """Manage multi-warehouse inventory operations."""
    
    def get_stock_balance_consolidated(self, item_code, warehouse_group=None):
        """Get consolidated stock balance across warehouses."""
        
        if warehouse_group:
            warehouses = self._get_warehouses_in_group(warehouse_group)
        else:
            warehouses = None
        
        # Query stock ledger
        query = """
            SELECT 
                warehouse,
                SUM(actual_qty) as qty,
                AVG(valuation_rate) as rate
            FROM `tabBin`
            WHERE item_code = %s
            {warehouse_filter}
            GROUP BY warehouse
        """.format(
            warehouse_filter="AND warehouse IN %s" if warehouses else ""
        )
        
        params = [item_code]
        if warehouses:
            params.append(tuple(warehouses))
        
        results = frappe.db.sql(query, tuple(params), as_dict=True)
        
        return {
            "by_warehouse": {r.warehouse: r for r in results},
            "total_qty": sum(r.qty for r in results),
            "weighted_avg_rate": self._calculate_weighted_average(results)
        }
    
    def create_transfer_order(self, source, destination, items):
        """Create warehouse transfer order."""
        
        transfer = frappe.get_doc({
            "doctype": "Stock Entry",
            "stock_entry_type": "Material Transfer",
            "from_warehouse": source,
            "to_warehouse": destination,
            "items": [
                {
                    "item_code": item["item_code"],
                    "qty": item["qty"],
                    "s_warehouse": source,
                    "t_warehouse": destination
                }
                for item in items
            ]
        })
        
        transfer.insert()
        return transfer
    
    def get_transfer_in_transit(self, warehouse=None):
        """Get stock currently in transit."""
        
        filters = {"docstatus": 0, "stock_entry_type": "Material Transfer"}
        if warehouse:
            filters["from_warehouse"] = warehouse
        
        return frappe.get_all("Stock Entry",
            filters=filters,
            fields=["name", "from_warehouse", "to_warehouse", "posting_date"]
        )
    
    def _get_warehouses_in_group(self, group_warehouse):
        """Get all warehouses under a warehouse group."""
        
        # Recursive query to get child warehouses
        warehouses = [group_warehouse]
        
        children = frappe.get_all("Warehouse",
            filters={"parent_warehouse": group_warehouse},
            fields=["name"]
        )
        
        for child in children:
            warehouses.extend(self._get_warehouses_in_group(child.name))
        
        return warehouses
```

---

## Blueprint 3: Manufacturing-Heavy ERP

### Overview
Full manufacturing lifecycle management from BOM to Work Order to Job Card with capacity planning and shop floor control.

```
┌─────────────────────────────────────────────────────────────────┐
│              MANUFACTURING LIFECYCLE                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐       │
│  │     BOM     │───►│  Work Order │───►│   Job Card  │       │
│  │  (Recipe)   │    │  (Schedule) │    │ (Execution) │       │
│  └─────────────┘    └──────┬──────┘    └──────┬──────┘       │
│                            │                    │              │
│                            ▼                    ▼              │
│                     ┌─────────────┐    ┌─────────────┐       │
│                     │ Workstation │    │   Quality   │       │
│                     │ (Capacity)  │    │   Control   │       │
│                     └─────────────┘    └─────────────┘       │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    MATERIAL FLOW                         │  │
│  │                                                          │  │
│  │  Raw Materials ──► WIP ──► Finished Goods ──► Dispatch │  │
│  │                                                          │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Blueprint 4: High Transaction Accounting System

### Overview
Accounting architecture optimized for high transaction volumes with sub-ledger design and batch processing.

```
┌─────────────────────────────────────────────────────────────────┐
│              ACCOUNTING ARCHITECTURE                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  SUB-LEDGERS                             │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │   │
│  │  │  Sales   │ │ Purchase │ │  Stock   │ │  Payroll │   │   │
│  │  │  Ledger │ │  Ledger  │ │  Ledger  │ │  Ledger  │   │   │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘   │   │
│  │       │            │            │            │          │   │
│  │       └────────────┴────┬───────┴────────────┘          │   │
│  │                         │                              │   │
│  │                         ▼                              │   │
│  │              ┌─────────────────┐                        │   │
│  │              │   GL Entry      │                        │   │
│  │              │  (Consolidated) │                        │   │
│  │              └─────────────────┘                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              BATCH PROCESSING                            │   │
│  │                                                          │   │
│  │  Transaction ──► Queue ──► Batch Process ──► Post      │   │
│  │                                                          │   │
│  │  (Immediate)   (Redis)    (Background)    (GL Entry)     │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Blueprint 5: API-First ERP

### Overview
API-first architecture for headless ERP with external integrations, mobile apps, and third-party systems.

```
┌─────────────────────────────────────────────────────────────────┐
│                   API-FIRST ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    API GATEWAY                             │   │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐          │   │
│  │  │   REST    │  │  GraphQL  │  │  Webhook  │          │   │
│  │  │   API     │  │   API     │  │  Endpoint │          │   │
│  │  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘          │   │
│  │        └──────────────┼──────────────┘                │   │
│  │                       │                                │   │
│  │                       ▼                                │   │
│  │  ┌─────────────────────────────────────────────────┐  │   │
│  │  │           AUTHENTICATION LAYER                   │  │   │
│  │  │     (API Keys / OAuth2 / JWT Tokens)            │  │   │
│  │  └─────────────────────────────────────────────────┘  │   │
│  │                       │                                │   │
│  └───────────────────────┼────────────────────────────────┘   │
│                          │                                       │
│  ┌───────────────────────┼────────────────────────────────┐     │
│  │                       ▼                                │     │
│  │  ┌─────────────────────────────────────────────────┐     │     │
│  │  │              CORE ERP ENGINE                   │     │     │
│  │  │                                                 │     │     │
│  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐          │     │     │
│  │  │  │Accounting│ │  Sales  │ │  Stock  │          │     │     │
│  │  │  │  Module │ │  Module │ │  Module │          │     │     │
│  │  │  └─────────┘ └─────────┘ └─────────┘          │     │     │
│  │  └─────────────────────────────────────────────────┘     │     │
│  └─────────────────────────────────────────────────────────────┘     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Blueprint 6: SaaS ERP Model

### Overview
Multi-tenant SaaS architecture for hosting multiple client organizations on shared infrastructure.

```
┌─────────────────────────────────────────────────────────────────┐
│                   SAAS ERP ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              INFRASTRUCTURE LAYER                        │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │   │
│  │  │  Load    │  │  App     │  │  Worker  │  │   DB     │  │   │
│  │  │ Balancer │  │ Servers  │  │  Nodes   │  │  Cluster │  │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              TENANT ISOLATION LAYER                      │   │
│  │                                                         │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│  │  │   Tenant 1   │  │   Tenant 2   │  │   Tenant 3   │  │   │
│  │  │   Site A     │  │   Site B     │  │   Site C     │  │   │
│  │  │  (Client 1)  │  │  (Client 2)  │  │  (Client 3)  │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │   │
│  │                                                         │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│  │  │   Tenant N   │  │   Tenant N+1 │  │   Tenant N+2 │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              ORCHESTRATION LAYER                         │   │
│  │                                                         │   │
│  │  • Site Provisioning    • Backup Management             │   │
│  │  • Update Deployment    • Monitoring                   │   │
│  │  • Resource Scaling     • Billing Integration          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Blueprint 7: Vendor Portal System

### Overview
External vendor/supplier portal for purchase orders, invoices, and collaboration.

```
┌─────────────────────────────────────────────────────────────────┐
│                  VENDOR PORTAL ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────┐      ┌───────────────────────────┐   │
│  │    VENDOR PORTAL      │      │       MAIN ERP            │   │
│  │   (External Site)     │      │      (Internal)           │   │
│  │                       │      │                           │   │
│  │  ┌─────────────────┐  │      │  ┌─────────────────────┐  │   │
│  │  │  Portal User  │  │◄────►│  │   Purchase Module   │  │   │
│  │  │  (Vendor)       │  │      │  └─────────────────────┘  │   │
│  │  └─────────────────┘  │      │                           │   │
│  │                       │      │  ┌─────────────────────┐  │   │
│  │  • View POs          │      │  │   Supplier Master   │  │   │
│  │  • Submit Invoices   │      │  └─────────────────────┘  │   │
│  │  • Track Payments    │      │                           │   │
│  │  • Update Profile    │      │  ┌─────────────────────┐  │   │
│  │                       │      │  │   Accounting        │  │   │
│  └───────────────────────┘      │  └─────────────────────┘  │   │
│           │                       └───────────────────────────┘   │
│           │                       │                               │
│           └───────────────────────┘                               │
│              (API + Webhook Sync)                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Blueprint 8: Enterprise Reporting Layer

### Overview
Dedicated reporting architecture with data warehouse, OLAP cubes, and BI integration.

```
┌─────────────────────────────────────────────────────────────────┐
│              ENTERPRISE REPORTING ARCHITECTURE                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              OPERATIONAL ERP (OLTP)                      │   │
│  │                   (Source)                               │   │
│  └────────────────────────┬────────────────────────────────┘   │
│                           │                                      │
│                           │ ETL Process                          │
│                           │ (Daily/Real-time)                    │
│                           ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              DATA WAREHOUSE (OLAP)                       │   │
│  │                                                         │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │   │
│  │  │  Sales   │ │Purchase  │ │  Stock   │ │Financial │  │   │
│  │  │   Star   │ │   Star   │ │   Star   │ │   Star   │  │   │
│  │  │  Schema  │ │  Schema  │ │  Schema  │ │  Schema  │  │   │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘  │   │
│  │       │            │            │            │         │   │
│  │       └────────────┴────┬───────┴────────────┘         │   │
│  │                         │                              │   │
│  │                         ▼                              │   │
│  │  ┌─────────────────────────────────────────────────┐  │   │
│  │  │         CONSOLIDATED DATA MART                  │  │   │
│  │  └─────────────────────────────────────────────────┘  │   │
│  └────────────────────────┬────────────────────────────────┘   │
│                           │                                      │
│           ┌───────────────┼───────────────┐                      │
│           ▼               ▼               ▼                      │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │   Power BI   │ │   Tableau    │ │   Custom     │            │
│  │   Dashboard  │ │   Dashboard  │ │   Reports    │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Blueprint 9: Audit Logging Architecture

### Overview
Comprehensive audit logging for compliance, security, and forensic analysis.

```
┌─────────────────────────────────────────────────────────────────┐
│              AUDIT LOGGING ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │            APPLICATION LAYER                           │   │
│  │                                                         │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐             │   │
│  │  │ Create   │  │ Update   │  │ Delete   │             │   │
│  │  │  Event   │  │  Event   │  │  Event   │             │   │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘             │   │
│  │       │            │            │                       │   │
│  │       └────────────┴────┬───────┘                       │   │
│  │                        │                                │   │
│  │                        ▼                                │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │              AUDIT LOGGER                        │   │   │
│  │  │  • Capture User, Timestamp, IP                   │   │   │
│  │  │  • Record Before/After State                   │   │   │
│  │  │  • Hash for Tamper Detection                   │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  │                        │                                │   │
│  └────────────────────────┼────────────────────────────────┘   │
│                           │                                      │
│                           ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              AUDIT STORAGE                             │   │
│  │                                                         │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │  Primary: Immutable Log Store (Write-once)      │   │   │
│  │  │  Secondary: Time-series Database (Query)          │   │   │
│  │  │  Archive: Cold Storage (Compliance retention)     │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Summary: Blueprint Selection Guide

| Scenario | Recommended Blueprint | Key Considerations |
|----------|----------------------|-------------------|
| Multi-branch retail | Multi-Company + Multi-Warehouse | Company isolation, inter-branch transfers |
| Manufacturing SME | Manufacturing-Heavy | BOM complexity, capacity planning |
| Trading company | Multi-Warehouse + High Transaction | Inventory valuation, fast transactions |
| Enterprise group | Multi-Company + Reporting Layer | Consolidation, data warehouse |
| Service business | API-First | Project tracking, time billing |
| ERP SaaS provider | SaaS Model | Tenant isolation, provisioning |
| B2B portal | Vendor Portal | Supplier collaboration, self-service |
| Regulated industry | Audit Logging | Compliance, tamper-proof logs |
