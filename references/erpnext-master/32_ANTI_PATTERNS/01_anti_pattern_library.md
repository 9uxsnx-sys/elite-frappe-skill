# Anti-Pattern Library — Detection & Correction

Complete reference for identifying, detecting, and correcting common Frappe/ERPNext anti-patterns.

---

## Anti-Pattern 1: Fat DocType

### Symptoms
- More than 80-100 fields in a single DocType
- Mixed concerns (master data + transaction data + configuration)
- Slow form loading (>2 seconds)
- Permission complexity explosion
- `tabDocField` queries dominating performance logs

### Why It's Wrong
| Issue | Impact |
|-------|--------|
| Database table bloat | Slower INSERT/UPDATE operations |
| Form UI unusability | Users scroll excessively |
| Permission explosion | Role-permission matrix becomes unmanageable |
| Memory overhead | Each document loads all fields |
| Validation complexity | `validate()` method becomes unmaintainable |

### Detection Script
```python
import frappe

def detect_fat_doctypes(threshold=80):
    """Detect DocTypes with excessive field counts."""
    results = []
    
    doctypes = frappe.get_all("DocType", 
        filters={"issingle": 0, "istable": 0},
        fields=["name", "module"])
    
    for dt in doctypes:
        field_count = frappe.db.count("DocField", 
            filters={"parent": dt.name, "parenttype": "DocType"})
        
        if field_count > threshold:
            results.append({
                "doctype": dt.name,
                "module": dt.module,
                "field_count": field_count,
                "severity": "CRITICAL" if field_count > 150 else "HIGH"
            })
    
    return sorted(results, key=lambda x: x["field_count"], reverse=True)

# Usage
fat_doctypes = detect_fat_doctypes(80)
for dt in fat_doctypes:
    print(f"🚨 {dt['severity']}: {dt['doctype']} has {dt['field_count']} fields")
```

### Correction Strategy

#### Phase 1: Analysis
```python
def analyze_doctype_structure(doctype_name):
    """Categorize fields by purpose."""
    meta = frappe.get_meta(doctype_name)
    
    categories = {
        "core_identity": [],      # name, naming_series
        "master_data": [],        # customer, item, supplier
        "transactional": [],      # qty, rate, amount, status
        "configuration": [],      # flags, settings, options
        "computed": [],           # formula fields, totals
        "metadata": [],           # creation, modified, owner
        "custom": []              # custom_* fields
    }
    
    for field in meta.fields:
        if field.fieldname.startswith("custom_"):
            categories["custom"].append(field.fieldname)
        elif field.fieldname in ["name", "naming_series", "title"]:
            categories["core_identity"].append(field.fieldname)
        elif field.fieldtype == "Link":
            categories["master_data"].append(field.fieldname)
        elif field.fieldtype in ["Float", "Currency", "Int"] and field.read_only:
            categories["computed"].append(field.fieldname)
        elif field.fieldname in ["creation", "modified", "modified_by", "owner"]:
            categories["metadata"].append(field.fieldname)
        elif field.fieldtype in ["Check", "Select"]:
            categories["configuration"].append(field.fieldname)
        else:
            categories["transactional"].append(field.fieldname)
    
    return categories
```

#### Phase 2: Decomposition

**WRONG: Monolithic DocType**
```python
# projects/doctype/project/project.json - 180 fields
{
    "name": "Project",
    "fields": [
        # Core (3)
        {"fieldname": "naming_series"},
        {"fieldname": "project_name"},
        {"fieldname": "status"},
        # Customer (15)
        {"fieldname": "customer"},
        {"fieldname": "customer_name"},
        # ... 15 customer-related fields
        # Budget (25)
        {"fieldname": "estimated_cost"},
        {"fieldname": "actual_cost"},
        # ... 25 budget fields
        # Tasks (40)
        {"fieldname": "task_1"},
        {"fieldname": "task_2"},
        # ... 40 task fields
        # Resources (30)
        {"fieldname": "project_manager"},
        # ... 30 resource fields
        # Billing (25)
        {"fieldname": "billing_method"},
        # ... 25 billing fields
        # Milestones (20)
        {"fieldname": "milestone_1"},
        # ... 20 milestone fields
        # Documents (15)
        {"fieldname": "contract_doc"},
        # ... 15 document references
        # Notes (17)
        {"fieldname": "internal_notes"}
        # ... 17 note fields
    ]
}
```

