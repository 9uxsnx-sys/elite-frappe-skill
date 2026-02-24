# Failure Scenario Simulation

Collapse point analysis for 500k invoices, 5k concurrent users, infrastructure failures, and permission misconfigurations.

---

## 1. Scenario: 500k Invoices

### Load Simulation

```python
# failure_scenarios/invoice_volume_failure.py

import frappe
import time
from datetime import datetime

class InvoiceVolumeFailureSimulator:
    """
    Simulate system behavior under 500k invoice volume.
    
    COLLAPSE POINTS:
    - Database: Slow queries without indexes (> 2s response)
    - Memory: Worker exhaustion (OOM errors)
    - Disk: Log file explosion (> 50GB)
    - Network: Timeout cascades
    """
    
    SIMULATION_PARAMS = {
        "invoice_count": 500000,
        "concurrent_users": 100,
        "daily_new_invoices": 1000,
        "report_complexity": "multi_month"
    }
    
    def simulate_query_performance(self):
        """Simulate query performance degradation."""
        
        # Baseline (10k invoices): < 100ms
        # 100k invoices: ~500ms (with indexes)
        # 500k invoices: ~3s (without optimization)
        # 500k invoices: ~800ms (with proper indexes)
        
        results = {}
        
        # Test 1: Simple filter query
        start = time.time()
        frappe.get_all("Sales Invoice",
            filters={"customer": "_Test Customer"},
            fields=["name", "grand_total"],
            limit=20
        )
        results["filtered_list"] = {
            "time_ms": (time.time() - start) * 1000,
            "threshold": 500,
            "status": "OK" if (time.time() - start) < 0.5 else "DEGRADED"
        }
        
        # Test 2: Aggregate query (aging report)
        start = time.time()
        frappe.db.sql("""
            SELECT 
                customer,
                SUM(grand_total) as total,
                DATEDIFF(CURDATE(), due_date) as days_overdue
            FROM `tabSales Invoice`
            WHERE docstatus = 1
            AND outstanding_amount > 0
            GROUP BY customer
        """)
        results["aggregate_report"] = {
            "time_ms": (time.time() - start) * 1000,
            "threshold": 5000,
            "status": "OK" if (time.time() - start) < 5 else "FAILING"
        }
        
        # Test 3: Count query
        start = time.time()
        frappe.db.count("Sales Invoice", {"docstatus": 1})
        results["count_query"] = {
            "time_ms": (time.time() - start) * 1000,
            "threshold": 100,
            "status": "OK" if (time.time() - start) < 0.1 else "DEGRADED"
        }
        
        return results
    
    def identify_failure_modes(self):
        """Identify specific failure modes at 500k volume."""
        
        return {
            "database_failures": {
                "slow_queries": {
                    "symptom": "Query time > 5 seconds",
                    "impact": "Request timeouts, user frustration",
                    "prevention": "Add indexes on customer, posting_date, status",
                    "detection": "Enable slow query log > 1s"
                },
                "connection_exhaustion": {
                    "symptom": "Too many connections errors",
                    "impact": "Complete service outage",
                    "prevention": "Connection pooling, max_connections=500",
                    "detection": "Monitor mysql> show status like 'Threads_connected'"
                },
                "lock_contention": {
                    "symptom": "Lock wait timeout exceeded",
                    "impact": "Deadlocks, transaction failures",
                    "prevention": "Row-level locking, transaction batching",
                    "detection": "SHOW ENGINE INNODB STATUS"
                }
            },
            "application_failures": {
                "memory_exhaustion": {
                    "symptom": "OOM Killer, 502 errors",
                    "impact": "Worker process termination",
                    "prevention": "Limit query results, streaming responses",
                    "detection": "Monitor worker memory usage"
                },
                "worker_starvation": {
                    "symptom": "Request queue buildup",
                    "impact": "Cascading slowdowns",
                    "prevention": "Auto-scaling, circuit breakers",
                    "detection": "Queue depth monitoring"
                }
            },
            "infrastructure_failures": {
                "disk_space": {
                    "symptom": "No space left on device",
                    "impact": "Writes fail, corruption risk",
                    "prevention": "Log rotation, 80% alert threshold",
                    "detection": "df -h monitoring"
                },
                "backup_time": {
                    "symptom": "Backup takes > 8 hours",
                    "impact": "No recovery point, maintenance window overflow",
                    "prevention": "Incremental backups, hot backups",
                    "detection": "Backup duration tracking"
                }
            }
        }
    
    def mitigation_strategies(self):
        """Define mitigation strategies for 500k invoice volume."""
        
        return {
            "immediate": {
                "database_indexes": [
                    "CREATE INDEX idx_customer_date ON `tabSales Invoice` (customer, posting_date)",
                    "CREATE INDEX idx_status_date ON `tabSales Invoice` (status, posting_date)",
                    "ANALYZE TABLE `tabSales Invoice`"
                ],
                "query_optimization": [
                    "Use EXPLAIN for slow queries",
                    "Replace get_all with Query Builder for complex filters",
                    "Add LIMIT clauses to all list queries"
                ],
                "caching": [
                    "Cache customer outstanding amount",
                    "Cache monthly sales totals",
                    "Cache aging buckets"
                ]
            },
            "short_term": {
                "archiving": [
                    "Move invoices > 2 years to archive table",
                    "Create archive query view for reporting",
                    "Implement archive retrieval workflow"
                ],
                "partitioning": [
                    "Partition by fiscal year",
                    "Partition by company (multi-tenant)",
                    "Use partition pruning in queries"
                ]
            },
            "long_term": {
                "read_replicas": [
                    "Report queries to read replica",
                    "Real-time replication monitoring",
                    "Automatic failover"
                ],
                "data_warehouse": [
                    "ETL to data warehouse for analytics",
                    "Keep operational data lean",
                    "Separate OLTP and OLAP"
                ]
            }
        }

# Survival thresholds
VOLUME_SURVIVAL_THRESHOLDS = {
    "critical": {
        "list_query_ms": 500,
        "report_query_seconds": 10,
        "concurrent_reports": 3,
        "database_cpu_percent": 80
    },
    "warning": {
        "list_query_ms": 1000,
        "report_query_seconds": 30,
        "concurrent_reports": 5,
        "database_cpu_percent": 60
    }
}
```

