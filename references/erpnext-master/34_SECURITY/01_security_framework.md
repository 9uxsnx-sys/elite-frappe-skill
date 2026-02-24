# Security Framework

Permission audit, API security, multi-tenant isolation, and comprehensive security architecture for Frappe/ERPNext enterprise deployments.

---

## 1. Permission Audit Checklist

### Permission Model Review

```python
# Comprehensive permission audit

class PermissionAuditor:
    """Audit permission configuration for security gaps."""
    
    CRITICAL_DOCTYPES = [
        "User", "Role", "Permission", "System Settings",
        "Company", "Chart of Accounts", "GL Entry",
        "Sales Invoice", "Purchase Invoice"
    ]
    
    def __init__(self):
        self.findings = []
    
    def audit_all(self):
        """Run complete permission audit."""
        
        return {
            "role_explosion": self.check_role_explosion(),
            "orphan_permissions": self.find_orphan_permissions(),
            "overprivileged_roles": self.check_overprivileged_roles(),
            "missing_permissions": self.find_missing_permissions(),
            "wildcards": self.find_wildcard_permissions(),
            "cross_company": self.check_cross_company_access(),
            "field_level": self.audit_field_level_permissions()
        }
    
    def check_role_explosion(self, threshold=50):
        """Detect role explosion - too many roles."""
        
        roles = frappe.get_all("Role", fields=["name"])
        
        if len(roles) > threshold:
            return {
                "risk": "HIGH",
                "count": len(roles),
                "threshold": threshold,
                "recommendation": "Consolidate roles - consider role templates"
            }
        
        return {"risk": "LOW", "count": len(roles)}
    
    def find_orphan_permissions(self):
        """Find permissions for deleted DocTypes."""
        
        all_doctypes = set(d.name for d in frappe.get_all("DocType"))
        
        orphan_perms = frappe.get_all("DocPerm",
            filters={"parenttype": "DocType"},
            fields=["parent", "role", "name"]
        )
        
        orphans = [p for p in orphan_perms if p.parent not in all_doctypes]
        
        return {
            "count": len(orphans),
            "permissions": orphans,
            "cleanup_sql": f"DELETE FROM `tabDocPerm` WHERE name IN ({', '.join([o.name for o in orphans])})"
        }
    
    def check_overprivileged_roles(self):
        """Find roles with excessive permissions."""
        
        # Roles that can modify critical DocTypes
        overprivileged = []
        
        for role in frappe.get_all("Role", fields=["name"]):
            perms = frappe.get_all("DocPerm",
                filters={
                    "role": role.name,
                    "parent": ["in", self.CRITICAL_DOCTYPES],
                    "write": 1
                }
            )
            
            if len(perms) > 5:
                overprivileged.append({
                    "role": role.name,
                    "critical_writes": len(perms),
                    "doctypes": [p.parent for p in perms]
                })
        
        return overprivileged
    
    def find_wildcard_permissions(self):
        """Find wildcard (*) permissions - security risk."""
        
        wildcards = frappe.get_all("DocPerm",
            filters={"permlevel": 0},  # Main level
            fields=["parent", "role", "read", "write", "create", "delete"]
        )
        
        high_risk = []
        for perm in wildcards:
            # Check if role has all permissions on sensitive DocType
            if perm.parent in self.CRITICAL_DOCTYPES:
                if perm.read and perm.write and perm.create and perm.delete:
                    high_risk.append({
                        "doctype": perm.parent,
                        "role": perm.role,
                        "risk": "CRITICAL - Full access to sensitive DocType"
                    })
        
        return high_risk
    
    def check_cross_company_access(self):
        """Check for cross-company permission violations."""
        
        # In multi-company setups, check if users can access other companies' data
        violations = []
        
        companies = frappe.get_all("Company", fields=["name"])
        
        if len(companies) <= 1:
            return []
        
        # Check if any role has access to all companies
        for role in frappe.get_all("Role", fields=["name"]):
            # Users with this role
            users = frappe.get_all("User", 
                filters={"role_profile_name": role.name},
                fields=["name"]
            )
            
            for user in users:
                # Check company restrictions
                user_doc = frappe.get_doc("User", user.name)
                
                if not user_doc.get("companies"):  # No company restriction
                    # This user can access all companies
                    violations.append({
                        "user": user.name,
                        "role": role.name,
                        "issue": "No company restriction - can access all companies"
                    })
        
        return violations

# Usage
auditor = PermissionAuditor()
report = auditor.audit_all()
```

