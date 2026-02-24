# Upgrade & Migration Intelligence

Safe patch sequencing, version compatibility matrix, rollback strategies, backup automation, and zero-downtime deployment methods.

---

## 1. Safe Patch Sequencing

### Patch Ordering Framework

```python
# Patch dependency and sequencing system

class PatchSequencer:
    """Manage safe patch sequencing for upgrades."""
    
    PATCH_CATEGORIES = {
        "schema": {"priority": 1, "risk": "HIGH"},      # Database schema changes
        "data": {"priority": 2, "risk": "MEDIUM"},       # Data migrations
        "config": {"priority": 3, "risk": "LOW"},         # Configuration updates
        "cleanup": {"priority": 4, "risk": "LOW"}        # Cleanup operations
    }
    
    def __init__(self):
        self.patches = []
        self.dependencies = {}
    
    def add_patch(self, patch_id, category, dependencies=None):
        """Add patch with dependencies."""
        self.patches.append({
            "id": patch_id,
            "category": category,
            "priority": self.PATCH_CATEGORIES[category]["priority"],
            "risk": self.PATCH_CATEGORIES[category]["risk"]
        })
        
        if dependencies:
            self.dependencies[patch_id] = dependencies
    
    def get_execution_sequence(self):
        """Get ordered patch execution sequence."""
        
        # Topological sort with priority
        in_degree = {p["id"]: 0 for p in self.patches}
        graph = {p["id"]: [] for p in self.patches}
        
        # Build dependency graph
        for patch_id, deps in self.dependencies.items():
            for dep in deps:
                graph[dep].append(patch_id)
                in_degree[patch_id] += 1
        
        # Kahn's algorithm with priority queue
        from heapq import heappush, heappop
        
        queue = []
        for patch in self.patches:
            if in_degree[patch["id"]] == 0:
                heappush(queue, (patch["priority"], patch["id"]))
        
        result = []
        while queue:
            _, patch_id = heappop(queue)
            result.append(patch_id)
            
            for neighbor in graph[patch_id]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    patch = next(p for p in self.patches if p["id"] == neighbor)
                    heappush(queue, (patch["priority"], neighbor))
        
        return result

# Example usage
sequencer = PatchSequencer()
sequencer.add_patch("add_company_field", "schema")
sequencer.add_patch("migrate_company_data", "data", ["add_company_field"])
sequencer.add_patch("update_company_settings", "config", ["migrate_company_data"])
sequencer.add_patch("remove_old_column", "cleanup", ["migrate_company_data"])

sequence = sequencer.get_execution_sequence()
# Result: ["add_company_field", "migrate_company_data", "update_company_settings", "remove_old_column"]
```

### Idempotent Patch Design

```python
# Idempotent patch example

import frappe

def execute():
    """
    Idempotent patch: Can be run multiple times safely.
    
    Principles:
    1. Check before creating
    2. Check before modifying
    3. Handle already-applied state
    """
    
    # Check if column already exists
    if not column_exists("Sales Order", "new_field"):
        frappe.db.sql("""
            ALTER TABLE `tabSales Order`
            ADD COLUMN `new_field` VARCHAR(140)
        """)
        print("Added new_field column")
    else:
        print("Column already exists - skipping")
    
    # Check before updating data
    unprocessed = frappe.db.sql("""
        SELECT name FROM `tabSales Order`
        WHERE new_field IS NULL
        LIMIT 1000
    """, as_dict=True)
    
    if unprocessed:
        for so in unprocessed:
            frappe.db.set_value("Sales Order", so.name, "new_field", "default_value")
        print(f"Updated {len(unprocessed)} records")
    else:
        print("All records already processed")

def column_exists(doctype, column):
    """Check if column exists in table."""
    table = f"tab{doctype.replace(' ', '')}"
    
    result = frappe.db.sql(f"""
        SELECT COUNT(*) FROM information_schema.columns
        WHERE table_name = '{table}'
        AND column_name = '{column}'
    """)
    
    return result[0][0] > 0
```

---

## 2. Version Compatibility Matrix

### Version Support Matrix