---

## 2. Scenario: 5k Concurrent Users

### Concurrency Simulation

```python
# failure_scenarios/concurrency_failure.py

import frappe
import threading
import time
from concurrent.futures import ThreadPoolExecutor

class ConcurrencyFailureSimulator:
    """
    Simulate system under 5,000 concurrent users.
    
    COLLAPSE POINTS:
    - Connection pool exhaustion
    - CPU saturation
    - Memory exhaustion
    - Thread deadlock
    """
    
    SIMULATION_PARAMS = {
        "concurrent_users": 5000,
        "requests_per_user_per_minute": 10,
        "peak_multiplier": 3,
        "think_time_seconds": 5
    }
    
    def calculate_load(self):
        """Calculate system load metrics."""
        
        params = self.SIMULATION_PARAMS
        
        # Peak requests per minute
        base_rpm = params["concurrent_users"] * params["requests_per_user_per_minute"]
        peak_rpm = base_rpm * params["peak_multiplier"]
        
        # Workers needed (120 req/min per worker)
        workers_needed = peak_rpm / 120
        
        # Database connections (2 per worker)
        db_connections = workers_needed * 2
        
        # Memory (256MB per worker)
        memory_gb = (workers_needed * 256) / 1024
        
        return {
            "base_requests_per_minute": base_rpm,
            "peak_requests_per_minute": peak_rpm,
            "gunicorn_workers": int(workers_needed * 1.5),  # Headroom
            "database_connections": int(db_connections),
            "memory_required_gb": memory_gb,
            "recommended_config": {
                "cpu_cores": max(16, int(workers_needed / 2)),
                "memory_gb": max(32, int(memory_gb * 1.5)),
                "db_max_connections": min(500, int(db_connections * 2))
            }
        }
    
    def simulate_thread_saturation(self):
        """Simulate thread pool saturation."""
        
        def worker_task(user_id):
            """Simulate user request."""
            try:
                # Simulate form load
                time.sleep(0.1)
                
                # Simulate save operation
                time.sleep(0.2)
                
                return {"user": user_id, "status": "success"}
            except Exception as e:
                return {"user": user_id, "status": "failed", "error": str(e)}
        
        # Simulate with 5k users
        results = {"success": 0, "failed": 0, "timeouts": 0}
        
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(worker_task, i) for i in range(5000)]
            
            for future in futures:
                try:
                    result = future.result(timeout=10)
                    if result["status"] == "success":
                        results["success"] += 1
                    else:
                        results["failed"] += 1
                except TimeoutError:
                    results["timeouts"] += 1
        
        return results
    
    def identify_collapse_points(self):
        """Identify where system collapses under load."""
        
        return {
            "connection_pool_exhaustion": {
                "trigger": "Threads_connected > max_connections",
                "symptoms": [
                    "MySQL Error 1040: Too many connections",
                    "Request queue buildup",
                    "Timeout errors"
                ],
                "threshold": 500,  # MySQL default
                "prevention": [
                    "Implement connection pooling",
                    "Set max_connections based on workers",
                    "Add connection timeout: 10s"
                ]
            },
            "cpu_saturation": {
                "trigger": "CPU > 90% sustained",
                "symptoms": [
                    "Request latency increase",
                    "Context switching overhead",
                    "Load average > CPU cores"
                ],
                "threshold": "90% for 5 minutes",
                "prevention": [
                    "Horizontal scaling",
                    "Query optimization",
                    "Caching layer"
                ]
            },
            "memory_pressure": {
                "trigger": "Memory usage > 90%",
                "symptoms": [
                    "OOM Killer invocation",
                    "Swap usage increase",
                    "GC pressure (Python)"
                ],
                "threshold": "85% for 2 minutes",
                "prevention": [
                    "Worker memory limits",
                    "Query result limits",
                    "Streaming responses"
                ]
            },
            "thread_deadlock": {
                "trigger": "Circular lock dependencies",
                "symptoms": [
                    "Requests hang indefinitely",
                    "No CPU activity",
                    "Deadlock in logs"
                ],
                "threshold": "Any occurrence",
                "prevention": [
                    "Lock ordering conventions",
                    "Lock timeout settings",
                    "Deadlock detection"
                ]
            }
        }

# Concurrency survival matrix
CONCURRENCY_SURVIVAL = {
    "small_deployment": {
        "max_concurrent": 50,
        "hardware": "2 CPU, 4GB RAM",
        "failure_mode": "Memory pressure at 80 users"
    },
    "medium_deployment": {
        "max_concurrent": 200,
        "hardware": "4 CPU, 8GB RAM",
        "failure_mode": "Connection pool at 300 users"
    },
    "large_deployment": {
        "max_concurrent": 500,
        "hardware": "8 CPU, 16GB RAM",
        "failure_mode": "CPU saturation at 600 users"
    },
    "enterprise_deployment": {
        "max_concurrent": 1500,
        "hardware": "16 CPU, 32GB RAM",
        "failure_mode": "Network I/O at 2000 users"
    },
    "cluster_deployment": {
        "max_concurrent": 5000,
        "hardware": "4x Large nodes + Load balancer",
        "failure_mode": "Database bottleneck at 8000 users"
    }
}
```

