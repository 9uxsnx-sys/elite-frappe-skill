# Automated Code Pattern Library

Production-grade templates with context: why, when, limitations.

---

## 1. Clean DocType Skeleton

### Pattern: Service-Based DocType

```python
# doctype_controller.py

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate

class SalesOrder(Document):
    """
    Clean DocType controller following service pattern.
    
    WHY: Separates core lifecycle from business logic for testability.
    WHEN: Any DocType with complex business rules (>50 lines validation).
    LIMITATIONS: Adds indirection; overkill for simple master data.
    """
    
    def validate(self):
        """Thin validation - delegates to service."""
        from custom_app.services.sales_order_service import SalesOrderValidationService
        SalesOrderValidationService(self).validate()
    
    def on_submit(self):
        """Thin submit handler."""
        from custom_app.services.sales_order_service import SalesOrderSubmissionService
        SalesOrderSubmissionService(self).execute()
    
    def on_cancel(self):
        """Thin cancel handler."""
        from custom_app.services.sales_order_service import SalesOrderCancellationService
        SalesOrderCancellationService(self).execute()

# Service implementation
class SalesOrderValidationService:
    """
    Handles all validation logic for Sales Order.
    
    WHY: Centralized validation enables testing without database.
    WHEN: Complex validation rules spanning multiple fields.
    """
    
    def __init__(self, doc):
        self.doc = doc
        self.errors = []
    
    def validate(self):
        """Execute all validations."""
        self.validate_customer()
        self.validate_items()
        self.validate_dates()
        self.validate_financials()
        
        if self.errors:
            frappe.throw("<br>".join(self.errors))
    
    def validate_customer(self):
        if not frappe.db.exists("Customer", self.doc.customer):
            self.errors.append(f"Customer {self.doc.customer} does not exist")
    
    def validate_items(self):
        for item in self.doc.items:
            if not item.qty or item.qty <= 0:
                self.errors.append(f"Row {item.idx}: Quantity must be > 0")
    
    def validate_dates(self):
        if self.doc.delivery_date and self.doc.delivery_date < nowdate():
            self.errors.append("Delivery date cannot be in the past")
    
    def validate_financials(self):
        if self.doc.grand_total <= 0:
            self.errors.append("Order total must be greater than zero")
```

---

## 2. Hook Override Skeleton

### Pattern: Override with Super Call

```python
# overrides/custom_sales_invoice.py

from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice
import frappe

class CustomSalesInvoice(SalesInvoice):
    """
    Override core Sales Invoice behavior.
    
    WHY: Extends core without modifying source.
    WHEN: Need custom validation/submission logic.
    LIMITATIONS: Vulnerable to core changes; requires version pinning.
    """
    
    def validate(self):
        """Extend validation - call super first."""
        super().validate()
        self.validate_custom_rules()
    
    def validate_custom_rules(self):
        """Custom validation logic."""
        # Custom business rules here
        pass
    
    def on_submit(self):
        """Extend submission."""
        super().on_submit()
        self.trigger_custom_workflow()
    
    def trigger_custom_workflow(self):
        """Custom post-submit actions."""
        if self.grand_total > 100000:
            frappe.enqueue(
                "custom_app.workflows.high_value_order_review",
                sales_invoice=self.name
            )
    
    def on_cancel(self):
        """Extend cancellation."""
        # Pre-cancel checks
        self.validate_cancel_eligibility()
        
        super().on_cancel()
        
        # Post-cancel cleanup
        self.cleanup_custom_data()
    
    def validate_cancel_eligibility(self):
        """Check if cancellation allowed."""
        if self.status == "Paid":
            frappe.throw("Cannot cancel paid invoice. Process refund first.")
    
    def cleanup_custom_data(self):
        """Clean up related custom records."""
        frappe.db.sql("""
            DELETE FROM `tabCustom Invoice Extension`
            WHERE sales_invoice = %s
        """, self.name)

# hooks.py registration
override_doctype_class = {
    "Sales Invoice": "custom_app.overrides.custom_sales_invoice.CustomSalesInvoice"
}
```