```python
VERSION_COMPATIBILITY = {
    "frappe": {
        "v14": {
            "supported_erpnext": ["v14"],
            "python": "3.8-3.10",
            "mariadb": "10.3-10.6",
            "redis": "5.0+",
            "node": "14-16",
            "deprecated": True,
            "eol_date": "2024-12-31"
        },
        "v15": {
            "supported_erpnext": ["v15"],
            "python": "3.10-3.11",
            "mariadb": "10.6-10.11",
            "redis": "6.0+",
            "node": "16-18",
            "deprecated": False,
            "eol_date": "2025-12-31"
        },
        "v16": {
            "supported_erpnext": ["v16"],
            "python": "3.11-3.12",
            "mariadb": "10.6-11.0",
            "redis": "7.0+",
            "node": "18-20",
            "deprecated": False,
            "eol_date": "2026-12-31"
        }
    },
    "breaking_changes": {
        "v14_to_v15": [
            {"component": "bench", "change": "Node 16 required", "action": "upgrade_node"},
            {"component": "framework", "change": "get_query -> get_list", "action": "code_update"},
            {"component": "payments", "change": "New payments app", "action": "install_app"}
        ],
        "v15_to_v16": [
            {"component": "python", "change": "Python 3.11 minimum", "action": "upgrade_python"},
            {"component": "db", "change": "JSON field changes", "action": "migration_script"}
        ]
    }
}

class VersionCompatibilityChecker:
    """Check version compatibility before upgrade."""
    
    def __init__(self, current_frappe, current_erpnext, target_frappe, target_erpnext):
        self.current = {"frappe": current_frappe, "erpnext": current_erpnext}
        self.target = {"frappe": target_frappe, "erpnext": target_erpnext}
    
    def check_compatibility(self):
        """Check if upgrade path is compatible."""
        
        issues = []
        
        # Check Frappe compatibility
        if not self._is_compatible(self.current["frappe"], self.target["frappe"]):
            issues.append({
                "severity": "CRITICAL",
                "message": f"Cannot upgrade from Frappe {self.current['frappe']} to {self.target['frappe']}"
            })
        
        # Check ERPNext compatibility with target Frappe
        supported = VERSION_COMPATIBILITY["frappe"][self.target["frappe"]]["supported_erpnext"]
        if self.target["erpnext"] not in supported:
            issues.append({
                "severity": "CRITICAL",
                "message": f"ERPNext {self.target['erpnext']} not compatible with Frappe {self.target['frappe']}"
            })
        
        # Check breaking changes
        breaking = self._get_breaking_changes()
        if breaking:
            issues.append({
                "severity": "WARNING",
                "breaking_changes": breaking,
                "action_required": "Review and address breaking changes"
            })
        
        return {
            "compatible": len([i for i in issues if i["severity"] == "CRITICAL"]) == 0,
            "issues": issues,
            "upgrade_path": self._suggest_upgrade_path()
        }
    
    def _get_breaking_changes(self):
        """Get list of breaking changes between versions."""
        
        key = f"v{self.current['frappe']}_to_v{self.target['frappe']}"
        return VERSION_COMPATIBILITY["breaking_changes"].get(key, [])
    
    def _suggest_upgrade_path(self):
        """Suggest safe upgrade path if direct upgrade not possible."""
        
        # Check if multi-hop upgrade needed
        current_major = int(self.current["frappe"].lstrip("v"))
        target_major = int(self.target["frappe"].lstrip("v"))
        
        if target_major - current_major > 1:
            return [
                f"v{current_major}",
                f"v{current_major + 1}",
                self.target["frappe"]
            ]
        
        return [self.current["frappe"], self.target["frappe"]]
```

---

## 3. Breaking Change Detection Checklist

### Pre-Upgrade Checklist