---

## 3. Scenario: Redis Failure

### Cache Failure Impact

```python
# failure_scenarios/redis_failure.py

import frappe

class RedisFailureSimulator:
    """
    Simulate system behavior when Redis fails.
    
    COLLAPSE POINTS:
    - Session loss (users logged out)
    - Rate limiting bypass
    - Cache stampede (database overload)
    - Background job queue loss
    """
    
    def simulate_session_loss(self):
        """Simulate impact of session store failure."""
        
        # Without Redis sessions:
        # - Users logged out immediately
        # - All unsaved work lost
        # - CSRF tokens invalid
        
        impact = {
            "immediate": {
                "user_sessions": "All invalidated",
                "unsaved_forms": "Data lost",
                "active_workflows": "State unknown"
            },
            "recovery_time": {
                "sessions_restored": "Never (new login required)",
                "service_degraded_duration": "Until Redis restored"
            },
            "mitigation": {
                "session_backup": "Database-backed sessions",
                "graceful_degradation": "Allow local session temporarily",
                "user_notification": "Immediate alert about logout"
            }
        }
        
        return impact
    
    def simulate_cache_stampede(self):
        """Simulate cache stampede when Redis restarts cold."""
        
        # All requests hit database simultaneously
        stampede_scenario = {
            "trigger": "Redis restart with empty cache",
            "progression": [
                "0s: Redis restarts",
                "0-5s: First requests hit DB",
                "5-30s: 1000x normal DB load",
                "30s: DB connection pool exhausted",
                "30-60s: Requests queue/begin failing",
                "60s+: Cascading failures"
            ],
            "prevention": [
                "Warm cache before switch",
                "Circuit breaker on DB load",
                "Request coalescing",
                "Staggered cache warming"
            ],
            "detection": [
                "DB connection count spike",
                "Query time > 1s",
                "Cache hit rate < 10%"
            ]
        }
        
        return stampede_scenario
    
    def simulate_queue_loss(self):
        """Simulate impact of losing background job queue."""
        
        # RQ jobs stored in Redis - loss means:
        queue_impact = {
            "pending_jobs": "Permanently lost",
            "scheduled_jobs": "Never execute",
            "email_notifications": "Never sent",
            "report_generation": "Never completes",
            "integration_syncs": "Data inconsistency"
        }
        
        recovery_strategy = {
            "immediate": [
                "Alert operations team",
                "Queue critical jobs for manual processing",
                "Notify affected users"
            ],
            "short_term": [
                "Restart Redis from AOF if available",
                "Resubmit critical jobs",
                "Verify data consistency"
            ],
            "long_term": [
                "Enable Redis persistence (AOF + RDB)",
                "Redis Sentinel for HA",
                "Backup queue to database before enqueue"
            ]
        }
        
        return {
            "impact": queue_impact,
            "recovery": recovery_strategy
        }

# Redis resilience recommendations
REDIS_RESILIENCE = {
    "persistence": {
        "aof_enabled": True,
        "aof_fsync": "everysec",
        "rdb_enabled": True,
        "save_intervals": ["900 1", "300 10", "60 10000"]
    },
    "high_availability": {
        "sentinel_enabled": True,
        "sentinel_count": 3,
        "replica_count": 1,
        "auto_failover": True
    },
    "monitoring": {
        "memory_usage_threshold": "80%",
        "connected_clients_threshold": 1000,
        "cache_hit_rate_threshold": "90%"
    }
}
```