**CORRECT: Decomposed Architecture**
```python
# projects/doctype/project/project.json - 20 fields (core only)
{
    "name": "Project",
    "fields": [
        {"fieldname": "naming_series", "label": "Naming Series"},
        {"fieldname": "project_name", "label": "Project Name", "reqd": 1},
        {"fieldname": "status", "label": "Status", "fieldtype": "Select"},
        {"fieldname": "project_type", "label": "Type", "fieldtype": "Link", "options": "Project Type"},
        {"fieldname": "customer", "label": "Customer", "fieldtype": "Link", "options": "Customer"},
        {"fieldname": "expected_start_date", "label": "Expected Start", "fieldtype": "Date"},
        {"fieldname": "expected_end_date", "label": "Expected End", "fieldtype": "Date"},
        {"fieldname": "department", "label": "Department", "fieldtype": "Link", "options": "Department"},
        {"fieldname": "project_manager", "label": "Project Manager", "fieldtype": "Link", "options": "User"},
        {"fieldname": "notes", "label": "Notes", "fieldtype": "Text Editor"}
    ]
}

# projects/doctype/project_budget/project_budget.json
{
    "name": "Project Budget",
    "fields": [
        {"fieldname": "project", "label": "Project", "fieldtype": "Link", "options": "Project", "reqd": 1},
        {"fieldname": "budget_category", "label": "Category", "fieldtype": "Select"},
        {"fieldname": "estimated_amount", "label": "Estimated", "fieldtype": "Currency"},
        {"fieldname": "actual_amount", "label": "Actual", "fieldtype": "Currency"},
        {"fieldname": "variance", "label": "Variance", "fieldtype": "Currency", "read_only": 1}
    ]
}

# projects/doctype/project_resource/project_resource.json
{
    "name": "Project Resource",
    "fields": [
        {"fieldname": "project", "label": "Project", "fieldtype": "Link", "options": "Project"},
        {"fieldname": "resource_type", "label": "Type", "fieldtype": "Select", "options": "Employee\nEquipment\nContractor"},
        {"fieldname": "resource", "label": "Resource", "fieldtype": "Dynamic Link", "options": "resource_type"},
        {"fieldname": "allocation_percentage", "label": "Allocation %", "fieldtype": "Percent"},
        {"fieldname": "from_date", "label": "From", "fieldtype": "Date"},
        {"fieldname": "to_date", "label": "To", "fieldtype": "Date"}
    ]
}

# projects/doctype/project_milestone/project_milestone.json
{
    "name": "Project Milestone",
    "fields": [
        {"fieldname": "project", "label": "Project", "fieldtype": "Link", "options": "Project"},
        {"fieldname": "milestone_name", "label": "Milestone", "reqd": 1},
        {"fieldname": "target_date", "label": "Target Date", "fieldtype": "Date"},
        {"fieldname": "actual_date", "label": "Actual Date", "fieldtype": "Date"},
        {"fieldname": "status", "label": "Status", "fieldtype": "Select", "options": "Pending\nIn Progress\nCompleted\nDelayed"}
    ]
}

# projects/doctype/project_document/project_document.json
{
    "name": "Project Document",
    "fields": [
        {"fieldname": "project", "label": "Project", "fieldtype": "Link", "options": "Project"},
        {"fieldname": "document_type", "label": "Type", "fieldtype": "Select", "options": "Contract\nSOW\nProposal\nInvoice\nOther"},
        {"fieldname": "document", "label": "Document", "fieldtype": "Attach"},
        {"fieldname": "uploaded_by", "label": "Uploaded By", "fieldtype": "Link", "options": "User"},
        {"fieldname": "uploaded_on", "label": "Uploaded On", "fieldtype": "Datetime"}
    ]
}
```

#### Phase 3: Migration Script
```python
import frappe
from frappe import _

def migrate_fat_project_to_decomposed():
    """
    Migrate legacy Project records to decomposed structure.
    Run as: bench --site site.com execute projects.migrate.migrate_fat_project_to_decomposed
    """
    frappe.db.savepoint("migration_start")
    
    try:
        legacy_projects = frappe.get_all("Project", fields=["*"])
        
        for idx, legacy in enumerate(legacy_projects):
            # Create Project Budget records
            if legacy.estimated_cost:
                frappe.get_doc({
                    "doctype": "Project Budget",
                    "project": legacy.name,
                    "budget_category": "Overall",
                    "estimated_amount": legacy.estimated_cost,
                    "actual_amount": legacy.actual_cost or 0
                }).insert()
            
            # Migrate milestones
            for i in range(1, 21):
                milestone_field = f"milestone_{i}"
                if legacy.get(milestone_field):
                    frappe.get_doc({
                        "doctype": "Project Milestone",
                        "project": legacy.name,
                        "milestone_name": legacy.get(milestone_field),
                        "target_date": legacy.get(f"milestone_{i}_date")
                    }).insert()
            
            # Commit every 100 records
            if idx % 100 == 0:
                frappe.db.commit()
                print(f"Migrated {idx + 1}/{len(legacy_projects)} projects")
        
        frappe.db.commit()
        print("✅ Migration completed successfully")
        
    except Exception as e:
        frappe.db.rollback(save_point="migration_start")
        frappe.throw(f"Migration failed: {str(e)}")
```

---

## Anti-Pattern 2: Logic Inside Client Script

### Symptoms
- JavaScript files > 200 lines
- Complex calculations in `frm.set_value()`
- Business rules in `.js` files
- `validate()` bypassed through client-side manipulation

### Why It's Wrong
| Issue | Impact |
|-------|--------|
| Security vulnerability | User can manipulate client-side values |
| No audit trail | Actions not logged on server |
| API inconsistency | Behavior differs between UI and API calls |
| Testing impossibility | Can't unit test client logic |
| Bypassed validation | Server-side validation still required |

### Detection Script
```python
import os
import re

def detect_client_logic_bloat(app_path, threshold_lines=50, threshold_calculation=10):
    """Detect excessive business logic in client scripts."""
    results = []
    
    js_path = os.path.join(app_path, "public", "js")
    if not os.path.exists(js_path):
        return results
    
    for filename in os.listdir(js_path):
        if not filename.endswith('.js'):
            continue
            
        filepath = os.path.join(js_path, filename)
        with open(filepath, 'r') as f:
            content = f.read()
            lines = content.split('\n')
            
            # Detect calculation patterns
            calc_patterns = [
                r'frm\.doc\.[\w_]+\s*[\+\-\*/%]\s*',  # Arithmetic on frm.doc
                r'calculate\w*\s*\(',  # calculate functions
                r'flt\(.*\)\s*[\+\-\*/%]',  # Frappe float calculations
                r'sum\(|total\s*=',  # Aggregation
                r'discount|tax|vat|amount',  # Financial calculations
                r'\.toFixed\(|Number\(|parseFloat\('  # Type conversions
            ]
            
            calculation_lines = 0
            for line in lines:
                for pattern in calc_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        calculation_lines += 1
                        break
            
            if len(lines) > threshold_lines or calculation_lines > threshold_calculation:
                results.append({
                    "file": filename,
                    "total_lines": len(lines),
                    "calculation_lines": calculation_lines,
                    "severity": "CRITICAL" if calculation_lines > 20 else "HIGH"
                })
    
    return results
```