---

## 3. Background Job Worker

### Pattern: Stateful Job with Progress

```python
# jobs/bulk_processor.py

import frappe
from frappe.utils.background_jobs import enqueue

class BulkProcessor:
    """
    Stateful background job with progress tracking.
    
    WHY: Handles long operations without blocking requests.
    WHEN: >1000 records or >30 second processing time.
    LIMITATIONS: No real-time result; requires polling.
    """
    
    def __init__(self, job_name=None):
        self.job_name = job_name or f"bulk_process_{frappe.utils.random_string(8)}"
        self.total_records = 0
        self.processed = 0
        self.errors = []
    
    def process(self, doctype, filters=None, processor_fn=None):
        """Process records in background."""
        
        enqueue(
            method=self._process_batch,
            doctype=doctype,
            filters=filters,
            processor_fn=processor_fn,
            job_name=self.job_name,
            queue="long",
            timeout=3600
        )
        
        return {"job_name": self.job_name, "status": "queued"}
    
    def _process_batch(self, doctype, filters, processor_fn):
        """Internal processing method."""
        
        # Get all records
        records = frappe.get_all(doctype, filters=filters, fields=["name"])
        self.total_records = len(records)
        
        # Process in chunks
        chunk_size = 100
        
        for i in range(0, len(records), chunk_size):
            chunk = records[i:i + chunk_size]
            
            try:
                for record in chunk:
                    self._process_single(record, processor_fn)
                    self.processed += 1
                
                # Update progress
                self._update_progress()
                
                # Commit batch
                frappe.db.commit()
                
            except Exception as e:
                self.errors.append({
                    "record": record.name,
                    "error": str(e)
                })
                frappe.db.rollback()
        
        # Final status
        self._update_status("completed" if not self.errors else "completed_with_errors")
    
    def _process_single(self, record, processor_fn):
        """Process single record."""
        doc = frappe.get_doc(record.doctype, record.name)
        processor_fn(doc)
        doc.save()
    
    def _update_progress(self):
        """Publish progress update."""
        progress = (self.processed / self.total_records) * 100
        
        frappe.publish_realtime(
            f"job_progress:{self.job_name}",
            {
                "progress": progress,
                "processed": self.processed,
                "total": self.total_records
            }
        )
    
    def get_status(self):
        """Get current job status."""
        # Implementation to retrieve from cache/database
        pass

# Usage
processor = BulkProcessor()
processor.process(
    doctype="Sales Order",
    filters={"status": "Draft"},
    processor_fn=lambda doc: doc.submit()
)
```

---

## 4. Scheduled Job

### Pattern: Idempotent Scheduled Task

```python
# jobs/scheduled_tasks.py

import frappe
from frappe.utils import now, add_days

class ScheduledTaskRunner:
    """
    Idempotent scheduled task implementation.
    
    WHY: Ensures task can run multiple times without side effects.
    WHEN: Daily/weekly maintenance tasks.
    LIMITATIONS: Slightly slower due to idempotency checks.
    """
    
    def daily_cleanup(self):
        """Daily cleanup task - safe to re-run."""
        
        # Check if already run today
        last_run = frappe.cache.get_value("daily_cleanup_last_run")
        
        if last_run and last_run[:10] == now()[:10]:
            frappe.logger().info("Daily cleanup already ran today")
            return
        
        # Execute cleanup
        self._cleanup_old_logs()
        self._archive_completed_jobs()
        self._clear_temp_files()
        
        # Mark as run
        frappe.cache.set_value("daily_cleanup_last_run", now())
        
        frappe.logger().info("Daily cleanup completed")
    
    def _cleanup_old_logs(self, days=30):
        """Clean up logs older than N days."""
        
        cutoff = add_days(now(), -days)
        
        # Check what would be deleted first
        count = frappe.db.count("Error Log", {"creation": ["<", cutoff]})
        
        if count > 0:
            frappe.db.sql("""
                DELETE FROM `tabError Log`
                WHERE creation < %s
                LIMIT 10000
            """, cutoff)
            
            frappe.db.commit()
            frappe.logger().info(f"Cleaned up {count} old error logs")
    
    def _archive_completed_jobs(self):
        """Archive completed background jobs."""
        
        # Move to archive table
        frappe.db.sql("""
            INSERT INTO `tabRQ Job Archive`
            SELECT * FROM `tabRQ Job`
            WHERE status IN ('finished', 'failed')
            AND modified < DATE_SUB(NOW(), INTERVAL 7 DAY)
        """)
        
        # Delete originals
        frappe.db.sql("""
            DELETE FROM `tabRQ Job`
            WHERE status IN ('finished', 'failed')
            AND modified < DATE_SUB(NOW(), INTERVAL 7 DAY)
        """)
        
        frappe.db.commit()

# hooks.py registration
scheduler_events = {
    "daily": [
        "custom_app.jobs.scheduled_tasks.daily_cleanup"
    ],
    "weekly": [
        "custom_app.jobs.scheduled_tasks.weekly_report"
    ],
    "monthly": [
        "custom_app.jobs.scheduled_tasks.monthly_reconciliation"
    ]
}
```