---

## 4. Scenario: Background Jobs Queue Overflow

### Queue Failure Analysis

```python
# failure_scenarios/queue_overflow.py

import frappe

class QueueOverflowSimulator:
    """
    Simulate background job queue overflow.
    
    COLLAPSE POINTS:
    - Queue length > memory limit
    - Worker saturation
    - Priority inversion (long jobs blocking short)
    - Dead letter queue overflow
    """
    
    def simulate_queue_buildup(self):
        """Simulate progressive queue buildup."""
        
        timeline = {
            "normal": {
                "queue_depth": "< 100",
                "worker_utilization": "< 70%",
                "job_latency": "< 10s",
                "status": "Healthy"
            },
            "warning": {
                "queue_depth": "100-1000",
                "worker_utilization": "70-90%",
                "job_latency": "10s-5min",
                "status": "Degraded"
            },
            "critical": {
                "queue_depth": "1000-10000",
                "worker_utilization": "> 95%",
                "job_latency": "5min-1hour",
                "status": "Failing"
            },
            "collapse": {
                "queue_depth": "> 10000",
                "worker_utilization": "100%",
                "job_latency": "> 1 hour",
                "status": "COLLAPSE - Jobs timing out"
            }
        }
        
        return timeline
    
    def identify_causes(self):
        """Identify common causes of queue overflow."""
        
        return {
            "sudden_spike": {
                "cause": "Bulk operation (import, export)",
                "signature": "Queue jumps from <100 to >5000 in minutes",
                "prevention": "Queue bulk ops separately, add workers",
                "response": "Scale workers immediately, pause non-critical jobs"
            },
            "slow_job_stall": {
                "cause": "Job taking longer than timeout",
                "signature": "Workers stuck, queue grows steadily",
                "prevention": "Proper timeout configuration, job profiling",
                "response": "Kill stuck jobs, increase timeout or optimize"
            },
            "worker_crashes": {
                "cause": "Workers dying due to OOM/errors",
                "signature": "Workers = 0, queue grows",
                "prevention": "Worker monitoring, auto-restart",
                "response": "Restart workers, check error logs"
            },
            "priority_inversion": {
                "cause": "Long jobs blocking short urgent jobs",
                "signature": "Short queue growing while workers busy",
                "prevention": "Separate queues by priority",
                "response": "Requeue long jobs to long queue"
            }
        }
    
    def recovery_procedures(self):
        """Define queue overflow recovery procedures."""
        
        return {
            "immediate_response": [
                "Scale workers: bench worker --queue default --burst",
                "Pause non-critical scheduled jobs",
                "Alert on-call engineer"
            ],
            "queue_management": [
                "Inspect queue: bench execute frappe.utils.background_jobs.get_jobs",
                "Cancel stuck jobs: bench execute frappe.utils.background_jobs.remove_failed_jobs",
                "Requeue with priority: Use high priority for critical jobs"
            ],
            "root_cause": [
                "Analyze job execution times from logs",
                "Identify slowest jobs for optimization",
                "Check for failed jobs causing retries"
            ]
        }

# Queue monitoring thresholds
QUEUE_ALERT_THRESHOLDS = {
    "default": {
        "warning": 100,
        "critical": 1000,
        "emergency": 5000
    },
    "short": {
        "warning": 50,
        "critical": 200,
        "emergency": 1000
    },
    "long": {
        "warning": 20,
        "critical": 50,
        "emergency": 200
    }
}
```

