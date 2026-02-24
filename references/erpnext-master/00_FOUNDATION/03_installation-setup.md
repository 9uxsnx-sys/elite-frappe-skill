# ERPNext Installation & Setup

## Quick Reference
Use `bench` CLI to install ERPNext. Standard flow: bench init → bench get-app erpnext → bench new-site → bench install-app erpnext.

## AI Prompt
\`\`\`
When troubleshooting installation:
1. Check Python version (3.10+)
2. Check Node.js version (16+)
3. Verify MariaDB/MySQL connection
4. Check bench directory permissions
5. Review error logs in logs/bench-start.log
\`\`\`

---

## Prerequisites

### System Requirements
- Ubuntu 20.04/22.04 or Debian 10+
- Python 3.10+
- Node.js 16+ / 18+
- MariaDB 10.6+ / MySQL 8.0+
- Redis 6+
- Nginx (production)

### Hardware Requirements
| Environment | RAM | CPU | Disk |
|-------------|-----|-----|------|
| Development | 4GB | 2 | 20GB |
| Production | 8GB+ | 4+ | 50GB+ |

---

## Installation Methods

### Method 1: Easy Install (Recommended)
\`\`\`bash
# Download and run easy install script
wget https://frappe.io/easy-install.py
python3 easy-install.py --production --site yoursite.local
\`\`\`

### Method 2: Manual Installation
\`\`\`bash
# 1. Install bench
pip install frappe-bench

# 2. Initialize bench
bench init frappe-bench --frappe-branch version-15

# 3. Create site
cd frappe-bench
bench new-site yoursite.local

# 4. Get ERPNext
bench get-app erpnext --branch version-15

# 5. Install ERPNext on site
bench --site yoursite.local install-app erpnext

# 6. Start development server
bench start
\`\`\`

### Method 3: Docker
\`\`\`yaml
# docker-compose.yml
version: "3"
services:
  erpnext:
    image: frappe/erpnext:v15
    ports:
      - "8000:8000"
    environment:
      - FRAPPE_SITE_NAME=site1.localhost
\`\`\`

---

## Version Branches

| Branch | Status | Use Case |
|--------|--------|----------|
| version-14 | Stable | Production |
| version-15 | Stable | Production |
| version-16 | Latest | New features |
| develop | Beta | Development |

\`\`\`bash
# Get specific version
bench get-app erpnext --branch version-15
\`\`\`

---

## Initial Setup

### 1. Company Setup
\`\`\`
Setup > Company > New Company
- Company Name
- Abbreviation (used in account names)
- Country
- Currency
- Chart of Accounts (Standard/Custom)
\`\`\`

### 2. Fiscal Year
\`\`\`
Setup > Fiscal Year > New Fiscal Year
- Year: 2024
- Year Start Date: 2024-01-01
- Year End Date: 2024-12-31
\`\`\`

### 3. Users & Roles
\`\`\`
Setup > User > New User
- Email
- First Name, Last Name
- Roles: Sales User, Purchase User, etc.
\`\`\`

### 4. Chart of Accounts
\`\`\`
Setup > Chart of Accounts
- Import from template
- Or create manually
- Accounts created automatically with Company abbreviation
\`\`\`

---

## Common Setup Issues

### Issue: MariaDB Connection Error
\`\`\`bash
# Check MariaDB status
sudo systemctl status mariadb

# Reset root password
sudo mysql_secure_installation

# Create frappe user
mysql -u root -p
CREATE USER 'frappe'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON *.* TO 'frappe'@'localhost';
FLUSH PRIVILEGES;
\`\`\`

### Issue: Permission Denied
\`\`\`bash
# Fix permissions
sudo chown -R $USER:$USER ~/frappe-bench
chmod -R 755 ~/frappe-bench
\`\`\`

### Issue: Redis Connection Error
\`\`\`bash
# Start Redis
sudo systemctl start redis
sudo systemctl enable redis

# Check Redis
redis-cli ping  # Should return PONG
\`\`\`

---

## Bench Commands Reference

### Site Management
\`\`\`bash
bench new-site [site-name]           # Create new site
bench --site [site] list-apps        # List installed apps
bench --site [site] install-app [app] # Install app
bench --site [site] uninstall-app [app] # Uninstall app
bench --site [site] drop-site        # Delete site
\`\`\`

### Database Operations
\`\`\`bash
bench --site [site] backup           # Create backup
bench --site [site] restore [file]   # Restore backup
bench --site [site] migrate          # Run migrations
bench --site [site] console          # Python console
\`\`\`

### Maintenance
\`\`\`bash
bench --site [site] clear-cache      # Clear cache
bench --site [site] reload-doc       # Reload doctype
bench update                         # Update all apps
bench restart                        # Restart services
\`\`\`

### Production Setup
\`\`\`bash
bench setup production               # Setup production mode
bench setup nginx                    # Configure nginx
bench setup supervisor               # Configure supervisor
sudo supervisorctl restart all       # Restart all processes
\`\`\`

---

## Configuration Files

### site_config.json
\`\`\`json
{
  "db_name": "site1",
  "db_password": "password",
  "developer_mode": 1,
  "disable_website_cache": 1
}
\`\`\`

### common_site_config.json
\`\`\`json
{
  "background_workers": 2,
  "file_watcher_port": 6787,
  "frappe_user": "frappe",
  "gunicorn_workers": 4,
  "redis_cache": "redis://localhost:13000",
  "redis_queue": "redis://localhost:11000",
  "redis_socketio": "redis://localhost:12000"
}
\`\`\`

---

## Related Topics
- [ERPNext Overview](./01_erpnext-overview.md)
- [Company Setup](./05_company-setup.md)