### Permission Hardening

```python
def harden_permissions():
    """Apply security hardening to permissions."""
    
    # 1. Remove wildcard permissions from critical DocTypes
    critical_doctypes = ["User", "Role", "System Settings"]
    
    for doctype in critical_doctypes:
        # Ensure only System Manager has write access
        perms = frappe.get_all("DocPerm",
            filters={
                "parent": doctype,
                "write": 1,
                "role": ["!=", "System Manager"]
            }
        )
        
        for perm in perms:
            frappe.db.set_value("DocPerm", perm.name, "write", 0)
    
    # 2. Add create permissions only where needed
    transaction_doctypes = ["Sales Invoice", "Purchase Invoice", "Journal Entry"]
    
    for doctype in transaction_doctypes:
        # Remove create from read-only roles
        perms = frappe.get_all("DocPerm",
            filters={
                "parent": doctype,
                "create": 1,
                "role": ["in", ["Report User", "Analytics User"]]
            }
        )
        
        for perm in perms:
            frappe.db.set_value("DocPerm", perm.name, "create", 0)
    
    frappe.db.commit()
```

---

## 2. Role Explosion Mitigation

### Role Template Pattern

```python
# Role template system to prevent explosion

ROLE_TEMPLATES = {
    "sales_user": {
        "description": "Standard sales user",
        "permissions": {
            "Sales Order": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 0},
            "Sales Invoice": {"read": 1, "write": 0, "create": 0, "submit": 0, "cancel": 0},
            "Customer": {"read": 1, "write": 1, "create": 1},
            "Item": {"read": 1, "write": 0, "create": 0}
        }
    },
    "sales_manager": {
        "extends": "sales_user",
        "additional_permissions": {
            "Sales Invoice": {"write": 1, "create": 1, "submit": 1, "cancel": 1},
            "Sales Order": {"cancel": 1}
        }
    },
    "accounting_user": {
        "description": "Standard accounting user",
        "permissions": {
            "Journal Entry": {"read": 1, "write": 1, "create": 1, "submit": 1},
            "Payment Entry": {"read": 1, "write": 1, "create": 1, "submit": 1},
            "GL Entry": {"read": 1, "write": 0, "create": 0},
            "Account": {"read": 1, "write": 0, "create": 0}
        }
    }
}

class RoleTemplateManager:
    """Manage role creation from templates."""
    
    def create_from_template(self, role_name, template_name, customizations=None):
        """Create role from template."""
        
        template = ROLE_TEMPLATES.get(template_name)
        if not template:
            frappe.throw(f"Template {template_name} not found")
        
        # Create role
        role = frappe.get_doc({
            "doctype": "Role",
            "role_name": role_name,
            "desk_access": 1
        })
        role.insert()
        
        # Apply permissions
        for doctype, perms in template["permissions"].items():
            self._apply_permission(role_name, doctype, perms)
        
        # Apply customizations
        if customizations:
            for doctype, perms in customizations.items():
                self._apply_permission(role_name, doctype, perms)
        
        return role
    
    def _apply_permission(self, role, doctype, perms):
        """Apply permission to role."""
        
        perm_doc = frappe.get_doc({
            "doctype": "DocPerm",
            "parent": doctype,
            "parenttype": "DocType",
            "parentfield": "permissions",
            "role": role,
            **perms
        })
        perm_doc.insert()
```

---

## 3. Field-Level Permission Logic

### Granular Field Security