---

## 5. Scenario: Migration Failure

### Database Migration Collapse

```python
# failure_scenarios/migration_failure.py

import frappe

class MigrationFailureSimulator:
    """
    Simulate database migration failure scenarios.
    
    COLLAPSE POINTS:
    - Partial migration (inconsistent state)
    - Lock timeout during alter table
    - Data corruption during migration
    - Rollback failure
    """
    
    def simulate_partial_migration(self):
        """Simulate partial migration leaving system inconsistent."""
        
        # Scenario: Migration adds column, fails on data migration
        partial_state = {
            "schema": {
                "new_column_exists": True,
                "old_column_exists": True,
                "constraint_applied": False
            },
            "data": {
                "new_column_populated": "50%",  # Partial
                "orphaned_records": True,
                "referential_integrity": "Broken"
            },
            "impact": {
                "forms": "Load errors (missing data)",
                "reports": "Incorrect calculations",
                "integrations": "API failures"
            }
        }
        
        recovery = {
            "detection": [
                "Migration log shows partial completion",
                "Error logs show constraint violations",
                "User reports form loading issues"
            ],
            "assessment": [
                "Identify which patches succeeded",
                "Identify data inconsistencies",
                "Determine if rollback possible"
            ],
            "remediation": [
                "If rollback: Restore from backup",
                "If forward: Complete partial migration",
                "If stuck: Manual SQL repair"
            ]
        }
        
        return {"state": partial_state, "recovery": recovery}
    
    def simulate_lock_timeout(self):
        """Simulate lock timeout during large table alter."""
        
        # Large table (> 1M rows) ALTER TABLE scenario
        lock_scenario = {
            "trigger": "ALTER TABLE on 5M row table during business hours",
            "progression": [
                "Migration starts: ALTER TABLE...",
                "Table locked: All writes blocked",
                "Queue builds: User requests queue",
                "Timeout: Lock wait timeout exceeded",
                "Rollback: Migration rolls back",
                "State: No changes applied, system unresponsive for 5 minutes"
            ],
            "prevention": [
                "Use pt-online-schema-change for large tables",
                "Schedule during maintenance window",
                "Use ALGORITHM=INPLACE if supported",
                "Break into smaller batches"
            ],
            "recovery": [
                "Kill blocking queries",
                "Restart services if needed",
                "Reschedule with proper tool"
            ]
        }
        
        return lock_scenario
    
    def migration_safety_checklist(self):
        """Pre-migration safety checklist."""
        
        return {
            "before_migration": [
                "Full backup verified restorable",
                "Test migration completed on staging",
                "Rollback procedure documented",
                "Maintenance window scheduled",
                "Team on standby",
                "Monitoring dashboards ready"
            ],
            "during_migration": [
                "Execute patches in order",
                "Log each patch execution time",
                "Monitor error logs continuously",
                "Checkpoint after each major step",
                "Abort if error rate > threshold"
            ],
            "after_migration": [
                "Verify schema changes applied",
                "Verify data migrated correctly",
                "Run smoke tests",
                "Monitor error rates for 1 hour",
                "Confirm rollback not needed"
            ]
        }

# Migration safety wrapper
SAFE_MIGRATION_PRACTICES = {
    "transaction_scope": {
        "do": "Wrap each patch in transaction",
        "dont": "Never use auto-commit for patches",
        "why": "Enables rollback on failure"
    },
    "savepoints": {
        "do": "Use savepoints between major steps",
        "dont": "Don't rely on single transaction for long ops",
        "why": "Allows partial rollback"
    },
    "idempotency": {
        "do": "Make all patches idempotent",
        "dont": "Never assume clean state",
        "why": "Safe to re-run if interrupted"
    },
    "batching": {
        "do": "Process data in batches of 1000",
        "dont": "Don't process millions in one transaction",
        "why": "Prevents lock timeout and memory issues"
    }
}
```

