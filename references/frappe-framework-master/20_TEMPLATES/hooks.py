# Frappe Framework Hooks Template
# Place this file in: custom_app/hooks.py

app_name = "custom_app"
app_title = "Custom App"
app_publisher = "Your Company"
app_description = "Custom Frappe Application"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "support@yourcompany.com"

# ============================================
# INCLUDE JS/CSS
# ============================================

app_include_js = "/assets/custom_app/js/custom.js"
app_include_css = "/assets/custom_app/css/custom.css"

doctype_js = {
    "Task": "public/js/task.js",
    "Project": "public/js/project.js",
}

# ============================================
# DOC EVENTS
# ============================================

doc_events = {
    "*": {
        "on_update": "custom_app.handlers.on_any_update"
    },
    "Task": {
        "validate": "custom_app.handlers.task.validate",
        "before_submit": "custom_app.handlers.task.before_submit",
        "on_submit": "custom_app.handlers.task.on_submit",
        "on_cancel": "custom_app.handlers.task.on_cancel"
    },
    "Project": {
        "validate": "custom_app.handlers.project.validate",
        "on_submit": "custom_app.handlers.project.on_submit"
    }
}

# ============================================
# OVERRIDE/EXTEND CONTROLLERS
# ============================================

override_doctype_class = {
    "Task": "custom_app.overrides.task.CustomTask"
}

extend_doctype_class = {
    "Project": "custom_app.extensions.project.ExtendedProject"
}

# ============================================
# PERMISSIONS
# ============================================

permission_query_conditions = {
    "Task": "custom_app.permissions.task_query"
}

has_permission = {
    "Task": "custom_app.permissions.has_task_permission"
}

# ============================================
# SCHEDULER EVENTS
# ============================================

scheduler_events = {
    "hourly": [
        "custom_app.tasks.hourly.cleanup"
    ],
    "daily": [
        "custom_app.tasks.daily.report"
    ],
    "weekly": [
        "custom_app.tasks.weekly.summary"
    ],
    "monthly": [
        "custom_app.tasks.monthly.billing"
    ],
    "cron": {
        "0 9 * * *": ["custom_app.tasks.cron.morning"]
    }
}

# ============================================
# WEBSITE
# ============================================

website_route_rules = [
    {"from_route": "/custom/<name>", "to_route": "custom_page"}
]

website_redirects = [
    {"source": "/old-page", "target": "/new-page"}
]

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
# FIXTURES
# ============================================

fixtures = [
    {"doctype": "Custom Field", "filters": [["dt", "in", ["Task"]]]},
    {"doctype": "Property Setter", "filters": [["doc_type", "in", ["Task"]]]}
]