```python
BREAKING_CHANGE_DETECTION = {
    "database_schema": {
        "checks": [
            "Column type changes",
            "Column renames",
            "Table renames",
            "Index changes",
            "Foreign key changes"
        ],
        "detection_query": """
            SELECT 
                table_name,
                column_name,
                data_type,
                column_default
            FROM information_schema.columns
            WHERE table_schema = %s
            AND table_name LIKE 'tab%%'
        """
    },
    "api_changes": {
        "checks": [
            "Method signature changes",
            "Return type changes",
            "Deprecated methods",
            "New required parameters"
        ],
        "detection_script": """
            # Use AST to detect API changes
            import ast
            import inspect
            
            def get_method_signature(obj):
                return inspect.signature(obj)
        """
    },
    "configuration": {
        "checks": [
            "Site config changes",
            "New required settings",
            "Deprecated settings",
            "Default value changes"
        ]
    },
    "dependencies": {
        "checks": [
            "Python version requirements",
            "Node version requirements",
            "MariaDB version requirements",
            "Redis version requirements",
            "New system dependencies"
        ]
    }
}

def run_pre_upgrade_checks(site_name, target_version):
    """Run comprehensive pre-upgrade checks."""
    
    results = {
        "passed": [],
        "warnings": [],
        "failed": []
    }
    
    # Check 1: Database compatibility
    db_check = check_database_compatibility(site_name, target_version)
    if db_check["status"] == "pass":
        results["passed"].append("Database compatibility")
    else:
        results["failed"].append({
            "check": "Database compatibility",
            "details": db_check["issues"]
        })
    
    # Check 2: Custom app compatibility
    app_check = check_custom_app_compatibility(site_name, target_version)
    if app_check["compatible"]:
        results["passed"].append("Custom app compatibility")
    else:
        results["warnings"].append({
            "check": "Custom app compatibility",
            "apps": app_check["incompatible_apps"]
        })
    
    # Check 3: Disk space
    space_check = check_disk_space(site_name)
    if space_check["sufficient"]:
        results["passed"].append("Disk space")
    else:
        results["failed"].append({
            "check": "Disk space",
            "required": space_check["required_gb"],
            "available": space_check["available_gb"]
        })
    
    # Check 4: Backup verification
    backup_check = verify_backup_integrity(site_name)
    if backup_check["valid"]:
        results["passed"].append("Backup integrity")
    else:
        results["failed"].append({
            "check": "Backup integrity",
            "error": backup_check["error"]
        })
    
    return results

def check_database_compatibility(site_name, target_version):
    """Check if database is compatible with target version."""
    
    issues = []
    
    # Get current schema
    current_tables = frappe.db.sql("""
        SHOW TABLES
    "", as_dict=True)
    
    # Check for deprecated tables
    deprecated_tables = {
        "v15": ["tabSeries", "tabSingles"],
        "v16": ["tabEmail Digest", "tabDesktop Icon"]
    }
    
    target_deprecated = deprecated_tables.get(target_version, [])
    
    for table in current_tables:
        table_name = list(table.values())[0]
        if table_name in target_deprecated:
            issues.append(f"Table {table_name} deprecated in {target_version}")
    
    return {
        "status": "pass" if not issues else "fail",
        "issues": issues
    }
```

---

## 4. Rollback Strategy

### Rollback Implementation

```python
class UpgradeRollbackManager:
    """Manage upgrade rollback procedures."""
    
    def __init__(self, site_name):
        self.site_name = site_name
        self.backup_path = None
        self.restore_point = None
    
    def create_restore_point(self):
        """Create rollback restore point."""
        
        timestamp = frappe.utils.now()
        self.restore_point = {
            "timestamp": timestamp,
            "database_backup": self._backup_database(),
            "file_backup": self._backup_files(),
            "version_state": self._capture_version_state()
        }
        
        # Save restore point metadata
        frappe.cache.set_value(
            f"upgrade_restore_point:{self.site_name}",
            self.restore_point
        )
        
        return self.restore_point
    
    def rollback(self, reason=None):
        """Execute rollback to restore point."""
        
        restore_point = frappe.cache.get_value(
            f"upgrade_restore_point:{self.site_name}"
        )
        
        if not restore_point:
            raise Exception("No restore point found")
        
        try:
            # Step 1: Stop services
            self._stop_services()
            
            # Step 2: Restore database
            self._restore_database(restore_point["database_backup"])
            
            # Step 3: Restore files
            self._restore_files(restore_point["file_backup"])
            
            # Step 4: Restore versions
            self._restore_versions(restore_point["version_state"])
            
            # Step 5: Restart services
            self._start_services()
            
            # Log rollback
            frappe.logger().error(
                f"Upgrade rolled back for {self.site_name}. Reason: {reason}"
            )
            
            return {"success": True, "restored_to": restore_point["timestamp"]}
            
        except Exception as e:
            frappe.logger().error(f"Rollback failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _backup_database(self):
        """Create database backup."""
        from frappe.utils.backups import BackupGenerator
        
        backup = BackupGenerator(
            db_name=frappe.conf.db_name,
            user=frappe.conf.db_name,
            password=frappe.conf.db_password,
            db_host=frappe.conf.db_host or "localhost"
        )
        
        backup.take_dump()
        return backup.backup_path_db
    
    def _capture_version_state(self):
        """Capture current version state."""
        
        return {
            "frappe": frappe.__version__,
            "erpnext": frappe.get_module_list("erpnext").__version__ if frappe.get_module_list("erpnext") else None,
            "apps": {
                app: frappe.get_attr(f"{app}.__version__", "unknown")
                for app in frappe.get_installed_apps()
            }
        }

# Rollback triggers
ROLLBACK_TRIGGERS = {
    "database_migration_failure": {
        "severity": "CRITICAL",
        "auto_rollback": True,
        "notification": ["admin@company.com"]
    },
    "service_startup_failure": {
        "severity": "CRITICAL",
        "auto_rollback": True,
        "max_wait_seconds": 300
    },
    "critical_error_rate": {
        "severity": "HIGH",
        "auto_rollback": False,
        "threshold": "10 errors per minute",
        "notification": ["admin@company.com", "ops@company.com"]
    },
    "performance_degradation": {
        "severity": "MEDIUM",
        "auto_rollback": False,
        "threshold": "response time > 5s for 5 minutes",
        "notification": ["ops@company.com"]
    }
}
```