---

## 6. Scenario: Permission Misconfiguration

### Security Collapse

```python
# failure_scenarios/permission_failure.py

import frappe

class PermissionFailureSimulator:
    """
    Simulate permission misconfiguration scenarios.
    
    COLLAPSE POINTS:
    - Privilege escalation (users gaining admin access)
    - Data leakage (cross-company visibility)
    - Unauthorized financial transactions
    - Audit trail gaps
    """
    
    def simulate_privilege_escalation(self):
        """Simulate privilege escalation attack."""
        
        attack_vector = {
            "method": "Wildcard (*) permission on critical DocType",
            "entry_point": "Custom script with elevated permissions",
            "exploitation": [
                "User with limited role gets write access",
                "Modifies approval workflow",
                "Creates backdoor admin account",
                "Accesses sensitive financial data"
            ],
            "detection": [
                "Permission audit finds * wildcard",
                "Unexpected admin account creation",
                "User accessing outside business hours",
                "Bulk data exports by non-admin"
            ],
            "prevention": [
                "Regular permission audits",
                "No wildcards on critical DocTypes",
                "Two-person rule for permission changes",
                "Alert on admin account creation"
            ]
        }
        
        return attack_vector
    
    def simulate_cross_company_leakage(self):
        """Simulate cross-company data leakage."""
        
        leakage_scenario = {
            "cause": "Missing company filter in custom report",
            "impact": {
                "company_a_users": "See Company B invoices",
                "financial_data": "Competitor insights exposed",
                "customer_lists": "Shared across companies",
                "pricing": "Cross-company visibility"
            },
            "detection": [
                "User reports seeing wrong company data",
                "Query logs show missing company filters",
                "Unusual cross-company access patterns"
            ],
            "prevention": [
                "Enforce company filter in base query",
                "Multi-company test suite",
                "Data isolation testing",
                "Regular permission audits"
            ]
        }
        
        return leakage_scenario
    
    def permission_audit_checklist(self):
        """Regular permission audit checklist."""
        
        return {
            "weekly": [
                "Review new user role assignments",
                "Check for unexpected permission grants",
                "Verify admin activity logs"
            ],
            "monthly": [
                "Full permission matrix review",
                "Test cross-company isolation",
                "Verify API key rotations",
                "Check for orphaned permissions"
            ],
            "quarterly": [
                "External security audit",
                "Penetration testing",
                "Disaster recovery test",
                "Compliance verification"
            ]
        }

# Permission monitoring alerts
PERMISSION_ALERT_RULES = {
    "privilege_escalation": {
        "trigger": "Role with critical permissions assigned to new user",
        "severity": "HIGH",
        "notification": ["security@company.com", "admin@company.com"]
    },
    "wildcard_permission": {
        "trigger": "DocPerm with permlevel=0 and all rights granted",
        "severity": "CRITICAL",
        "notification": ["security@company.com"]
    },
    "cross_company_access": {
        "trigger": "User accessing data from multiple companies rapidly",
        "severity": "MEDIUM",
        "notification": ["admin@company.com"]
    },
    "bulk_export": {
        "trigger": "Non-admin user exporting > 1000 records",
        "severity": "HIGH",
        "notification": ["security@company.com"]
    }
}
```

---

## Summary: Failure Response Playbook

**When system fails, execute in order:**

1. **STOP** - Don't make it worse, halt deployments
2. **ASSESS** - Identify failure mode using monitoring
3. **ISOLATE** - Contain the failure (disable features if needed)
4. **MITIGATE** - Apply emergency fixes
5. **RECOVER** - Restore service
6. **VERIFY** - Confirm full recovery
7. **DOCUMENT** - Record incident timeline
8. **PREVENT** - Implement permanent fix

**Emergency Contacts:**
- Database issues: DBA team
- Application errors: Dev team lead
- Infrastructure: DevOps/SRE
- Security: Security team
- Business: Project manager