---

## 5. Permission Rule Template

### Pattern: Dynamic Permission Handler

```python
# permissions/dynamic_permissions.py

import frappe
from frappe.permissions import add_user_permission

class DynamicPermissionManager:
    """
    Dynamic permission assignment based on business rules.
    
    WHY: Automates permission grants based on data changes.
    WHEN: Territories, regions, or project-based access control.
    LIMITATIONS: Async nature - slight delay in permission application.
    """
    
    def assign_territory_permissions(self, user, territory):
        """Assign user permissions for territory and children."""
        
        # Get territory hierarchy
        territories = self._get_territory_hierarchy(territory)
        
        for t in territories:
            # Create user permission
            if not frappe.db.exists("User Permission", {
                "user": user,
                "allow": "Territory",
                "for_value": t
            }):
                add_user_permission("Territory", t, user)
        
        # Apply to Customer DocType
        frappe.db.sql("""
            INSERT INTO `tabUser Permission` (name, user, allow, for_value)
            SELECT 
                CONCAT(%s, '-', c.name),
                %s,
                'Customer',
                c.name
            FROM `tabCustomer` c
            WHERE c.territory IN %s
            ON DUPLICATE KEY UPDATE modified = NOW()
        """, (user, user, tuple(territories)))
    
    def revoke_territory_permissions(self, user, territory):
        """Revoke permissions when territory changes."""
        
        frappe.db.sql("""
            DELETE FROM `tabUser Permission`
            WHERE user = %s
            AND allow = 'Territory'
            AND for_value = %s
        """, (user, territory))
        
        frappe.db.commit()
    
    def _get_territory_hierarchy(self, territory):
        """Get territory and all children."""
        
        territories = [territory]
        
        children = frappe.get_all("Territory",
            filters={"parent_territory": territory},
            fields=["name"]
        )
        
        for child in children:
            territories.extend(self._get_territory_hierarchy(child.name))
        
        return territories

# Hook integration
def on_customer_update(doc, method):
    """Update permissions when customer territory changes."""
    
    if doc.has_value_changed("territory"):
        manager = DynamicPermissionManager()
        
        # Get sales reps for this territory
        sales_reps = frappe.get_all("Sales Person",
            filters={"territory": doc.territory},
            fields=["user"]
        )
        
        for rep in sales_reps:
            if rep.user:
                manager.assign_territory_permissions(rep.user, doc.territory)
```

---

## 6. Complex Report Builder

### Pattern: Cached Report with Parameters