---

## 5. Backup Strategy Automation

### Automated Backup System

```python
class AutomatedBackupManager:
    """Automated backup management with verification."""
    
    BACKUP_SCHEDULE = {
        "full": {
            "frequency": "daily",
            "retention_days": 30,
            "time": "02:00",
            "verify": True
        },
        "incremental": {
            "frequency": "hourly",
            "retention_hours": 24,
            "verify": False
        },
        "pre_upgrade": {
            "trigger": "before_upgrade",
            "retention_days": 90,
            "verify": True,
            "offsite": True
        }
    }
    
    def __init__(self, site_name):
        self.site_name = site_name
    
    def create_backup(self, backup_type="full", verify=True):
        """Create backup with optional verification."""
        
        from frappe.utils.backups import BackupGenerator
        
        # Create backup
        backup = BackupGenerator(
            db_name=frappe.conf.db_name,
            user=frappe.conf.db_name,
            password=frappe.conf.db_password,
            db_host=frappe.conf.db_host or "localhost"
        )
        
        backup.take_dump()
        backup.copy_site_config()
        
        result = {
            "database": backup.backup_path_db,
            "files": backup.backup_path_files,
            "config": backup.backup_path_conf,
            "timestamp": frappe.utils.now(),
            "type": backup_type
        }
        
        # Verify if requested
        if verify:
            result["verification"] = self._verify_backup(result)
        
        # Store metadata
        self._store_backup_metadata(result)
        
        return result
    
    def _verify_backup(self, backup_paths):
        """Verify backup integrity."""
        
        import subprocess
        
        # Verify database dump
        db_verify = subprocess.run(
            ["mariadb", "--help"],
            capture_output=True
        )
        
        # Check file sizes
        import os
        
        db_size = os.path.getsize(backup_paths["database"])
        if db_size < 1024:  # Less than 1KB is suspicious
            return {
                "valid": False,
                "error": "Database backup too small"
            }
        
        # Test restore to temp database
        test_result = self._test_restore(backup_paths["database"])
        
        return {
            "valid": test_result["success"],
            "test_restore": test_result,
            "file_sizes": {
                "database_mb": db_size / (1024 * 1024)
            }
        }
    
    def _test_restore(self, backup_file):
        """Test restore to temporary database."""
        
        temp_db = f"test_restore_{frappe.utils.random_string(8)}"
        
        try:
            # Create temp database
            frappe.db.sql(f"CREATE DATABASE IF NOT EXISTS `{temp_db}`")
            
            # Restore backup
            import subprocess
            result = subprocess.run(
                [
                    "mariadb",
                    f"--database={temp_db}",
                    f"--user={frappe.conf.db_name}",
                    f"--password={frappe.conf.db_password}"
                ],
                stdin=open(backup_file, 'rb'),
                capture_output=True
            )
            
            if result.returncode == 0:
                return {"success": True}
            else:
                return {"success": False, "error": result.stderr.decode()}
                
        finally:
            # Cleanup
            frappe.db.sql(f"DROP DATABASE IF EXISTS `{temp_db}`")
    
    def cleanup_old_backups(self):
        """Clean up old backups based on retention policy."""
        
        import os
        from datetime import datetime, timedelta
        
        backup_dir = frappe.utils.get_site_path("private", "backups")
        
        for filename in os.listdir(backup_dir):
            filepath = os.path.join(backup_dir, filename)
            
            # Get file age
            file_time = datetime.fromtimestamp(os.path.getctime(filepath))
            age_days = (datetime.now() - file_time).days
            
            # Apply retention policy
            if age_days > self.BACKUP_SCHEDULE["full"]["retention_days"]:
                os.remove(filepath)
                print(f"Removed old backup: {filename}")

# Scheduler integration
scheduler_events = {
    "daily": ["custom_app.backup.daily_backup"],
    "hourly": ["custom_app.backup.hourly_backup"]
}
```