### Correction Strategy

**WRONG: Business logic in client script**
```javascript
// custom_app/public/js/sales_invoice.js - 150 lines
frappe.ui.form.on('Sales Invoice', {
    items_on_form_rendered: function(frm) {
        calculate_totals(frm);
    },
    
    discount_percentage: function(frm) {
        // Complex business logic - WRONG!
        var total = 0;
        for (var i = 0; i < frm.doc.items.length; i++) {
            var item = frm.doc.items[i];
            var item_total = flt(item.qty) * flt(item.rate);
            
            // Apply item-level discount
            if (item.discount_percentage) {
                item_total = item_total * (1 - flt(item.discount_percentage) / 100);
            }
            
            // Apply tax
            var tax_amount = item_total * 0.15;  // Hard-coded VAT!
            item.total_with_tax = item_total + tax_amount;
            
            total += item.total_with_tax;
        }
        
        // Apply document-level discount
        if (frm.doc.discount_percentage) {
            total = total * (1 - flt(frm.doc.discount_percentage) / 100);
        }
        
        // Add shipping
        if (frm.doc.shipping_amount) {
            total += flt(frm.doc.shipping_amount);
        }
        
        frm.set_value('grand_total', total);
        frm.set_value('rounded_total', Math.round(total));
        
        // Validate credit limit
        if (total > 100000) {
            frappe.show_alert('Large order - requires approval');
        }
        
        frm.refresh_fields(['items', 'grand_total', 'rounded_total']);
    }
});
```

**CORRECT: Server-side logic with client trigger**
```javascript
// custom_app/public/js/sales_invoice.js - 30 lines
frappe.ui.form.on('Sales Invoice', {
    discount_percentage: function(frm) {
        // Just trigger server calculation
        frm.save();  // Server handles all logic
    },
    
    refresh: function(frm) {
        // UI-only: Add approval button for large orders
        if (frm.doc.grand_total > 100000 && !frm.doc.approved) {
            frm.add_custom_button(__('Request Approval'), function() {
                frappe.call({
                    method: 'custom_app.api.request_approval',
                    args: { invoice: frm.doc.name },
                    callback: function(r) {
                        frm.reload_doc();
                    }
                });
            });
        }
    }
});
```

```python
# custom_app/sales_invoice_extension.py
import frappe
from frappe import _
from frappe.utils import flt

class CustomSalesInvoice:
    def validate(self):
        """All business logic lives here."""
        self.calculate_totals()
        self.validate_credit_limit()
        self.apply_tax_rules()
    
    def calculate_totals(self):
        """Server-side calculation with full audit trail."""
        total = 0
        
        for item in self.doc.items:
            # Get tax template from item master
            tax_template = frappe.get_cached_doc("Item Tax Template", item.item_tax_template)
            tax_rate = sum(tax.tax_rate for tax in tax_template.taxes) if tax_template else 0
            
            # Calculate item total
            item.amount = flt(item.qty) * flt(item.rate)
            
            # Apply item-level discount
            if item.discount_percentage:
                item.amount = item.amount * (1 - flt(item.discount_percentage) / 100)
            
            # Calculate tax
            item.tax_amount = item.amount * (tax_rate / 100)
            item.total_with_tax = item.amount + item.tax_amount
            
            total += item.total_with_tax
        
        # Apply document-level discount
        if self.doc.discount_percentage:
            total = total * (1 - flt(self.doc.discount_percentage) / 100)
        
        # Add shipping from company settings
        shipping = self.get_shipping_cost()
        total += shipping
        
        self.doc.grand_total = total
        self.doc.rounded_total = round(total)
    
    def validate_credit_limit(self):
        """Enforced server-side - cannot be bypassed."""
        customer = frappe.get_cached_doc("Customer", self.doc.customer)
        
        if self.doc.grand_total > customer.credit_limit:
            if not frappe.has_permission("Sales Invoice", "submit", self.doc):
                frappe.throw(_(
                    "Order exceeds credit limit. "
                    "Requires Sales Manager approval."
                ))
```

---

## Anti-Pattern 3: Business Logic in Controller

### Symptoms
- Controller methods > 100 lines
- Multiple API calls within `validate()`
- Complex workflow orchestration in controller
- "God object" pattern

### Why It's Wrong
| Issue | Impact |
|-------|--------|
| Violates Single Responsibility | Controller handles everything |
| Hard to test | Can't unit test individual behaviors |
| Difficult to extend | Tight coupling |
| Duplication | Same logic copied across controllers |
| Upgrade fragility | Core changes break custom logic |

### Detection Script
```python
import inspect
import frappe

def detect_bloated_controllers(threshold_lines=80):
    """Detect controllers with excessive method sizes."""
    results = []
    
    # Get all DocType controllers
    for doctype in frappe.get_all("DocType", filters={"custom": 0}, fields=["name", "module"]):
        try:
            doc_class = frappe.get_doc(doctype.name).__class__
            
            for method_name in ['validate', 'on_submit', 'on_cancel', 'before_save']:
                if hasattr(doc_class, method_name):
                    method = getattr(doc_class, method_name)
                    source = inspect.getsource(method)
                    line_count = len(source.split('\n'))
                    
                    if line_count > threshold_lines:
                        results.append({
                            "doctype": doctype.name,
                            "method": method_name,
                            "lines": line_count,
                            "module": doctype.module,
                            "severity": "CRITICAL" if line_count > 150 else "HIGH"
                        })
        except:
            continue
    
    return sorted(results, key=lambda x: x["lines"], reverse=True)
```

### Correction Strategy: Service Layer Pattern