```python
# reports/custom_report.py

import frappe
from frappe.utils import cint, flt

class CustomReportBuilder:
    """
    Complex report with caching and parameter handling.
    
    WHY: Handles expensive queries with intelligent caching.
    WHEN: Reports taking >5 seconds or run frequently.
    LIMITATIONS: Stale data risk - implement cache invalidation.
    """
    
    CACHE_TTL = 3600  # 1 hour
    
    def __init__(self, filters=None):
        self.filters = filters or {}
        self.cache_key = self._generate_cache_key()
    
    def execute(self):
        """Execute report with caching."""
        
        # Check cache
        cached = frappe.cache.get_value(self.cache_key)
        if cached:
            return cached
        
        # Build and execute query
        columns = self._get_columns()
        data = self._get_data()
        
        result = {
            "columns": columns,
            "data": data,
            "chart": self._get_chart(data),
            "summary": self._get_summary(data)
        }
        
        # Cache result
        frappe.cache.set_value(self.cache_key, result, expires_in_sec=self.CACHE_TTL)
        
        return result
    
    def _get_columns(self):
        """Define report columns."""
        return [
            {"fieldname": "customer", "label": "Customer", "fieldtype": "Link", "options": "Customer", "width": 200},
            {"fieldname": "total_sales", "label": "Total Sales", "fieldtype": "Currency", "width": 150},
            {"fieldname": "total_qty", "label": "Quantity", "fieldtype": "Float", "width": 100},
            {"fieldname": "last_order", "label": "Last Order", "fieldtype": "Date", "width": 120}
        ]
    
    def _get_data(self):
        """Fetch and process report data."""
        
        from frappe.query_builder import DocType
        
        SO = DocType("Sales Order")
        
        query = frappe.qb.from_(SO).select(
            SO.customer,
            frappe.qb.functions.Sum(SO.grand_total).as_("total_sales"),
            frappe.qb.functions.Sum(SO.total_qty).as_("total_qty"),
            frappe.qb.functions.Max(SO.transaction_date).as_("last_order")
        ).where(
            SO.docstatus == 1
        )
        
        # Apply filters
        if self.filters.get("from_date"):
            query = query.where(SO.transaction_date >= self.filters["from_date"])
        
        if self.filters.get("to_date"):
            query = query.where(SO.transaction_date <= self.filters["to_date"])
        
        if self.filters.get("customer"):
            query = query.where(SO.customer == self.filters["customer"])
        
        query = query.groupby(SO.customer)
        
        return query.run(as_dict=True)
    
    def _get_chart(self, data):
        """Generate chart from data."""
        return {
            "data": {
                "labels": [d.customer for d in data[:10]],
                "datasets": [{"values": [flt(d.total_sales) for d in data[:10]]}]
            },
            "type": "bar"
        }
    
    def _get_summary(self, data):
        """Generate summary statistics."""
        
        total_sales = sum(flt(d.total_sales) for d in data)
        
        return [
            {"value": total_sales, "indicator": "Green", "label": "Total Sales", "datatype": "Currency"},
            {"value": len(data), "indicator": "Blue", "label": "Customer Count", "datatype": "Int"}
        ]
    
    def _generate_cache_key(self):
        """Generate unique cache key based on filters."""
        import hashlib
        import json
        
        filter_str = json.dumps(self.filters, sort_keys=True)
        hash_val = hashlib.md5(filter_str.encode()).hexdigest()
        
        return f"report:custom_customer_sales:{hash_val}"
    
    @staticmethod
    def invalidate_cache(customer=None):
        """Invalidate report cache."""
        
        if customer:
            # Invalidate specific customer
            pattern = f"report:custom_customer_sales:*{customer}*"
        else:
            # Invalidate all
            pattern = "report:custom_customer_sales:*"
        
        frappe.cache.delete_keys(pattern)

# Report registration
# In report JSON file
{
    "report_name": "Custom Customer Sales",
    "report_type": "Script Report",
    "is_standard": "No",
    "module": "Custom App"
}

# Report execution entry point
def execute(filters=None):
    return CustomReportBuilder(filters).execute()
```

---

## 7. API Wrapper

### Pattern: RESTful API Resource

