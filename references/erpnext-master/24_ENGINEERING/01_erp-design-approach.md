# ERP System Design Approach

## Quick Reference
When designing ERP systems: analyze business processes → map to ERPNext modules → design DocTypes → configure workflows → implement integrations. Start with standard features, then customize.

## AI Prompt
\`\`\`
When designing an ERP system:
1. Understand business domain and processes
2. Map processes to ERPNext standard features
3. Identify gaps requiring customization
4. Design data model (DocTypes) first
5. Plan workflows and validations
6. Consider scalability and performance
\`\`\`

---

## Design Methodology

### Step 1: Domain Analysis
\`\`\`
Questions to ask:
- What business processes need support?
- Who are the users and their roles?
- What are the key entities?
- What reports are needed?
- What integrations are required?
\`\`\`

### Step 2: Process Mapping
\`\`\`
For each business process:
1. Document current workflow
2. Identify input/output
3. Map to ERPNext DocTypes
4. Identify custom requirements
5. Plan automation points
\`\`\`

### Step 3: Gap Analysis
\`\`\`
Compare requirements vs ERPNext capabilities:
- Standard features (80%): Use as-is
- Configuration (10%): Settings, workflows
- Customization (10%): Custom DocTypes, scripts
\`\`\`

---

## Design Framework

### Business Domain → Module Mapping

| Domain | ERPNext Module | Key DocTypes |
|--------|----------------|--------------|
| Sales | Selling, CRM | Lead, Quotation, SO, SI |
| Procurement | Buying | PO, PR, PI |
| Inventory | Stock | Item, Warehouse, SE |
| Accounting | Accounts | JE, PE, GL Entry |
| Manufacturing | Manufacturing | BOM, WO |
| HR | HR, Payroll | Employee, Salary Slip |
| Projects | Projects | Project, Task, Timesheet |

### Entity → DocType Design

\`\`\`
When designing new DocTypes:

1. Check if similar DocType exists
   - Can extend existing DocType?
   - Can use Custom Fields?

2. Define fields
   - What data to capture?
   - What validations needed?
   - What relationships?

3. Define relationships
   - Parent-child tables
   - Link fields to other DocTypes
   - Dynamic links (if needed)

4. Define behavior
   - Naming series
   - Controller hooks (validate, on_submit)
   - Permissions

5. Define integrations
   - REST API endpoints
   - Webhooks
   - External system sync
\`\`\`

---

## DocType Design Patterns

### Pattern 1: Master DocType
\`\`\`python
# Entity: Customer, Supplier, Item
# Characteristics:
# - No docstatus (always editable)
# - Used in transactions via Link field
# - May have hierarchy (groups)

# Example: Vehicle Fleet
{
    "doctype": "Vehicle",
    "vehicle_number": "MH-01-1234",
    "vehicle_type": "Truck",
    "capacity": 10,
    "status": "Active",
    "driver": "EMP-001"
}
\`\`\`

### Pattern 2: Transaction DocType
\`\`\`python
# Entity: Sales Invoice, Purchase Order
# Characteristics:
# - Has docstatus (Draft → Submitted → Cancelled)
# - Creates ledger entries
# - Linked to master records

# Example: Trip Log
{
    "doctype": "Trip Log",
    "vehicle": "VH-001",
    "trip_date": "2024-01-15",
    "start_km": 10000,
    "end_km": 10150,
    "fuel_consumed": 25,
    "status": "Draft"  # → Submitted
}

# On Submit: Create Fuel Entry, Update Vehicle KM
\`\`\`

### Pattern 3: Child Table
\`\`\`python
# Entity: Sales Invoice Item, Journal Entry Account
# Characteristics:
# - Part of parent document
# - No independent existence

# Example: Trip Log Expense
{
    "parent": "TRIP-001",
    "doctype": "Trip Log Expense",
    "expense_type": "Fuel",
    "amount": 2500,
    "remarks": "Diesel refill"
}
\`\`\`

### Pattern 4: Configuration DocType
\`\`\`python
# Entity: Settings, Configuration
# Characteristics:
# - Single record per company
# - Stores system configuration

# Example: Fleet Settings
{
    "doctype": "Fleet Settings",
    "default_fuel_rate": 100,
    "km_rate": 15,
    "maintenance_alert_days": 30
}
\`\`\`

---

## Workflow Design

### State Machine Model
\`\`\`
Draft → Pending Approval → Approved → Completed
                ↓
            Rejected → Draft (for revision)
\`\`\`

### ERPNext Workflow Configuration
\`\`\`
1. Create Workflow DocType
   - Define states
   - Define transitions
   - Assign approvers

2. Link to DocType
   - Enable workflow
   - Set initial state

3. Configure notifications
   - On state change
   - Email alerts
\`\`\`

---

## Integration Design

### Inbound Integration
\`\`\`
External System → ERPNext

Options:
1. REST API
   - POST /api/resource/[DocType]
   - Requires API Key/Token

2. Webhook Receiver
   - Create custom endpoint
   - Process payload
   - Create/update records

3. File Import
   - CSV/Excel import
   - Scheduled processing
\`\`\`

### Outbound Integration
\`\`\`
ERPNext → External System

Options:
1. Webhooks
   - On document events
   - POST to external URL

2. Custom API
   - @frappe.whitelist() method
   - External system calls

3. Scheduled Sync
   - Background job
   - Batch processing
\`\`\`

---

## Scalability Considerations

### Database
- Index frequently queried fields
- Archive old data
- Use read replicas for reporting

### Application
- Background jobs for heavy operations
- Cache frequently accessed data
- Optimize queries

### Infrastructure
- Horizontal scaling for web workers
- Separate database server
- CDN for static assets

---

## Example: Designing a Fleet Management System

### Domain Analysis
\`\`\`
Processes:
- Vehicle registration
- Trip logging
- Fuel management
- Maintenance scheduling
- Driver assignment
- Cost tracking
\`\`\`

### Module Design
\`\`\`
fleet_management/
├── doctype/
│   ├── vehicle/
│   ├── trip_log/
│   ├── fuel_entry/
│   ├── maintenance_log/
│   └── driver/
├── report/
│   ├── vehicle_cost_report/
│   └── fuel_efficiency_report/
└── hooks.py
\`\`\`

### DocType Design
\`\`\`
Vehicle (Master)
├── vehicle_number (Primary)
├── vehicle_type (Link to Vehicle Type)
├── driver (Link to Driver/Employee)
├── status (Active/Maintenance/Retired)
└── current_km (Updated by Trip Log)

Trip Log (Transaction)
├── vehicle (Link to Vehicle)
├── driver (Link to Driver)
├── trip_date
├── start_km / end_km
├── fuel_consumed
├── expenses (Child Table)
└── status (Draft/Submitted)

Fuel Entry (Transaction)
├── vehicle (Link to Vehicle)
├── fuel_date
├── fuel_type
├── quantity
├── rate
├── amount
└── odometer_reading
\`\`\`

### Automation Points
\`\`\`python
# On Trip Log submit:
1. Update Vehicle current_km
2. Create Fuel Entry if fuel consumed
3. Check maintenance due
4. Calculate cost per km

# On Fuel Entry submit:
1. Create Stock Entry (fuel is item)
2. Update Vehicle odometer
3. Create GL Entry for fuel expense
\`\`\`

---

## Related Topics
- [Module Design](./02_module-design.md)
- [Process Mapping](./03_process-mapping.md)
- [Customization Strategy](./04_customization-strategy.md)