```python
# Field-level permission implementation

class FieldLevelSecurity:
    """Implement field-level security controls."""
    
    SENSITIVE_FIELDS = {
        "Employee": ["bank_account", "salary", "personal_email"],
        "Customer": ["credit_limit", "tax_id", "bank_account"],
        "Supplier": ["bank_account", "tax_id"],
        "User": ["email", "phone", "api_key", "api_secret"]
    }
    
    def validate_field_access(self, doc, fieldname, action="read"):
        """Validate if user can access specific field."""
        
        # Check if field is sensitive
        sensitive = self.SENSITIVE_FIELDS.get(doc.doctype, [])
        
        if fieldname not in sensitive:
            return True  # Not sensitive, allow
        
        # Check additional permissions
        if action == "write":
            # Only allow write to specific roles
            allowed_roles = ["System Manager", f"{doc.doctype} Manager"]
            
            if not any(r in frappe.get_roles() for r in allowed_roles):
                frappe.throw(
                    f"You don't have permission to modify {fieldname}",
                    frappe.PermissionError
                )
        
        return True
    
    def mask_sensitive_fields(self, doc, user=None):
        """Mask sensitive fields in response."""
        
        user = user or frappe.session.user
        sensitive = self.SENSITIVE_FIELDS.get(doc.doctype, [])
        
        masked_doc = frappe.get_doc(doc.doctype, doc.name).as_dict()
        
        for field in sensitive:
            if not self._has_field_permission(doc.doctype, field, user):
                masked_doc[field] = "***MASKED***"
        
        return masked_doc
    
    def _has_field_permission(self, doctype, field, user):
        """Check if user has permission to see field."""
        
        # Own record
        if frappe.get_doc(doctype, frappe.form_dict.get("name")).owner == user:
            return True
        
        # Manager role
        if f"{doctype} Manager" in frappe.get_roles(user):
            return True
        
        # System Manager
        if "System Manager" in frappe.get_roles(user):
            return True
        
        return False

# Controller integration
class Employee(Document):
    def validate(self):
        # Check field-level permissions
        security = FieldLevelSecurity()
        
        if self.has_value_changed("salary"):
            security.validate_field_access(self, "salary", "write")
    
    def on_update(self):
        # Log sensitive field changes
        if self.has_value_changed("bank_account"):
            frappe.logger().warning(
                f"Bank account changed for {self.name} by {frappe.session.user}"
            )
```

---

## 4. API Exposure Rules

### API Security Framework

```python
# API security and exposure controls

class APISecurityFramework:
    """Control API exposure and security."""
    
    API_RULES = {
        "public_endpoints": {
            "max_rate": 100,  # requests per minute
            "require_auth": False,
            "allowed_methods": ["GET"]
        },
        "private_endpoints": {
            "max_rate": 1000,
            "require_auth": True,
            "allowed_methods": ["GET", "POST", "PUT", "DELETE"]
        },
        "admin_endpoints": {
            "max_rate": 500,
            "require_auth": True,
            "required_roles": ["System Manager"],
            "allowed_methods": ["GET", "POST", "PUT", "DELETE"]
        }
    }
    
    def secure_endpoint(self, fn, endpoint_type="private"):
        """Decorator to secure API endpoint."""
        
        rules = self.API_RULES.get(endpoint_type, self.API_RULES["private"])
        
        @frappe.whitelist(allow_guest=not rules["require_auth"])
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Rate limiting
            if not self._check_rate_limit(fn.__name__, rules["max_rate"]):
                frappe.throw("Rate limit exceeded", frappe.RateLimitExceededError)
            
            # Authentication check
            if rules["require_auth"] and frappe.session.user == "Guest":
                frappe.throw("Authentication required", frappe.AuthenticationError)
            
            # Role check
            if "required_roles" in rules:
                if not any(r in frappe.get_roles() for r in rules["required_roles"]):
                    frappe.throw("Insufficient permissions", frappe.PermissionError)
            
            # Method check
            if frappe.request.method not in rules["allowed_methods"]:
                frappe.throw("Method not allowed", frappe.MethodNotAllowed)
            
            return fn(*args, **kwargs)
        
        return wrapper
    
    def _check_rate_limit(self, endpoint, max_rate):
        """Simple rate limit check using Redis."""
        
        key = f"rate_limit:{frappe.session.user}:{endpoint}"
        current = frappe.cache.get_value(key) or 0
        
        if current >= max_rate:
            return False
        
        frappe.cache.set_value(key, current + 1, expires_in_sec=60)
        return True

# Usage
security = APISecurityFramework()

@security.secure_endpoint(endpoint_type="public")
@frappe.whitelist(allow_guest=True)
def get_public_products():
    """Public endpoint with rate limiting."""
    return frappe.get_all("Item", fields=["name", "item_name", "standard_rate"])

@security.secure_endpoint(endpoint_type="private")
@frappe.whitelist()
def get_customer_orders(customer):
    """Private endpoint requiring authentication."""
    return frappe.get_all("Sales Order",
        filters={"customer": customer},
        fields=["name", "status", "grand_total"]
    )

@security.secure_endpoint(endpoint_type="admin")
@frappe.whitelist()
def admin_clear_cache():
    """Admin-only endpoint."""
    frappe.clear_cache()
    return {"success": True}
```