---

## 6. Schema Evolution Logic

### Safe Schema Migration

```python
class SchemaEvolutionManager:
    """Manage safe database schema evolution."""
    
    def add_column_safe(self, doctype, column_name, column_type, 
                        default=None, nullable=True):
        """
        Safely add column to existing table.
        
        Strategy for large tables:
        1. Add as nullable first
        2. Backfill data in batches
        3. Add default constraint
        4. Make non-nullable if required
        """
        
        table = f"tab{doctype.replace(' ', '')}"
        
        # Step 1: Add nullable column
        frappe.db.sql(f"""
            ALTER TABLE `{table}`
            ADD COLUMN `{column_name}` {column_type} NULL
        """)
        
        # Step 2: Backfill in batches (for large tables)
        if not nullable or default is not None:
            self._backfill_column(doctype, column_name, default)
        
        # Step 3: Add constraints
        if not nullable:
            frappe.db.sql(f"""
                ALTER TABLE `{table}`
                MODIFY COLUMN `{column_name}` {column_type} NOT NULL
            """)
        
        if default:
            frappe.db.sql(f"""
                ALTER TABLE `{table}`
                ALTER COLUMN `{column_name}` SET DEFAULT '{default}'
            """)
    
    def _backfill_column(self, doctype, column_name, default_value, batch_size=1000):
        """Backfill column data in batches."""
        
        table = f"tab{doctype.replace(' ', '')}"
        
        # Get total count
        total = frappe.db.count(doctype)
        processed = 0
        
        while processed < total:
            frappe.db.sql(f"""
                UPDATE `{table}`
                SET `{column_name}` = %s
                WHERE `{column_name}` IS NULL
                LIMIT %s
            """, (default_value, batch_size))
            
            processed += batch_size
            frappe.db.commit()
            
            print(f"Backfilled {processed}/{total} records")
    
    def drop_column_safe(self, doctype, column_name):
        """
        Safely drop column with verification.
        
        Steps:
        1. Verify no code references column
        2. Backup data
        3. Drop column
        """
        
        # Check for code references
        references = self._find_code_references(doctype, column_name)
        
        if references:
            raise Exception(
                f"Cannot drop column - found {len(references)} code references: "
                f"{', '.join(references[:5])}"
            )
        
        # Backup column data
        self._backup_column_data(doctype, column_name)
        
        # Drop column
        table = f"tab{doctype.replace(' ', '')}"
        frappe.db.sql(f"""
            ALTER TABLE `{table}`
            DROP COLUMN `{column_name}`
        """)
    
    def rename_column_safe(self, doctype, old_name, new_name):
        """Safely rename column."""
        
        table = f"tab{doctype.replace(' ', '')}"
        
        # MariaDB syntax
        frappe.db.sql(f"""
            ALTER TABLE `{table}`
            RENAME COLUMN `{old_name}` TO `{new_name}`
        """)
        
        # Update metadata
        self._update_field_metadata(doctype, old_name, new_name)

# Migration safety wrapper
def safe_migration(fn):
    """Decorator for safe migration execution."""
    
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Create savepoint
        frappe.db.savepoint("migration_start")
        
        try:
            result = fn(*args, **kwargs)
            
            # Commit on success
            frappe.db.commit()
            return result
            
        except Exception as e:
            # Rollback on failure
            frappe.db.rollback(save_point="migration_start")
            
            # Log failure
            frappe.log_error(f"Migration failed: {str(e)}")
            
            raise
    
    return wrapper
```

