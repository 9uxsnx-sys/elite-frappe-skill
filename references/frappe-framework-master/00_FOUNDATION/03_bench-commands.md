# Bench Commands Cheat Sheet

## Quick Reference
Comprehensive list of essential bench commands for Frappe/ERPNext development and administration.

## AI Prompt
```
When working with Frappe:
1. Use bench commands for all site operations
2. Always backup before major operations
3. Use --site flag for single-site operations
4. Check logs after errors
```

---

## Site Management

### Creating & Managing Sites
```bash
# Create new site
bench new-site site1.local

# Create site with MariaDB root password
bench new-site site1.local --mariadb-root-password 123456

# Create site with PostgreSQL
bench new-site site1.local --db-type postgres

# Drop site (removes database and files)
bench drop-site site1.local

# Backup site
bench --site site1.local backup

# Restore site
bench --site site1.local restore-path /path/to/database.sql

# Migrate site (after pulling updates)
bench --site site1.local migrate

# Migrate to specific version
bench --site site1.local migrate --to version-15
```

---

## App Management

### Installing & Managing Apps
```bash
# Install an app
bench get-app erpnext

# Install app from GitHub
bench get-app https://github.com/frappe/erpnext

# Install specific branch
bench get-app erpnext --branch version-15

# Remove app
bench remove-app erpnext

# Update app
bench update --pull

# Update specific app
bench update --app erpnext

# Build apps (compile assets)
bench build

# Build specific app
bench build --app erpnext

# Rebuild search index
bench rebuild-search
```

---

## Development

### Running Development Server
```bash
# Start development server
bench start

# Start with multiple workers
bench start --with-coverage

# Disable file watcher
bench start --no-watch
```

### Generator Commands
```bash
# Generate new app
bench new-app my_app

# Generate new module in existing app
bench new-module module_name --app my_app

# Generate new DocType
bench new-doctype doctype_name --app my_app

# Generate new Page
bench new-page page_name --app my_app

# Generate new Web Template
bench new-web-template template_name
```

---

## Configuration

### Environment Variables
```bash
# Set environment variables
bench set-config FRAPPE_SITE site1.local

# Set global config
bench set-config -g max_workers 4

# Get config
bench get-config FRAPPE_SITE

# Remove config
bench set-config --unset FRAPPE_SITE
```

### Setup Commands
```bash
# Add site to bench
bench add-site site1.local

# Use existing MariaDB
bench config set-db root_password 123456

# Setup production
bench setup production frappe

# Setup nginx
bench setup nginx

# Setup supervisor
bench setup supervisor
```

---

## Users & Permissions

```bash
# Create new user
bench create-user admin@site1.local --first-name Admin --last-name User

# List all users
bench --site site1.local list-users

# Set user as administrator
bench --site site1.local add-system-manager administrator@site1.local

# Create role
bench create-role "Custom Role"

# Assign role to user
bench --site site1.local assign-role administrator@site1.local "Custom Role"
```

---

## Database Operations

```bash
# Open MariaDB console
bench --site site1.local mysql

# Run custom SQL
bench --site site1.local execute "frappe.db.sql('SELECT * FROM tabUser')"

# Export database
bench --site site1.local backup --with-files

# Import database
bench --site site1.local restore /path/to/database.sql

# Reset database (keeps files)
bench --site site1.local reinstall
```

---

## Background Jobs

```bash
# List scheduled jobs
bench --site site1.local list-jobs

# Enable scheduler
bench --site site1.local enable-scheduler

# Disable scheduler
bench --site site1.local disable-scheduler

# Run scheduler event
bench --site site1.local run-trigger

# Execute a scheduler method
bench --site site1.local execute frappe.utils.background_jobs.execute_method
```

---

## Logs & Debugging

```bash
# View logs
bench logs

# View error traceback
bench show-deploy-fail

# Clear cache
bench --site site1.local clear-cache

# Clear website cache
bench --site site1.local clear-website-cache

# Rebuild website routes
bench --site site1.local build-website-pages

# Check bench version
bench version

# Check site status
bench status
```

---

## Testing

```bash
# Run all tests
bench run-tests

# Run tests for specific app
bench --app erpnext run-tests

# Run specific test file
bench run-tests --app erpnext --test-module erpnext.stock.doctype.stock.test_stock

# Run tests in develop mode
bench run-tests --develop

# Run server-side JavaScript tests
bench run-tests --app erpnext --javascript

# Run Pytests for specific module
bench --site site1.local pytest erpnext.stock.doctype.stock
```

---

## Production Deployment

```bash
# Setup production
bench setup production

# Generate let’s encrypt certificate
bench setup letsencrypt site1.local

# Setup redis
bench setup redis

# Setup socketio
bench setup socketio

# Setup firewall
bench setup firewall

# Add to systemd
bench setup systemd
```

---

## Common Workflows

### Daily Development Workflow
```bash
# Pull latest changes
bench update

# Migrate all sites
bench --all migrate

# Build assets
bench build

# Clear cache
bench --all clear-cache
```

### Production Update Workflow
```bash
# Backup first
bench --site site1.local backup

# Pull changes
bench update --pull

# Migrate
bench --site site1.local migrate

# Build
bench build --app erpnext

# Clear cache
bench --site site1.local clear-cache
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Site not loading | `bench --site site1.local clear-cache` |
| Permission errors | `bench --site site1.local rebuild-permissions` |
| Slow performance | Check `frappe.log` or run with profiling |
| Lost admin password | `bench --site site1.local set-admin-password` |
| Database locked | `bench mysql -e "KILL ALL"` |

---

## Related Topics
- [Architecture](./01_architecture.md)
- [Directory Structure](./02_directory-structure.md)