```python
# api/resources.py

import frappe
from frappe.model.document import Document

class APIResource:
    """
    RESTful API resource base class.
    
    WHY: Consistent API patterns with built-in validation.
    WHEN: Exposing DocTypes or custom resources via API.
    LIMITATIONS: Adds overhead for simple one-off endpoints.
    """
    
    doctype = None
    allowed_methods = ["GET", "POST", "PUT", "DELETE"]
    required_fields = []
    read_only_fields = []
    
    @frappe.whitelist(allow_guest=False)
    def get(self, name):
        """Get single resource."""
        
        self._check_permission("read", name)
        
        doc = frappe.get_doc(self.doctype, name)
        
        return self._serialize(doc)
    
    @frappe.whitelist(allow_guest=False)
    def list(self, filters=None, fields=None, limit=20, offset=0):
        """List resources with filtering."""
        
        self._check_permission("read")
        
        filters = frappe.parse_json(filters) if filters else {}
        fields = frappe.parse_json(fields) if fields else ["name"]
        
        # Apply permission filters
        filters = self._apply_permission_filters(filters)
        
        results = frappe.get_list(
            self.doctype,
            filters=filters,
            fields=fields,
            limit_page_length=limit,
            limit_start=offset
        )
        
        return {
            "data": results,
            "total": frappe.db.count(self.doctype, filters=filters),
            "limit": limit,
            "offset": offset
        }
    
    @frappe.whitelist(allow_guest=False)
    def create(self, data):
        """Create new resource."""
        
        self._check_permission("create")
        self._validate_required_fields(data)
        
        doc = frappe.get_doc({"doctype": self.doctype, **data})
        doc.insert()
        
        return self._serialize(doc)
    
    @frappe.whitelist(allow_guest=False)
    def update(self, name, data):
        """Update existing resource."""
        
        self._check_permission("write", name)
        self._validate_readonly_fields(data)
        
        doc = frappe.get_doc(self.doctype, name)
        doc.update(data)
        doc.save()
        
        return self._serialize(doc)
    
    @frappe.whitelist(allow_guest=False)
    def delete(self, name):
        """Delete resource."""
        
        self._check_permission("delete", name)
        
        frappe.delete_doc(self.doctype, name)
        
        return {"success": True}
    
    def _check_permission(self, permtype, name=None):
        """Check user permission."""
        
        if not frappe.has_permission(self.doctype, permtype, name):
            frappe.throw("Insufficient permissions", frappe.PermissionError)
    
    def _apply_permission_filters(self, filters):
        """Apply additional permission-based filters."""
        
        # Override in subclass for custom filtering
        return filters
    
    def _validate_required_fields(self, data):
        """Validate required fields present."""
        
        missing = [f for f in self.required_fields if f not in data]
        
        if missing:
            frappe.throw(f"Missing required fields: {', '.join(missing)}")
    
    def _validate_readonly_fields(self, data):
        """Prevent modification of read-only fields."""
        
        readonly_in_data = [f for f in self.read_only_fields if f in data]
        
        if readonly_in_data:
            frappe.throw(f"Cannot modify read-only fields: {', '.join(readonly_in_data)}")
    
    def _serialize(self, doc):
        """Serialize document for API response."""
        
        return doc.as_dict()

# Concrete implementation
class CustomerAPI(APIResource):
    """Customer API resource."""
    
    doctype = "Customer"
    required_fields = ["customer_name"]
    read_only_fields = ["creation", "modified", "modified_by"]
    
    def _apply_permission_filters(self, filters):
        """Apply territory-based filtering."""
        
        user_territories = get_user_territories(frappe.session.user)
        
        if user_territories:
            filters["territory"] = ["in", user_territories]
        
        return filters

# Usage
@frappe.whitelist(allow_guest=False)
def customer_api(method, **kwargs):
    """Customer API entry point."""
    
    api = CustomerAPI()
    
    methods = {
        "GET": lambda: api.get(kwargs.get("name")),
        "LIST": lambda: api.list(
            kwargs.get("filters"),
            kwargs.get("fields"),
            cint(kwargs.get("limit", 20)),
            cint(kwargs.get("offset", 0))
        ),
        "POST": lambda: api.create(kwargs.get("data")),
        "PUT": lambda: api.update(kwargs.get("name"), kwargs.get("data")),
        "DELETE": lambda: api.delete(kwargs.get("name"))
    }
    
    handler = methods.get(method.upper())
    
    if not handler:
        frappe.throw("Invalid method")
    
    return handler()
```