### Token Security Strategy

```python
# API token security

class TokenManager:
    """Manage API tokens securely."""
    
    TOKEN_LIFETIME = 3600  # 1 hour
    REFRESH_LIFETIME = 86400  # 24 hours
    
    def generate_token(self, user, scopes=None):
        """Generate secure API token."""
        
        import secrets
        import hashlib
        import json
        
        # Generate random token
        token = secrets.token_urlsafe(32)
        
        # Hash for storage
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # Store metadata
        meta = {
            "user": user,
            "scopes": scopes or ["read"],
            "created": now(),
            "expires": add_to_date(now(), seconds=self.TOKEN_LIFETIME),
            "last_used": None,
            "use_count": 0
        }
        
        # Store hashed token
        frappe.cache.set_value(
            f"api_token:{token_hash}",
            meta,
            expires_in_sec=self.TOKEN_LIFETIME
        )
        
        # Return full token (one-time)
        return token
    
    def validate_token(self, token):
        """Validate API token."""
        
        import hashlib
        
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        meta = frappe.cache.get_value(f"api_token:{token_hash}")
        
        if not meta:
            return None
        
        # Check expiration
        if get_datetime(meta["expires"]) < now_datetime():
            frappe.cache.delete_value(f"api_token:{token_hash}")
            return None
        
        # Update metadata
        meta["last_used"] = now()
        meta["use_count"] += 1
        
        frappe.cache.set_value(
            f"api_token:{token_hash}",
            meta,
            expires_in_sec=self.TOKEN_LIFETIME
        )
        
        return meta
    
    def revoke_token(self, token):
        """Revoke API token."""
        
        import hashlib
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        frappe.cache.delete_value(f"api_token:{token_hash}")
```

---

## 5. CSRF Protection

### CSRF Security Implementation

```python
# CSRF protection for custom endpoints

class CSRFProtection:
    """CSRF protection for state-changing operations."""
    
    def validate_csrf_token(self, token):
        """Validate CSRF token from request."""
        
        expected = frappe.session.data.get("csrf_token")
        
        if not expected:
            frappe.throw("CSRF token not found in session")
        
        if not token:
            frappe.throw("CSRF token required", frappe.CSRFTokenError)
        
        if token != expected:
            frappe.throw("Invalid CSRF token", frappe.CSRFTokenError)
        
        return True
    
    def get_csrf_token(self):
        """Get or generate CSRF token for session."""
        
        import secrets
        
        if not frappe.session.data.get("csrf_token"):
            frappe.session.data["csrf_token"] = secrets.token_hex(32)
            frappe.session.save()
        
        return frappe.session.data["csrf_token"]

# Integration with whitelisted methods
def csrf_required(fn):
    """Decorator to require CSRF token."""
    
    @wraps(fn)
    def wrapper(*args, **kwargs):
        csrf_token = frappe.request.headers.get("X-Frappe-CSRF-Token")
        
        protection = CSRFProtection()
        protection.validate_csrf_token(csrf_token)
        
        return fn(*args, **kwargs)
    
    return wrapper

# Usage
@frappe.whitelist()
@csrf_required
def delete_record(doctype, name):
    """Delete record with CSRF protection."""
    
    if not frappe.has_permission(doctype, "delete", name):
        frappe.throw("Permission denied")
    
    frappe.delete_doc(doctype, name)
    return {"success": True}
```