**WRONG: Bloated controller**
```python
class SalesOrder(Document):
    def validate(self):
        # 200 lines of mixed concerns
        self.validate_customer()
        self.validate_items()
        self.calculate_taxes()
        self.check_credit_limit()
        self.update_inventory_projection()
        self.send_notification()
        self.sync_to_external_system()
        self.validate_against_contract()
        self.apply_promotions()
        self.check_minimum_order()
        self.validate_delivery_date()
        self.calculate_shipping()
        self.update_lead_status()
```

**CORRECT: Service layer extraction**
```python
# sales_order.py - Thin controller
from frappe.model.document import Document
from custom_app.services.sales_order import (
    SalesOrderValidationService,
    SalesOrderSubmissionService,
    SalesOrderNotificationService,
    ExternalSyncService
)

class SalesOrder(Document):
    """Thin controller - delegates to services."""
    
    def validate(self):
        SalesOrderValidationService(self).execute()
    
    def on_submit(self):
        SalesOrderSubmissionService(self).execute()
        SalesOrderNotificationService(self).send_submit_notifications()
        ExternalSyncService(self).sync_to_crm()
    
    def on_cancel(self):
        SalesOrderSubmissionService(self).reverse_inventory_reservation()
        SalesOrderNotificationService(self).send_cancel_notifications()


# services/sales_order/validation.py - 60 lines
class SalesOrderValidationService:
    def __init__(self, doc):
        self.doc = doc
        self.errors = []
    
    def execute(self):
        self.validate_customer()
        self.validate_items()
        self.validate_financials()
        self.validate_logistics()
        
        if self.errors:
            frappe.throw("\n".join(self.errors))
    
    def validate_customer(self):
        if not frappe.db.exists("Customer", self.doc.customer):
            self.errors.append(f"Customer {self.doc.customer} does not exist")
    
    def validate_items(self):
        for item in self.doc.items:
            if not item.qty or item.qty <= 0:
                self.errors.append(f"Item {item.item_code}: Quantity must be > 0")
    
    def validate_financials(self):
        if self.doc.grand_total <= 0:
            self.errors.append("Order total must be greater than zero")
    
    def validate_logistics(self):
        if self.doc.delivery_date and self.doc.delivery_date < today():
            self.errors.append("Delivery date cannot be in the past")


# services/sales_order/submission.py - 80 lines
class SalesOrderSubmissionService:
    def __init__(self, doc):
        self.doc = doc
    
    def execute(self):
        self.reserve_inventory()
        self.update_projections()
        self.create_gl_entries()
    
    def reverse_inventory_reservation(self):
        self.release_inventory()
        self.reverse_gl_entries()
    
    def reserve_inventory(self):
        for item in self.doc.items:
            if item.reserve_stock:
                create_stock_reservation(item)
    
    def release_inventory(self):
        frappe.db.sql("""
            DELETE FROM `tabStock Reservation`
            WHERE sales_order = %s
        """, self.doc.name)


# services/sales_order/notification.py - 40 lines
class SalesOrderNotificationService:
    def __init__(self, doc):
        self.doc = doc
    
    def send_submit_notifications(self):
        if self.doc.grand_total > 100000:
            self.notify_sales_manager()
        
        if self.doc.customer:
            self.notify_customer()
    
    def send_cancel_notifications(self):
        notify_roles = ["Sales Manager", "Accounts Manager"]
        for role in notify_roles:
            self.notify_role(role, f"Order {self.doc.name} cancelled")
```

---

## Anti-Pattern 4: Unindexed Filters

### Symptoms
- List views taking >2 seconds with <10k records
- `EXPLAIN` shows "Using where; Using filesort"
- User complaints about search performance
- Database CPU spikes during filtering

### Why It's Wrong
| Issue | Impact |
|-------|--------|
| Full table scans | O(n) instead of O(log n) lookups |
| Database CPU spikes | Resource exhaustion |
| User experience degradation | Page timeouts |
| Scalability ceiling | Performance collapses at scale |

### Detection Script
```python
import frappe

def analyze_filter_usage(days=30):
    """Analyze which filter fields need indexing."""
    # This requires query log analysis
    # Simplified version checks common filter patterns
    
    high_volume_doctypes = [
        "Sales Invoice", "Purchase Invoice", "Sales Order", "Purchase Order",
        "Delivery Note", "Stock Entry", "Journal Entry", "Payment Entry"
    ]
    
    results = []
    
    for doctype in high_volume_doctypes:
        count = frappe.db.count(doctype)
        if count < 1000:
            continue
        
        meta = frappe.get_meta(doctype)
        
        # Common filter fields that should be indexed
        filter_candidates = [
            "customer", "supplier", "company", "posting_date",
            "status", "item_code", "warehouse", "account"
        ]
        
        for fieldname in filter_candidates:
            field = meta.get_field(fieldname)
            if not field:
                continue
            
            is_indexed = field.search_index or field.index
            
            if not is_indexed and count > 50000:
                results.append({
                    "doctype": doctype,
                    "field": fieldname,
                    "record_count": count,
                    "indexed": False,
                    "severity": "CRITICAL" if count > 200000 else "HIGH"
                })
    
    return results

def generate_index_migration(doctype, fields):
    """Generate SQL for adding missing indexes."""
    table = f"tab{doctype.replace(' ', '')}"
    
    sql = []
    for field in fields:
        index_name = f"{field}_idx"
        sql.append(f"""
            ALTER TABLE `{table}`
            ADD INDEX `{index_name}` (`{field}`);
        """)
    
    return "\n".join(sql)
```

### Correction Strategy

**Add Index to DocType Definition**
```json
{
    "fieldname": "customer",
    "fieldtype": "Link",
    "options": "Customer",
    "search_index": 1,
    "index": 1
}
```