---

## 8. External Integration Template

### Pattern: Resilient External API Client

```python
# integrations/external_client.py

import requests
import frappe
from frappe.utils import now, add_to_date
from tenacity import retry, stop_after_attempt, wait_exponential

class ResilientAPIClient:
    """
    Resilient external API client with retries and circuit breaker.
    
    WHY: Handles network failures gracefully.
    WHEN: Integrating with third-party APIs.
    LIMITATIONS: Adds latency due to retry logic.
    """
    
    def __init__(self, base_url, api_key=None, timeout=30):
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self.circuit_state = "closed"  # closed, open, half-open
        self.failure_count = 0
        self.failure_threshold = 5
        self.recovery_timeout = 300  # 5 minutes
        self.last_failure_time = None
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def get(self, endpoint, params=None):
        """GET request with retries."""
        
        self._check_circuit_breaker()
        
        try:
            response = requests.get(
                f"{self.base_url}{endpoint}",
                params=params,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            response.raise_for_status()
            self._record_success()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self._record_failure()
            raise
    
    def post(self, endpoint, data):
        """POST request with idempotency."""
        
        # Add idempotency key for safety
        headers = self._get_headers()
        headers["Idempotency-Key"] = frappe.generate_hash()
        
        response = requests.post(
            f"{self.base_url}{endpoint}",
            json=data,
            headers=headers,
            timeout=self.timeout
        )
        
        response.raise_for_status()
        return response.json()
    
    def _get_headers(self):
        """Build request headers."""
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        return headers
    
    def _check_circuit_breaker(self):
        """Check if circuit is open."""
        
        if self.circuit_state == "open":
            # Check if recovery time passed
            if self.last_failure_time:
                recovery_time = add_to_date(self.last_failure_time, seconds=self.recovery_timeout)
                
                if now() > recovery_time:
                    self.circuit_state = "half-open"
                else:
                    raise Exception("Circuit breaker is open - service unavailable")
    
    def _record_success(self):
        """Record successful request."""
        
        if self.circuit_state == "half-open":
            self.circuit_state = "closed"
        
        self.failure_count = 0
    
    def _record_failure(self):
        """Record failed request."""
        
        self.failure_count += 1
        self.last_failure_time = now()
        
        if self.failure_count >= self.failure_threshold:
            self.circuit_state = "open"
            frappe.logger().error(f"Circuit breaker opened for {self.base_url}")

# Webhook handler
class WebhookHandler:
    """Handle incoming webhooks securely."""
    
    def __init__(self, secret):
        self.secret = secret
    
    def verify_signature(self, payload, signature):
        """Verify webhook signature."""
        
        import hmac
        import hashlib
        
        expected = hmac.new(
            self.secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected, signature)
    
    def process(self, event_type, payload):
        """Process webhook event."""
        
        handlers = {
            "payment.completed": self._handle_payment_completed,
            "order.shipped": self._handle_order_shipped,
            "customer.updated": self._handle_customer_updated
        }
        
        handler = handlers.get(event_type)
        
        if handler:
            return handler(payload)
        else:
            frappe.logger().warning(f"Unhandled webhook event: {event_type}")
            return {"status": "ignored"}
    
    def _handle_payment_completed(self, payload):
        """Handle payment completion webhook."""
        
        payment_id = payload.get("payment_id")
        order_id = payload.get("order_id")
        
        # Update payment entry
        payment_entry = frappe.get_doc("Payment Entry", {"reference_no": payment_id})
        payment_entry.db_set("status", "Completed")
        
        # Update linked order
        if order_id:
            sales_order = frappe.get_doc("Sales Order", order_id)
            sales_order.db_set("payment_status", "Paid")
        
        return {"status": "processed"}
```

---

## 9. Bulk Import Processor

### Pattern: Streaming Import with Validation

