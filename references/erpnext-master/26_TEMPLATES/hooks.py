# ERPNext Custom App Hooks Template
# Place this file in: custom_app/hooks.py

app_name = "custom_app"
app_title = "Custom App"
app_publisher = "Your Company"
app_description = "Custom ERPNext App"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "support@yourcompany.com"

# ============================================
# INCLUDE JS/CSS
# ============================================

# Include JS in desk
app_include_js = "/assets/custom_app/js/custom.js"

# Include CSS in desk
app_include_css = "/assets/custom_app/css/custom.css"

# Include JS/CSS for specific DocType
doctype_js = {
    "Sales Invoice": "public/js/sales_invoice.js",
    "Purchase Order": "public/js/purchase_order.js",
}

doctype_css = {
    "Sales Invoice": "public/css/sales_invoice.css",
}

# ============================================
# DOC EVENTS
# ============================================

doc_events = {
    # All DocTypes
    "*": {
        "validate": "custom_app.handlers.validate_all",
    },
    
    # Sales Invoice Events
    "Sales Invoice": {
        "validate": "custom_app.handlers.sales_invoice.validate",
        "before_submit": "custom_app.handlers.sales_invoice.before_submit",
        "on_submit": "custom_app.handlers.sales_invoice.on_submit",
        "on_cancel": "custom_app.handlers.sales_invoice.on_cancel",
        "on_update_after_submit": "custom_app.handlers.sales_invoice.on_update_after_submit",
    },
    
    # Sales Order Events
    "Sales Order": {
        "validate": "custom_app.handlers.sales_order.validate",
        "on_submit": "custom_app.handlers.sales_order.on_submit",
        "on_cancel": "custom_app.handlers.sales_order.on_cancel",
    },
    
    # Purchase Order Events
    "Purchase Order": {
        "validate": "custom_app.handlers.purchase_order.validate",
        "on_submit": "custom_app.handlers.purchase_order.on_submit",
    },
    
    # Stock Entry Events
    "Stock Entry": {
        "validate": "custom_app.handlers.stock_entry.validate",
        "on_submit": "custom_app.handlers.stock_entry.on_submit",
    },
    
    # Payment Entry Events
    "Payment Entry": {
        "validate": "custom_app.handlers.payment_entry.validate",
        "on_submit": "custom_app.handlers.payment_entry.on_submit",
    },
    
    # Item Events
    "Item": {
        "validate": "custom_app.handlers.item.validate",
        "after_insert": "custom_app.handlers.item.after_insert",
    },
    
    # Customer Events
    "Customer": {
        "validate": "custom_app.handlers.customer.validate",
        "after_insert": "custom_app.handlers.customer.after_insert",
        "on_trash": "custom_app.handlers.customer.on_trash",
    },
}

# ============================================
# OVERRIDE DOCTYPE CLASS
# ============================================

override_doctype_class = {
    "Sales Invoice": "custom_app.overrides.sales_invoice.CustomSalesInvoice",
    "Purchase Order": "custom_app.overrides.purchase_order.CustomPurchaseOrder",
}

# ============================================
# EXTEND DOCTYPE CLASS
# ============================================

extend_doctype_class = {
    "Sales Invoice": "custom_app.extensions.sales_invoice.ExtendSalesInvoice",
}

# ============================================
# PERMISSION HOOKS
# ============================================

# Custom permission query
permission_query_conditions = {
    "Sales Invoice": "custom_app.permissions.sales_invoice_query",
    "Item": "custom_app.permissions.item_query",
}

# Custom has_permission
has_permission = {
    "Sales Invoice": "custom_app.permissions.has_sales_invoice_permission",
}

# ============================================
# SCHEDULED TASKS
# ============================================

scheduler_events = {
    # Run every hour
    "hourly": [
        "custom_app.tasks.hourly.sync_external_data",
    ],
    
    # Run daily at midnight
    "daily": [
        "custom_app.tasks.daily.cleanup_logs",
        "custom_app.tasks.daily.send_daily_report",
    ],
    
    # Run weekly (Sunday)
    "weekly": [
        "custom_app.tasks.weekly.generate_weekly_report",
    ],
    
    # Run monthly (1st of month)
    "monthly": [
        "custom_app.tasks.monthly.generate_monthly_report",
    ],
    
    # Custom cron expressions
    "cron": {
        "0 9 * * *": [
            "custom_app.tasks.cron.morning_report",
        ],
        "0 17 * * 1-5": [
            "custom_app.tasks.cron.end_of_day_report",
        ],
    },
    
    # Run on all workers
    "all": [
        "custom_app.tasks.all.process_queue",
    ],
}

# ============================================
# INSTALL HOOKS
# ============================================

before_install = "custom_app.install.before_install"
after_install = "custom_app.install.after_install"
after_sync = "custom_app.install.after_sync"

# ============================================
# MIGRATION HOOKS
# ============================================

before_migrate = "custom_app.migrate.before_migrate"
after_migrate = "custom_app.migrate.after_migrate"

# ============================================
# TEST HOOKS
# ============================================

before_tests = "custom_app.tests.before_tests"
after_tests = "custom_app.tests.after_tests"

# ============================================
# WEBSITE HOOKS
# ============================================

# Website route rules
website_route_rules = [
    {"from_route": "/custom-page/<name>", "to_route": "custom_page"},
]

# Website redirects
website_redirects = [
    {"source": "/old-page", "target": "/new-page"},
]

# Website context
website_context = {
    "custom_key": "custom_value"
}

# Update website context (function)
update_website_context = "custom_app.website.update_context"

# ============================================
# FIXED ASSETS
# ============================================

fixtures = [
    # Export Custom Fields
    {
        "doctype": "Custom Field",
        "filters": [
            ["dt", "in", ["Sales Invoice", "Sales Order", "Customer"]]
        ]
    },
    
    # Export Property Setters
    {
        "doctype": "Property Setter",
        "filters": [
            ["doc_type", "in", ["Sales Invoice", "Item"]]
        ]
    },
]

# ============================================
# WEBSOCKET/REALTIME
# ============================================

# Custom realtime events
realtime_on = {
    "custom_event": "custom_app.realtime.handle_custom_event",
}

# ============================================
# API WHITELIST
# ============================================

# Additional whitelisted methods (beyond @frappe.whitelist())
# whitelisted_methods = [
#     "custom_app.api.get_custom_data",
# ]