**Migration for Existing Tables**
```python
# patches/add_sales_invoice_indexes.py
import frappe

def execute():
    """Add performance indexes to Sales Invoice."""
    
    indexes_to_add = [
        ("customer", "idx_customer"),
        ("posting_date", "idx_posting_date"),
        ("status", "idx_status"),
        ("company", "idx_company"),
        ("customer", "posting_date", "idx_customer_date")
    ]
    
    for columns, index_name in indexes_to_add:
        try:
            if isinstance(columns, str):
                columns = [columns]
            
            column_str = ", ".join([f"`{c}`" for c in columns])
            frappe.db.sql(f"""
                ALTER TABLE `tabSales Invoice`
                ADD INDEX `{index_name}` ({column_str})
            """)
            
            print(f"✅ Added index {index_name}")
        except Exception as e:
            if "Duplicate key name" in str(e):
                print(f"ℹ️ Index {index_name} already exists")
            else:
                print(f"❌ Failed to add index {index_name}: {e}")
```

---

## Anti-Pattern 5: Excessive Whitelisted Endpoints

### Symptoms
- > 15 `@frappe.whitelist()` methods in single file
- Public APIs exposing internal data structures
- No rate limiting on exposed methods
- API maintenance burden

### Detection Script
```python
import ast
import os

def count_whitelisted_methods(directory):
    """Count whitelisted methods per file."""
    results = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if not file.endswith('.py'):
                continue
            
            filepath = os.path.join(root, file)
            
            try:
                with open(filepath, 'r') as f:
                    tree = ast.parse(f.read())
                
                whitelist_count = 0
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        for decorator in node.decorator_list:
                            if isinstance(decorator, ast.Call):
                                if hasattr(decorator.func, 'attr') and decorator.func.attr == 'whitelist':
                                    whitelist_count += 1
                            elif isinstance(decorator, ast.Attribute):
                                if decorator.attr == 'whitelist':
                                    whitelist_count += 1
                
                if whitelist_count > 10:
                    results.append({
                        "file": filepath,
                        "count": whitelist_count,
                        "severity": "HIGH" if whitelist_count > 20 else "MEDIUM"
                    })
            except:
                continue
    
    return sorted(results, key=lambda x: x["count"], reverse=True)
```

### Correction Strategy: Consolidated API Pattern

**WRONG: Scattered whitelisted methods**
```python
@frappe.whitelist()
def get_customer_data(name): pass

@frappe.whitelist()
def get_customer_orders(name): pass

@frappe.whitelist()
def update_customer(name, data): pass

@frappe.whitelist()
def delete_customer(name): pass

@frappe.whitelist()
def get_customer_invoices(name): pass

@frappe.whitelist()
def get_customer_payments(name): pass
# ... 20 more methods
```

**CORRECT: RESTful API class**
```python
from frappe.model.document import Document

class CustomerAPI(Document):
    """Consolidated Customer API with built-in rate limiting."""
    
    @frappe.whitelist(allow_guest=False, methods=['GET'])
    def get(self, name):
        """Get customer with related data."""
        if not frappe.has_permission("Customer", "read", name):
            frappe.throw("Insufficient permissions")
        
        customer = frappe.get_doc("Customer", name)
        
        return {
            "customer": customer.as_dict(),
            "orders": self._get_recent_orders(name),
            "invoices": self._get_recent_invoices(name),
            "payments": self._get_recent_payments(name),
            "credit_status": self._get_credit_status(name)
        }
    
    @frappe.whitelist(allow_guest=False, methods=['POST'])
    def update(self, name, data):
        """Update customer with validation."""
        if not frappe.has_permission("Customer", "write", name):
            frappe.throw("Insufficient permissions")
        
        doc = frappe.get_doc("Customer", name)
        doc.update(data)
        doc.save()
        
        return {"success": True, "name": doc.name}
    
    @frappe.whitelist(allow_guest=False, methods=['DELETE'])
    def delete(self, name):
        """Delete customer with cascade check."""
        if not frappe.has_permission("Customer", "delete", name):
            frappe.throw("Insufficient permissions")
        
        # Check for open transactions
        open_orders = frappe.db.count("Sales Order", 
            filters={"customer": name, "status": ["!=", "Completed"]})
        
        if open_orders > 0:
            frappe.throw(f"Cannot delete: {open_orders} open orders exist")
        
        frappe.delete_doc("Customer", name)
        return {"success": True}
    
    def _get_recent_orders(self, customer, limit=5):
        return frappe.get_all("Sales Order",
            filters={"customer": customer},
            fields=["name", "status", "grand_total", "transaction_date"],
            order_by="transaction_date desc",
            limit=limit)
    
    def _get_credit_status(self, customer):
        # Implementation
        pass
```

---

## Anti-Pattern 6: Hard-Coded Company Logic

### Symptoms
- String literals like `"My Company LLC"` in code
- `if company == "XYZ Ltd"` conditionals
- Single-company assumptions
- Deployment failures in multi-company setups

### Detection Script
```python
import re
import os

def detect_hardcoded_companies(directory):
    """Detect hard-coded company references."""
    patterns = [
        r'["\'](\w+\s+(?:LLC|Ltd|Inc|Corp|Company|Trading|Group))["\']',
        r'company\s*==?\s*["\'][^"\']+["\']',
        r'company\s*[=!]+\s*["\'][^"\']+["\']',
        r'default_company\s*=\s*["\'][^"\']+["\']',
        r'company_name\s*:\s*["\'][^"\']+["\']',
    ]
    
    results = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if not file.endswith('.py'):
                continue
            
            filepath = os.path.join(root, file)
            
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    for pattern in patterns:
                        match = re.search(pattern, line, re.IGNORECASE)
                        if match and not line.strip().startswith('#'):
                            results.append({
                                "file": filepath,
                                "line": i,
                                "match": match.group(0),
                                "code": line.strip()
                            })
                            break
            except:
                continue
    
    return results
```

