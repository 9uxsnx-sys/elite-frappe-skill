# Directory Structure

## Quick Reference
Bench directory contains apps/, sites/, env/, config/. Each app has doctype/, api/, hooks.py. Each site has site_config.json and private files.

## AI Prompt
```
When navigating Frappe structure:
1. apps/ contains installed applications
2. sites/ contains site instances and data
3. env/ is Python virtual environment
4. Each DocType is a folder with .py, .json, .js
5. hooks.py is the extension point
```

---

## Bench Directory

```
frappe-bench/
├── apps/                           # Applications
│   ├── frappe/                    # Framework core
│   ├── erpnext/                   # ERPNext (if installed)
│   └── custom_app/                # Your app
│
├── sites/                          # Site instances
│   ├── site1.localhost/
│   │   ├── site_config.json       # Site config
│   │   ├── private/               # Private files
│   │   │   ├── backups/           # Database backups
│   │   │   └── files/             # Uploaded files
│   │   ├── public/                # Public files
│   │   └── logs/                  # Site logs
│   ├── common_site_config.json    # Global config
│   └── apps.txt                   # Installed apps list
│
├── env/                            # Python venv
│   ├── bin/
│   └── lib/
│
├── config/                         # Service configs
│   ├── redis_cache.conf
│   ├── redis_queue.conf
│   └── supervisor.conf
│
├── logs/                           # Bench logs
│   ├── bench-start.log
│   ├── web.error.log
│   └── worker.log
│
├── Procfile                        # Process definitions
└── patches.txt                     # Patch history
```

---

## App Directory Structure

```
custom_app/
├── custom_app/                     # Main module
│   ├── __init__.py
│   ├── hooks.py                    # Extension hooks
│   ├── modules.txt                 # Module list
│   ├── patches.txt                 # Database patches
│   │
│   ├── custom_module/              # A module
│   │   ├── __init__.py
│   │   └── doctype/               # DocTypes
│   │       ├── custom_doctype/
│   │       │   ├── __init__.py
│   │       │   ├── custom_doctype.py      # Controller
│   │       │   ├── custom_doctype.json    # Schema
│   │       │   ├─