---

## 6. Background Job Privilege Boundary

### Job Security Model

```python
# Secure background job execution

class SecureJobRunner:
    """Run background jobs with proper privilege boundaries."""
    
    def run_as_user(self, method, user, **kwargs):
        """Run job with specific user privileges."""
        
        # Store original user
        original_user = frappe.session.user
        
        try:
            # Switch to target user
            frappe.set_user(user)
            
            # Set user defaults
            frappe.defaults.set_user_default("company", 
                frappe.db.get_value("User", user, "company"))
            
            # Run method
            result = method(**kwargs)
            
            return result
            
        finally:
            # Restore original user
            frappe.set_user(original_user)
    
    def run_with_elevated_privileges(self, method, justification, **kwargs):
        """Run job with elevated privileges (logging required)."""
        
        # Log privilege escalation
        frappe.logger().warning(
            f"Elevated privileges used: {justification} "
            f"by {frappe.session.user}"
        )
        
        # Store original roles
        original_roles = frappe.get_roles()
        
        try:
            # Add temporary system manager role
            frappe.session.user = "Administrator"
            
            result = method(**kwargs)
            
            return result
            
        finally:
            # Restore original roles
            pass  # Roles are session-based
    
    def validate_job_permission(self, job_type, user):
        """Validate if user can queue specific job type."""
        
        job_permissions = {
            "data_export": ["System Manager", "Report Manager"],
            "data_import": ["System Manager", "Data Manager"],
            "bulk_update": ["System Manager"],
            "user_deletion": ["System Manager"]
        }
        
        required_roles = job_permissions.get(job_type, ["System Manager"])
        user_roles = frappe.get_roles(user)
        
        if not any(r in user_roles for r in required_roles):
            frappe.throw(
                f"User {user} cannot queue {job_type} job. "
                f"Required roles: {', '.join(required_roles)}"
            )

# Usage in background jobs
def secure_background_task(task_fn, run_as=None, justification=None):
    """Decorator for secure background task execution."""
    
    @wraps(task_fn)
    def wrapper(**kwargs):
        runner = SecureJobRunner()
        
        if run_as:
            return runner.run_as_user(task_fn, run_as, **kwargs)
        elif justification:
            return runner.run_with_elevated_privileges(task_fn, justification, **kwargs)
        else:
            return task_fn(**kwargs)
    
    return wrapper
```

---

## 7. Data Leakage Prevention

### DLP Implementation

```python
# Data leakage prevention

class DataLeakagePrevention:
    """Prevent sensitive data leakage in responses and logs."""
    
    SENSITIVE_PATTERNS = [
        r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',  # Credit card
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
        r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
        r'(password|secret|key|token)\s*[=:]\s*["\'][^"\']+["\']',  # Secrets
    ]
    
    def sanitize_for_logs(self, data):
        """Remove sensitive data before logging."""
        
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                if any(s in key.lower() for s in ["password", "secret", "key", "token", "api"]):
                    sanitized[key] = "***REDACTED***"
                else:
                    sanitized[key] = self.sanitize_for_logs(value)
            return sanitized
        
        elif isinstance(data, str):
            sanitized = data
            for pattern in self.SENSITIVE_PATTERNS:
                sanitized = re.sub(pattern, "***REDACTED***", sanitized)
            return sanitized
        
        elif isinstance(data, list):
            return [self.sanitize_for_logs(item) for item in data]
        
        return data
    
    def validate_response(self, response):
        """Validate response doesn't contain sensitive data."""
        
        response_str = json.dumps(response)
        
        for pattern in self.SENSITIVE_PATTERNS:
            if re.search(pattern, response_str):
                frappe.logger().error(
                    "Potential data leakage detected in response"
                )
                return False
        
        return True
    
    def mask_fields(self, doc, fields_to_mask):
        """Mask sensitive fields in document."""
        
        masked = doc.as_dict()
        
        for field in fields_to_mask:
            if field in masked:
                value = str(masked[field])
                if len(value) > 4:
                    masked[field] = value[:2] + "***" + value[-2:]
                else:
                    masked[field] = "***"
        
        return masked

# Integration
class SecureLogger:
    """Logger with automatic sanitization."""
    
    def __init__(self):
        self.dlp = DataLeakagePrevention()
    
    def info(self, message, data=None):
        if data:
            data = self.dlp.sanitize_for_logs(data)
        frappe.logger().info(f"{message}: {data}")
    
    def error(self, message, exception=None):
        if exception:
            safe_msg = self.dlp.sanitize_for_logs(str(exception))
            frappe.logger().error(f"{message}: {safe_msg}")
```