### Correction Strategy

**WRONG: Hard-coded company logic**
```python
def get_tax_rate(doc):
    if doc.company == "ABC Trading LLC":
        return 0.05  # 5% VAT
    elif doc.company == "XYZ Manufacturing Ltd":
        return 0.15  # 15% VAT
    else:
        return 0  # No tax

def get_reporting_currency(doc):
    if doc.company == "ABC Trading LLC":
        return "AED"
    elif doc.company == "XYZ Manufacturing Ltd":
        return "USD"
    else:
        return "SAR"
```

**CORRECT: Configuration-driven**
```python
def get_tax_rate(doc):
    """Get tax rate from company configuration."""
    company_settings = frappe.get_cached_doc("Company", doc.company)
    return flt(company_settings.default_tax_rate) / 100

def get_reporting_currency(doc):
    """Get reporting currency from company settings."""
    company = frappe.get_cached_doc("Company", doc.company)
    return company.default_currency or frappe.defaults.get_global_default("currency")

def get_company_setting(doc, setting_name):
    """Generic company-specific setting retrieval."""
    return frappe.db.get_value("Company", doc.company, setting_name)

# Even better: Use Company Settings DocType
class CompanySettings(Document):
    """Extended company configuration."""
    
    def get_special_handling_rules(self):
        return {
            "requires_dual_approval": self.requires_dual_approval,
            "approval_threshold": self.approval_threshold,
            "auto_submit_invoices": self.auto_submit_invoices
        }
```

---

## Anti-Pattern 7: Overusing Custom Fields

### Symptoms
- > 30 custom fields on core DocTypes
- Business logic dependent on custom field presence
- Version upgrade failures
- Performance degradation on core operations

### Detection Script
```python
def audit_custom_fields():
    """Audit custom field usage across core DocTypes."""
    core_doctypes = [
        "Sales Invoice", "Purchase Invoice", "Sales Order", "Purchase Order",
        "Customer", "Supplier", "Item", "Stock Entry", "Journal Entry"
    ]
    
    results = []
    
    for doctype in core_doctypes:
        custom_fields = frappe.get_all("Custom Field",
            filters={"dt": doctype},
            fields=["fieldname", "fieldtype", "modified"])
        
        if len(custom_fields) > 30:
            results.append({
                "doctype": doctype,
                "custom_field_count": len(custom_fields),
                "fields": [f.fieldname for f in custom_fields],
                "severity": "CRITICAL" if len(custom_fields) > 50 else "HIGH"
            })
    
    return results
```

### Correction Strategy: Extension Pattern

**WRONG: Many custom fields on Sales Invoice**
```json
// Custom fields added via UI
{
    "custom_tax_category": "Data",
    "custom_approval_level": "Select",
    "custom_region_code": "Data",
    "custom_customer_segment": "Select",
    "custom_special_handling": "Check",
    // ... 45 more custom fields
}
```

**CORRECT: Extension DocType with 1:1 relationship**
```python
# custom_app/doctype/invoice_extension/invoice_extension.json
{
    "name": "Invoice Extension",
    "fields": [
        {
            "fieldname": "sales_invoice",
            "label": "Sales Invoice",
            "fieldtype": "Link",
            "options": "Sales Invoice",
            "unique": 1,
            "reqd": 1
        },
        {"fieldname": "tax_category", "label": "Tax Category", "fieldtype": "Link", "options": "Tax Category"},
        {"fieldname": "approval_level", "label": "Approval Level", "fieldtype": "Select", "options": "Level 1\nLevel 2\nLevel 3"},
        {"fieldname": "region_code", "label": "Region Code", "fieldtype": "Data"},
        {"fieldname": "customer_segment", "label": "Customer Segment", "fieldtype": "Link", "options": "Customer Segment"},
        {"fieldname": "special_handling", "label": "Special Handling", "fieldtype": "Check"}
    ]
}

# Controller with override
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice

class CustomSalesInvoice(SalesInvoice):
    def validate(self):
        super().validate()
        self.validate_extension()
    
    def validate_extension(self):
        extension = frappe.get_value("Invoice Extension",
            {"sales_invoice": self.name},
            ["approval_level", "special_handling"],
            as_dict=1)
        
        if extension and extension.special_handling:
            if extension.approval_level == "Level 3" and self.grand_total > 50000:
                frappe.throw("Level 3 approval required for orders > 50,000")
```

---

## Anti-Pattern 8: Direct DB Manipulation

### Symptoms
- `frappe.db.sql()` for standard CRUD
- `UPDATE tabDocType` without ORM
- Bypassing document lifecycle
- Permission checks skipped

### Why It's Wrong
| Issue | Impact |
|-------|--------|
| Bypasses validation | Data integrity violations |
| No permission checking | Security vulnerability |
| Corrupts document state | Linked documents out of sync |
| Breaks hooks | Side effects don't trigger |

### Detection Script
```python
import re
import os

def detect_raw_sql(directory):
    """Detect potentially unsafe raw SQL."""
    dangerous_patterns = [
        r'UPDATE\s+`?tab\w+`?\s+SET',
        r'DELETE\s+FROM\s+`?tab\w+`?',
        r'INSERT\s+INTO\s+`?tab\w+`?',
        r'frappe\.db\.sql\s*\([^)]*tab',
        r'ALTER\s+TABLE\s+`?tab\w+`?',
        r'DROP\s+TABLE\s+`?tab\w+`?'
    ]
    
    results = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if not file.endswith('.py'):
                continue
            
            filepath = os.path.join(root, file)
            
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    for pattern in dangerous_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            # Check if justified
                            context = '\n'.join(lines[max(0, i-3):i])
                            if '/* REASON:' not in context and '# REASON:' not in context:
                                results.append({
                                    "file": filepath,
                                    "line": i,
                                    "sql": line.strip(),
                                    "severity": "CRITICAL"
                                })
                            break
            except:
                continue
    
    return results
```