---

## 7. Zero-Downtime Deployment Method

### Blue-Green Deployment

```python
class ZeroDowntimeDeployer:
    """Zero-downtime deployment using blue-green strategy."""
    
    def __init__(self, site_name):
        self.site_name = site_name
        self.blue_env = f"{site_name}-blue"
        self.green_env = f"{site_name}-green"
        self.current_env = None
    
    def deploy(self, new_version):
        """Execute zero-downtime deployment."""
        
        try:
            # Step 1: Determine target environment
            target_env = self._get_inactive_environment()
            
            # Step 2: Prepare target environment
            self._prepare_environment(target_env, new_version)
            
            # Step 3: Run migrations on target
            self._run_migrations(target_env)
            
            # Step 4: Sync data (if needed)
            self._sync_data(target_env)
            
            # Step 5: Health check
            if not self._health_check(target_env):
                raise Exception(f"Health check failed for {target_env}")
            
            # Step 6: Switch traffic
            self._switch_traffic(target_env)
            
            # Step 7: Verify switch
            if not self._verify_deployment():
                self._rollback_traffic()
                raise Exception("Deployment verification failed")
            
            # Step 8: Update current environment
            self._set_active_environment(target_env)
            
            return {"success": True, "environment": target_env}
            
        except Exception as e:
            # Automatic rollback
            self._rollback_traffic()
            return {"success": False, "error": str(e)}
    
    def _prepare_environment(self, env, version):
        """Prepare deployment environment."""
        
        # Copy current database
        source_db = frappe.conf.db_name
        target_db = f"{source_db}_{env}"
        
        # Clone database
        frappe.db.sql(f"CREATE DATABASE IF NOT EXISTS `{target_db}`")
        
        # Use mysqldump and restore
        import subprocess
        
        # Dump current
        dump_cmd = [
            "mysqldump",
            f"--user={frappe.conf.db_name}",
            f"--password={frappe.conf.db_password}",
            source_db
        ]
        
        # Restore to target
        restore_cmd = [
            "mysql",
            f"--user={frappe.conf.db_name}",
            f"--password={frappe.conf.db_password}",
            target_db
        ]
        
        dump_proc = subprocess.Popen(dump_cmd, stdout=subprocess.PIPE)
        restore_proc = subprocess.Popen(restore_cmd, stdin=dump_proc.stdout)
        restore_proc.wait()
    
    def _run_migrations(self, env):
        """Run database migrations on target environment."""
        
        # Switch to target database temporarily
        original_db = frappe.conf.db_name
        frappe.conf.db_name = f"{original_db}_{env}"
        
        try:
            # Run migrations
            frappe.modules.patch_handler.run_all()
            frappe.db.commit()
        finally:
            frappe.conf.db_name = original_db
    
    def _health_check(self, env):
        """Health check on target environment."""
        
        checks = [
            self._check_database_connectivity(env),
            self._check_critical_endpoints(env),
            self._check_background_workers(env),
            self._check_error_rate(env)
        ]
        
        return all(checks)
    
    def _switch_traffic(self, target_env):
        """Switch traffic to new environment."""
        
        # Update load balancer / reverse proxy
        # This is infrastructure-specific
        
        # For nginx:
        config_path = f"/etc/nginx/sites-available/{self.site_name}"
        
        # Update upstream
        new_upstream = f"127.0.0.1:{8000 if 'blue' in target_env else 8001}"
        
        # Reload nginx
        import subprocess
        subprocess.run(["nginx", "-s", "reload"])
    
    def _verify_deployment(self):
        """Verify deployment health."""
        
        import requests
        import time
        
        # Wait for services to stabilize
        time.sleep(10)
        
        # Check health endpoint
        try:
            response = requests.get(
                f"https://{self.site_name}/api/method/health_check",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False

# Alternative: Rolling Deployment
class RollingDeployer:
    """Rolling deployment with batch restarts."""
    
    def deploy(self, new_version, batch_percentage=25):
        """Deploy in batches for zero downtime."""
        
        workers = self._get_worker_list()
        batch_size = max(1, int(len(workers) * batch_percentage / 100))
        
        for i in range(0, len(workers), batch_size):
            batch = workers[i:i + batch_size]
            
            # Remove batch from load balancer
            self._drain_workers(batch)
            
            # Update batch
            self._update_workers(batch, new_version)
            
            # Health check batch
            if not self._health_check_batch(batch):
                # Rollback this batch
                self._rollback_batch(batch)
                return {"success": False, "failed_at": i}
            
            # Add batch back to load balancer
            self._activate_workers(batch)
        
        return {"success": True}
```