```python
# import/bulk_importer.py

import frappe
import csv
import json
from io import StringIO

class BulkImporter:
    """
    Streaming bulk import with validation and error handling.
    
    WHY: Handles large imports without memory exhaustion.
    WHEN: Importing >1000 records.
    LIMITATIONS: Async processing - not immediate.
    """
    
    def __init__(self, doctype, file_path=None, file_content=None):
        self.doctype = doctype
        self.file_path = file_path
        self.file_content = file_content
        self.errors = []
        self.imported = 0
        self.updated = 0
    
    def preview(self):
        """Preview import without making changes."""
        
        records = self._read_file()
        
        preview_data = []
        
        for i, record in enumerate(records[:10]):
            validation = self._validate_record(record)
            
            preview_data.append({
                "row": i + 1,
                "valid": validation["valid"],
                "errors": validation.get("errors", []),
                "action": self._determine_action(record)
            })
        
        return {
            "total_rows": len(records),
            "preview": preview_data,
            "sample_data": records[:3]
        }
    
    def import_data(self, batch_size=100):
        """Execute import in batches."""
        
        records = self._read_file()
        
        frappe.db.savepoint("bulk_import")
        
        try:
            for i, record in enumerate(records):
                try:
                    self._import_single(record)
                    
                    if (i + 1) % batch_size == 0:
                        frappe.db.commit()
                        frappe.db.savepoint(f"batch_{i}")
                        self._update_progress(i + 1, len(records))
                
                except Exception as e:
                    self.errors.append({
                        "row": i + 1,
                        "data": record,
                        "error": str(e)
                    })
                    frappe.db.rollback(save_point=f"batch_{(i // batch_size) * batch_size}")
            
            frappe.db.commit()
            
            return {
                "success": len(self.errors) == 0,
                "imported": self.imported,
                "updated": self.updated,
                "errors": self.errors
            }
            
        except Exception as e:
            frappe.db.rollback(save_point="bulk_import")
            raise
    
    def _read_file(self):
        """Read and parse import file."""
        
        if self.file_path:
            with open(self.file_path, 'r') as f:
                content = f.read()
        else:
            content = self.file_content
        
        # Detect format
        if content.strip().startswith('['):
            return json.loads(content)
        else:
            # CSV
            reader = csv.DictReader(StringIO(content))
            return list(reader)
    
    def _validate_record(self, record):
        """Validate single record."""
        
        errors = []
        
        # Check required fields
        meta = frappe.get_meta(self.doctype)
        
        for field in meta.get("fields", []):
            if field.reqd and not record.get(field.fieldname):
                errors.append(f"Missing required field: {field.label}")
        
        # Check Link fields exist
        for field in meta.get_link_fields():
            if record.get(field.fieldname):
                if not frappe.db.exists(field.options, record[field.fieldname]):
                    errors.append(f"{field.options} {record[field.fieldname]} does not exist")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _determine_action(self, record):
        """Determine if insert or update."""
        
        if record.get("name") and frappe.db.exists(self.doctype, record["name"]):
            return "update"
        
        return "insert"
    
    def _import_single(self, record):
        """Import single record."""
        
        action = self._determine_action(record)
        
        if action == "update":
            doc = frappe.get_doc(self.doctype, record["name"])
            doc.update(record)
            doc.save()
            self.updated += 1
        else:
            doc = frappe.get_doc({"doctype": self.doctype, **record})
            doc.insert()
            self.imported += 1
    
    def _update_progress(self, current, total):
        """Update progress indicator."""
        
        frappe.publish_realtime(
            "import_progress",
            {
                "current": current,
                "total": total,
                "percentage": (current / total) * 100
            }
        )
```

---

## 10. Event-Driven Pattern

### Pattern: Domain Event System