### Correction Strategy

**WRONG: Direct SQL manipulation**
```python
def bulk_update_status(order_names, new_status):
    """DANGEROUS: Bypasses all validation and hooks."""
    
    # Dangerous - no validation!
    frappe.db.sql("""
        UPDATE `tabSales Order`
        SET status = %s
        WHERE name IN %s
    """, (new_status, tuple(order_names)))
    
    frappe.db.commit()
```

**CORRECT: ORM with lifecycle**
```python
def bulk_update_status(order_names, new_status):
    """SAFE: Uses ORM with full validation and hooks."""
    
    results = {"success": [], "failed": []}
    
    frappe.db.savepoint("bulk_update")
    
    try:
        for idx, name in enumerate(order_names):
            try:
                doc = frappe.get_doc("Sales Order", name)
                
                # Permission check
                if not frappe.has_permission("Sales Order", "write", doc):
                    results["failed"].append({
                        "name": name,
                        "reason": "Insufficient permissions"
                    })
                    continue
                
                # Validation
                if doc.status == "Cancelled":
                    results["failed"].append({
                        "name": name,
                        "reason": "Cannot update cancelled order"
                    })
                    continue
                
                # Update with lifecycle
                doc.status = new_status
                doc.save()
                
                results["success"].append(name)
                
                # Periodic commit
                if idx % 50 == 0:
                    frappe.db.commit()
                    frappe.db.savepoint(f"batch_{idx}")
                    
            except Exception as e:
                results["failed"].append({"name": name, "reason": str(e)})
                frappe.db.rollback(save_point=f"batch_{idx // 50 * 50}")
        
        frappe.db.commit()
        
    except Exception as e:
        frappe.db.rollback(save_point="bulk_update")
        frappe.throw(f"Bulk update failed: {str(e)}")
    
    return results
```

---

## Anti-Pattern 9: Blocking Calls in Request Cycle

### Symptoms
- `requests.get()` in form controller
- External API calls in `validate()`
- File processing in request handler
- User-facing timeouts

### Why It's Wrong
| Issue | Impact |
|-------|--------|
| Request timeouts | 504 Gateway Timeout errors |
| Thread exhaustion | Server becomes unresponsive |
| Cascading failures | One slow API affects all users |
| Poor UX | Users wait indefinitely |

### Detection Script
```python
import re

def detect_blocking_calls(code):
    """Detect potentially blocking operations."""
    patterns = [
        r'requests\.(get|post|put|delete|patch)\s*\(',
        r'urllib\.request\.',
        r'http\.client\.',
        r'ftp\.',
        r'subprocess\.(run|call|Popen)',
        r'open\([^)]+["\']r["\'][^)]*\)',
        r'csv\.reader\(|csv\.DictReader',
        r'xlrd\.|openpyxl\.',
        r'pandas\.read_',
        r'smtplib\.|email\.',
    ]
    
    matches = []
    lines = code.split('\n')
    
    for i, line in enumerate(lines, 1):
        for pattern in patterns:
            if re.search(pattern, line):
                # Check if in request context (not background job)
                if 'def validate' in code or 'def before_save' in code:
                    matches.append({"line": i, "code": line.strip()})
                break
    
    return matches
```

### Correction Strategy

**WRONG: External API in request cycle**
```python
class PaymentEntry(Document):
    def validate(self):
        # DANGEROUS: Blocks request for 5-30 seconds!
        if self.payment_gateway:
            response = requests.post(
                "https://payment-gateway.com/api/v2/charge",
                json={
                    "amount": self.amount,
                    "currency": self.currency,
                    "token": self.payment_token
                },
                timeout=30
            )
            
            if response.status_code != 200:
                frappe.throw("Payment failed")
            
            self.transaction_id = response.json()["transaction_id"]
```

**CORRECT: Async background job**
```python
class PaymentEntry(Document):
    def on_submit(self):
        """Queue payment processing for async execution."""
        
        # Mark as pending
        self.db_set("payment_status", "Pending")
        
        # Queue for async processing
        frappe.enqueue(
            "custom_app.payment.process_payment_async",
            payment_entry=self.name,
            queue=" payments",
            timeout=300,
            job_name=f"payment-{self.name}"
        )
        
        frappe.msgprint(_(
            "Payment queued for processing. "
            "You will be notified when complete."
        ))

# Background job implementation
def process_payment_async(payment_entry):
    """Process payment in background - no request blocking."""
    doc = frappe.get_doc("Payment Entry", payment_entry)
    
    try:
        response = requests.post(
            "https://payment-gateway.com/api/v2/charge",
            json={
                "amount": doc.amount,
                "currency": doc.currency,
                "token": doc.payment_token
            },
            timeout=60
        )
        
        if response.status_code == 200:
            doc.db_set("payment_status", "Completed")
            doc.db_set("transaction_id", response.json()["transaction_id"])
            
            # Notify user
            frappe.publish_realtime(
                "payment_completed",
                {"payment_entry": payment_entry, "status": "success"},
                user=doc.owner
            )
        else:
            doc.db_set("payment_status", "Failed")
            doc.add_comment("Comment", text=f"Payment failed: {response.text}")
            
    except Exception as e:
        doc.db_set("payment_status", "Failed")
        doc.add_comment("Comment", text=f"Error: {str(e)}")
        frappe.log_error(f"Payment processing error: {str(e)}", "Payment Entry")
```

---

## Anti-Pattern 10: Missing Error Handling