---

## Summary: Upgrade Decision Matrix

| Scenario | Strategy | Downtime | Risk Level |
|----------|----------|----------|------------|
| Patch release (x.x.1) | Direct update | < 1 min | Low |
| Minor release (x.1) | Blue-green | 0 min | Medium |
| Major release (1.x) | Staged rollout | 5-10 min | High |
| Custom app update | Rolling | 0 min | Medium |
| Database schema change | Maintenance window | 10-30 min | High |
| Multi-version jump | Phased (step-by-step) | Multiple windows | Critical |

**Pre-Upgrade Checklist:**

- [ ] Full backup created and verified
- [ ] Test environment validated
- [ ] Breaking changes reviewed
- [ ] Rollback plan documented
- [ ] Maintenance window scheduled
- [ ] Team on standby
- [ ] Health checks prepared
- [ ] Monitoring alerts configured

---

## FRAPPE VERSION-SPECIFIC GUIDANCE

### Version Compatibility Matrix

| Frappe Version | ERPNext Version | Python | MariaDB | Node.js | Status |
|----------------|-----------------|--------|---------|---------|--------|
| v14.x | v14.x | 3.10-3.11 | 10.6+ | 16.x | LTS ✅ |
| v15.x | v15.x | 3.10-3.12 | 10.9+ | 18.x | Current ✅ |
| v16.x | v16.x (beta) | 3.11-3.12 | 10.11+ | 20.x | Preview ⚠️ |

### v14 → v15 Migration Guide

```python
# Pre-migration validation script
def validate_v15_readiness():
    """Check if system is ready for v15 upgrade."""
    
    checks = {
        "python_version": _check_python_version(min="3.10"),
        "node_version": _check_node_version(min="18"),
        "mariadb_version": _check_mariadb_version(min="10.9"),
        "custom_apps": _check_custom_app_compatibility(),
        "hooks_usage": _check_deprecated_hooks(),
        "python2_legacy": _check_python2_code(),
    }
    
    # Run all checks
    results = {}
    for check_name, check_fn in checks.items():
        try:
            results[check_name] = check_fn()
        except Exception as e:
            results[check_name] = {"status": "FAIL", "error": str(e)}
    
    return results

def _check_deprecated_hooks():
    """Check for deprecated hook usage in v15."""
    
    deprecated_hooks = [
        "app_include_js",  # Use app_include_js in hooks.py
        "web_include_js",  # Use web_form_js in web form
        "stylesheet",      # Use website_route_rules
    ]
    
    issues = []
    for app in frappe.get_installed_apps():
        hooks_file = frappe.get_app_path(app, "hooks.py")
        if os.path.exists(hooks_file):
            with open(hooks_file) as f:
                content = f.read()
                for hook in deprecated_hooks:
                    if hook in content:
                        issues.append(f"{app}: uses deprecated '{hook}'")
    
    return {
        "status": "FAIL" if issues else "PASS",
        "issues": issues
    }

def _check_custom_app_compatibility():
    """Check custom app compatibility with v15."""
    
    issues = []
    
    for app in frappe.get_installed_apps():
        app_path = frappe.get_app_path(app)
        
        # Check for Python 3.10+ incompatible code
        python_files = glob.glob(f"{app_path}/**/*.py", recursive=True)
        
        for pyfile in python_files[:50]:  # Sample check
            try:
                with open(pyfile) as f:
                    content = f.read()
                    
                    # Check for Python 2 patterns
                    if "print " in content and "print(" not in content:
                        issues.append(f"{pyfile}: Python 2 print syntax")
                    
                    if "except Exception, e:" in content:
                        issues.append(f"{pyfile}: Python 2 exception syntax")
                    
                    if "u'" in content or 'u"' in content:
                        issues.append(f"{pyfile}: Python 2 unicode literals")
            except:
                continue
    
    return {
        "status": "FAIL" if issues else "PASS",
        "issues": issues
    }
```