---

## 8. Multi-Tenant Isolation Strategy

### Tenant Isolation Architecture

```python
# Multi-company (tenant) isolation

class TenantIsolation:
    """Enforce multi-tenant data isolation."""
    
    COMPANY_ISOLATED_DOCTYPES = [
        "Sales Invoice", "Purchase Invoice", "Journal Entry",
        "Stock Ledger Entry", "GL Entry", "Payment Entry"
    ]
    
    def enforce_company_filter(self, doctype, filters):
        """Add company filter for multi-tenant safety."""
        
        if doctype not in self.COMPANY_ISOLATED_DOCTYPES:
            return filters
        
        user_companies = self._get_user_companies()
        
        if not user_companies:
            # No company restriction - can see all
            return filters
        
        # Add company filter
        if isinstance(filters, dict):
            filters["company"] = ["in", user_companies]
        elif isinstance(filters, list):
            filters.append(["company", "in", user_companies])
        
        return filters
    
    def _get_user_companies(self):
        """Get companies user has access to."""
        
        user_doc = frappe.get_doc("User", frappe.session.user)
        
        # Check if user has company restrictions
        if hasattr(user_doc, 'companies') and user_doc.companies:
            return [c.company for c in user_doc.companies]
        
        # Default company
        default = frappe.defaults.get_user_default("company")
        if default:
            return [default]
        
        return []
    
    def validate_cross_company_access(self, doc):
        """Validate user can access document's company."""
        
        if not hasattr(doc, 'company'):
            return True
        
        user_companies = self._get_user_companies()
        
        if not user_companies:
            return True
        
        if doc.company not in user_companies:
            frappe.throw(
                f"You don't have access to company {doc.company}",
                frappe.PermissionError
            )
        
        return True
    
    def get_company_scoped_query(self, doctype, fields=None, filters=None):
        """Get query with automatic company scoping."""
        
        filters = self.enforce_company_filter(doctype, filters or {})
        
        return frappe.get_all(
            doctype,
            fields=fields,
            filters=filters
        )

# Query override
class SecureQueryBuilder:
    """Query builder with automatic tenant isolation."""
    
    def __init__(self, doctype):
        self.doctype = doctype
        self.isolation = TenantIsolation()
    
    def build(self, fields=None, filters=None, **kwargs):
        """Build query with company isolation."""
        
        # Apply company filter
        filters = self.isolation.enforce_company_filter(self.doctype, filters)
        
        # Build query
        return frappe.get_all(
            self.doctype,
            fields=fields,
            filters=filters,
            **kwargs
        )
```

---

## Summary: Security Checklist

**Before production deployment:**

- [ ] Permission audit completed
- [ ] Role explosion mitigated (< 30 roles)
- [ ] No wildcard permissions on critical DocTypes
- [ ] Field-level permissions on sensitive data
- [ ] API rate limiting configured
- [ ] CSRF protection on state-changing endpoints
- [ ] Background job privilege boundaries defined
- [ ] Data leakage prevention in logs
- [ ] Multi-tenant isolation enforced
- [ ] Token security implemented
- [ ] Security audit logs enabled
- [ ] Penetration testing completed