### Symptoms
- No try-except blocks
- Silent failures with `pass`
- Missing validation before operations
- No transaction rollbacks
- Users see raw tracebacks

### Why It's Wrong
| Issue | Impact |
|-------|--------|
| Data corruption | Partial operations succeed |
| Silent failures | Issues go undetected |
| Debug nightmare | Hard to trace root cause |
| User confusion | Cryptic error messages |

### Detection Script
```python
import ast

def analyze_error_handling(code):
    """Analyze error handling coverage."""
    tree = ast.parse(code)
    
    functions = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_name = node.name
            has_try_except = False
            has_raise = False
            lines = node.end_lineno - node.lineno if node.end_lineno else 0
            
            for child in ast.walk(node):
                if isinstance(child, ast.Try):
                    has_try_except = True
                if isinstance(child, ast.Raise):
                    has_raise = True
            
            # Risk scoring
            risk_score = 0
            if lines > 20 and not has_try_except:
                risk_score += 3
            if not has_raise and lines > 10:
                risk_score += 1
            
            functions.append({
                "name": func_name,
                "lines": lines,
                "has_try_except": has_try_except,
                "has_raise": has_raise,
                "risk_score": risk_score
            })
    
    return [f for f in functions if f["risk_score"] > 2]
```

### Correction Strategy: Comprehensive Error Handling

**WRONG: No error handling**
```python
def process_import(file_path):
    """DANGEROUS: No error handling at all."""
    data = read_csv(file_path)
    
    for row in data:
        doc = frappe.get_doc({"doctype": "Item", **row})
        doc.insert()
    
    frappe.msgprint("Import completed")
```

**CORRECT: Multi-layer error handling**
```python
def process_import(file_path, chunk_size=100):
    """Comprehensive error handling with recovery."""
    
    # Phase 1: Validation
    if not os.path.exists(file_path):
        frappe.throw(f"File not found: {file_path}")
    
    if not file_path.endswith('.csv'):
        frappe.throw("Only CSV files supported")
    
    # Phase 2: Setup
    errors = []
    created = 0
    updated = 0
    batch_start_time = now()
    
    frappe.db.savepoint("import_start")
    
    try:
        # Phase 3: Processing with chunked commits
        data = read_csv(file_path)
        total_rows = len(data)
        
        for idx, row in enumerate(data, 1):
            try:
                # Row-level savepoint
                frappe.db.savepoint(f"row_{idx}")
                
                # Validation
                if not row.get("item_code"):
                    errors.append(f"Row {idx}: Missing item_code")
                    continue
                
                # Check for existing
                existing = frappe.db.exists("Item", row["item_code"])
                
                if existing:
                    # Update existing
                    doc = frappe.get_doc("Item", row["item_code"])
                    doc.update(row)
                    doc.save()
                    updated += 1
                else:
                    # Create new
                    doc = frappe.get_doc({"doctype": "Item", **row})
                    doc.insert()
                    created += 1
                
                # Periodic commit and progress
                if idx % chunk_size == 0:
                    frappe.db.commit()
                    frappe.publish_progress(
                        idx / total_rows * 100,
                        title=f"Processing... ({idx}/{total_rows})"
                    )
                    frappe.db.savepoint(f"batch_{idx}")
                
            except frappe.DuplicateEntryError as e:
                errors.append(f"Row {idx}: Duplicate entry - {str(e)}")
                frappe.db.rollback(save_point=f"row_{idx}")
                
            except frappe.ValidationError as e:
                errors.append(f"Row {idx}: Validation failed - {str(e)}")
                frappe.db.rollback(save_point=f"row_{idx}")
                
            except Exception as e:
                errors.append(f"Row {idx}: Unexpected error - {str(e)}")
                frappe.db.rollback(save_point=f"row_{idx}")
                frappe.log_error(f"Import error at row {idx}: {str(e)}", "Item Import")
        
        # Final commit
        frappe.db.commit()
        
        # Phase 4: Reporting
        duration = time_diff_in_seconds(now(), batch_start_time)
        
        result = {
            "success": True,
            "total": total_rows,
            "created": created,
            "updated": updated,
            "errors": len(errors),
            "duration_seconds": duration,
            "error_log": errors[:20]  # First 20 errors
        }
        
        # Log full error report
        if errors:
            frappe.log_error(
                f"Import completed with {len(errors)} errors:\n" + "\n".join(errors[:100]),
                "Item Import Report"
            )
        
        return result
        
    except Exception as e:
        # Global rollback on catastrophic failure
        frappe.db.rollback(save_point="import_start")
        frappe.throw(f"Import failed catastrophically: {str(e)}")
```

---

## Summary: Anti-Pattern Detection Pipeline

```python
# Complete anti-pattern audit

def run_full_audit(app_path):
    """Run complete anti-pattern detection."""
    
    audit_results = {
        "fat_doctypes": detect_fat_doctypes(80),
        "client_logic": detect_client_logic_bloat(app_path),
        "bloated_controllers": detect_bloated_controllers(80),
        "unindexed_filters": analyze_filter_usage(),
        "excessive_whitelist": count_whitelisted_methods(app_path),
        "hardcoded_companies": detect_hardcoded_companies(app_path),
        "custom_fields": audit_custom_fields(),
        "raw_sql": detect_raw_sql(app_path),
        "missing_error_handling": []  # Per-file analysis needed
    }
    
    # Calculate overall health score
    total_issues = sum(len(v) for v in audit_results.values() if isinstance(v, list))
    
    health_score = max(0, 100 - (total_issues * 2))
    
    return {
        "health_score": health_score,
        "total_issues": total_issues,
        "breakdown": audit_results
    }
```

---

**See also:**
- `33_PERFORMANCE/` — Performance optimization guide
- `34_SECURITY/` — Security validation
- `38_UPGRADE/` — Safe migration patterns