### v15 Key Changes & Breaking Changes

| Change | Impact | Migration Action |
|--------|--------|------------------|
| REST API v2 | Medium | Update API clients to use `/api/v2/` |
| Whitelist changes | High | Review all `@frappe.whitelist()` methods |
| Desk JS refactored | Low | Client scripts generally compatible |
| Database migrations | High | Run `bench migrate` before testing |
| Redis 7.x required | Medium | Upgrade Redis before bench update |
| New permission system | High | Test all custom permission checks |

### v15 → v16 Preview (Beta)

```python
# v16 readiness checker
def check_v16_readiness():
    """Prepare for v16 migration."""
    
    return {
        "requirements": {
            "python": "3.11+ (REQUIRED)",
            "node": "20.x+ (REQUIRED)",
            "mariadb": "10.11+ (REQUIRED)",
            "redis": "7.0+ (REQUIRED)"
        },
        "breaking_changes": [
            "Python 3.10 will be minimum",
            "Many v14 APIs deprecated",
            "New authentication system",
            "Vue 3 based desk (optional)"
        ],
        "new_features_preview": [
            "AI-assisted report builder",
            "Real-time collaboration",
            "GraphQL API support",
            "Enhanced mobile desk"
        ]
    }
```

### Version-Specific Code Patterns

```python
# V14 Compatible
frappe.response["message"] = {"success": True}

# V15+ - Preferred
frappe.flags = {"v15_compatible": True}
# Use frappe.publish_realtime for responses

# V14 Controller
class MyDoc(Document):
    def validate(self):
        pass

# V15+ Controller - with async support
import asyncio

class MyDoc(Document):
    async def validate(self):
        # Async validation supported in v15
        await self.async_check()
    
    def validate(self):
        # Sync fallback for backward compatibility
        pass
```

### Bench Commands by Version

```bash
# v14 Commands
bench update --patch
bench migrate
bench switch-to-branch version-14

# v15 Commands  
bench update --patch
bench migrate
bench switch-to-branch version-15
bench add-to-email-queue  # NEW in v15

# v16 Commands (Preview)
bench update --patch
bench migrate --skip-failing
bench switch-to-branch version-16
bench doctor  # NEW - health check
```

### Quick Version Detection

```python
def get_version_info():
    """Get current Frappe/ERPNext version info."""
    
    import frappe
    import subprocess
    
    # Get bench version
    result = subprocess.run(
        ["bench", "version"], 
        capture_output=True, 
        text=True
    )
    
    return {
        "frappe_version": frappe.__version__,
        "erpnext_version": frappe.get_attr("erpnext").__version__ if hasattr(frappe, "erpnext") else "N/A",
        "bench_output": result.stdout,
        "python_version": subprocess.run(
            ["python", "--version"], 
            capture_output=True, 
            text=True
        ).stdout
    }
```

### Upgrade Decision Matrix

| Current Version | Target Version | Recommended Approach |
|-----------------|----------------|---------------------|
| v13 | v14 or v15 | Go directly to v15 (skip v14 if possible) |
| v14 | v15 | In-place upgrade, test thoroughly |
| v14 | v16 | Wait for v16 stable, or step through v15 |
| v15 | v16 | Wait for stable, test beta first |

### Rollback Scripts by Version

```python
# Emergency rollback functions

def rollback_v15_to_v14():
    """Emergency rollback from v15 to v14."""
    
    # 1. Stop all workers
    subprocess.run(["bench", "stop-all-workers"])
    
    # 2. Restore database
    subprocess.run([
        "bench", "--site", "site1.local", 
        "restore", "/path/to/v14_backup.sql"
    ])
    
    # 3. Switch branches
    subprocess.run(["bench", "switch-to-branch", "version-14", "--apps", "frappe"])
    subprocess.run(["bench", "switch-to-branch", "version-14", "--apps", "erpnext"])
    
    # 4. Reinstall apps
    subprocess.run(["bench", "--site", "site1.local", "reinstall-apps"])
    
    # 5. Clear cache
    subprocess.run(["bench", "--site", "site1.local", "clear-cache"])