```python
# events/domain_events.py

import frappe
from datetime import datetime
from typing import List, Callable

class DomainEvent:
    """Base class for domain events."""
    
    def __init__(self, event_type, aggregate_id, payload):
        self.event_type = event_type
        self.aggregate_id = aggregate_id
        self.payload = payload
        self.timestamp = datetime.now()
        self.event_id = frappe.generate_hash()
    
    def to_dict(self):
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat()
        }

class EventBus:
    """
    Simple event bus for decoupled communication.
    
    WHY: Decouples components for better maintainability.
    WHEN: Multiple handlers need to react to same event.
    LIMITATIONS: Eventual consistency - handlers run async.
    """
    
    _handlers = {}
    
    @classmethod
    def subscribe(cls, event_type: str, handler: Callable):
        """Subscribe handler to event type."""
        
        if event_type not in cls._handlers:
            cls._handlers[event_type] = []
        
        cls._handlers[event_type].append(handler)
    
    @classmethod
    def publish(cls, event: DomainEvent):
        """Publish event to all subscribers."""
        
        # Persist event
        cls._persist_event(event)
        
        # Queue handlers
        handlers = cls._handlers.get(event.event_type, [])
        
        for handler in handlers:
            frappe.enqueue(
                method=cls._execute_handler,
                handler=handler,
                event=event.to_dict(),
                queue="default",
                timeout=300
            )
    
    @classmethod
    def _execute_handler(cls, handler, event):
        """Execute handler with error handling."""
        
        try:
            handler(event)
        except Exception as e:
            frappe.log_error(f"Event handler failed: {str(e)}")
            # Retry or dead letter queue logic here
    
    @classmethod
    def _persist_event(cls, event):
        """Persist event for replay capability."""
        
        frappe.get_doc({
            "doctype": "Event Log",
            "event_id": event.event_id,
            "event_type": event.event_type,
            "aggregate_id": event.aggregate_id,
            "payload": frappe.as_json(event.payload),
            "status": "pending"
        }).insert(ignore_permissions=True)

# Event definitions
class SalesOrderSubmitted(DomainEvent):
    def __init__(self, sales_order):
        super().__init__(
            event_type="sales_order.submitted",
            aggregate_id=sales_order.name,
            payload={
                "customer": sales_order.customer,
                "grand_total": sales_order.grand_total,
                "items": [item.as_dict() for item in sales_order.items]
            }
        )

# Handlers
def notify_sales_team(event):
    """Handler: Notify sales team of new order."""
    
    payload = event["payload"]
    
    # Send notification
    frappe.sendmail(
        recipients=get_sales_team_emails(),
        subject=f"New Sales Order: {event['aggregate_id']}",
        message=f"Customer: {payload['customer']}, Amount: {payload['grand_total']}"
    )

def update_customer_analytics(event):
    """Handler: Update customer analytics."""
    
    customer = event["payload"]["customer"]
    
    # Update customer stats
    frappe.db.sql("""
        UPDATE `tabCustomer`
        SET total_sales = total_sales + %s,
            order_count = order_count + 1,
            last_order_date = %s
        WHERE name = %s
    """, (event["payload"]["grand_total"], event["timestamp"], customer))

# Subscribe handlers
EventBus.subscribe("sales_order.submitted", notify_sales_team)
EventBus.subscribe("sales_order.submitted", update_customer_analytics)

# Usage in controller
class SalesOrder(Document):
    def on_submit(self):
        # ... existing logic ...
        
        # Publish event
        event = SalesOrderSubmitted(self)
        EventBus.publish(event)
```

---

## Summary: Pattern Selection Guide

| Pattern | Use Case | Complexity | When to Use |
|---------|----------|------------|-------------|
| Service-Based DocType | Complex validation | Medium | >50 lines validation logic |
| Override Class | Core extension | Medium | Modify core behavior |
| Background Job | Long processing | Low | >30 second operations |
| Scheduled Task | Recurring jobs | Low | Daily/weekly maintenance |
| Dynamic Permissions | Territory-based access | High | Complex access rules |
| Cached Report | Slow reports | Medium | >5 second reports |
| API Resource | REST API | Medium | External integrations |
| Resilient Client | Third-party APIs | Medium | External API calls |
| Bulk Import | Data migration | High | >1000 records |
| Event-Driven | Decoupled systems | High | Multiple async handlers |
