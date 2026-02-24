# System Constraint Map

Data volume limits, worker capacity assumptions, security threat model, and explicit tradeoffs for Frappe/ERPNext enterprise systems.

---

## 1. Data Volume Limits

### Hard Limits

```python
# System data volume constraints

DATA_VOLUME_LIMITS = {
    "per_doctype": {
        "reasonable": {
            "records": 100000,
            "performance_impact": "None with proper indexing",
            "maintenance": "Standard"
        },
        "large": {
            "records": 500000,
            "performance_impact": "Query optimization required",
            "maintenance": "Background jobs for bulk ops"
        },
        "enterprise": {
            "records": 2000000,
            "performance_impact": "Partitioning/archiving required",
            "maintenance": "Dedicated DBA, read replicas"
        },
        "maximum": {
            "records": 10000000,
            "performance_impact": "Custom architecture required",
            "maintenance": "Sharded database, data warehouse"
        }
    },
    "per_field": {
        "data": {"max_length": 65535, "storage": "TEXT"},
        "text_editor": {"max_length": 16777215, "storage": "LONGTEXT"},
        "code": {"max_length": 16777215, "storage": "LONGTEXT"},
        "attach": {"max_size_mb": 100, "recommended_max": 10}
    },
    "per_child_table": {
        "max_rows_recommended": 1000,
        "max_rows_hard": 10000,
        "performance_note": ">1000 rows causes form slowdown"
    },
    "attachments": {
        "per_site_max_gb": 500,
        "warning_threshold_gb": 400,
        "single_file_max_mb": 100,
        "storage_recommendation": "External S3/MinIO for >100GB"
    }
}

def assess_data_volume_risk(doctype, projected_records):
    """Assess risk level for projected data volume."""
    
    limits = DATA_VOLUME_LIMITS["per_doctype"]
    
    if projected_records <= limits["reasonable"]["records"]:
        return {
            "level": "LOW",
            "action": "Standard development",
            "indexing_required": True,
            "archival_required": False
        }
    elif projected_records <= limits["large"]["records"]:
        return {
            "level": "MEDIUM",
            "action": "Add performance optimization",
            "indexing_required": True,
            "archival_required": False,
            "background_jobs_required": True
        }
    elif projected_records <= limits["enterprise"]["records"]:
        return {
            "level": "HIGH",
            "action": "Architecture review required",
            "indexing_required": True,
            "archival_required": True,
            "partitioning_required": True,
            "read_replicas_recommended": True
        }
    else:
        return {
            "level": "CRITICAL",
            "action": "Custom architecture mandatory",
            "indexing_required": True,
            "archival_required": True,
            "partitioning_required": True,
            "sharding_required": True,
            "data_warehouse_required": True
        }
```

### Volume Thresholds by DocType

| DocType | Warning Level | Critical Level | Action Required |
|---------|---------------|----------------|-----------------|
| Sales Invoice | 500k | 2M | Archive closed invoices |
| GL Entry | 2M | 10M | Partition by fiscal year |
| Stock Ledger | 1M | 5M | FIFO valuation optimization |
| Email Queue | 100k | 500k | Aggressive cleanup |
| Error Log | 50k | 200k | Automated archiving |
| Activity Log | 500k | 2M | Reduce retention |
| Version | 1M | 5M | Cleanup old versions |
| Communication | 500k | 2M | Archive to cold storage |

---

## 2. Worker Capacity Assumptions

### Gunicorn Worker Limits

```python
WORKER_CAPACITY_MODEL = {
    "gunicorn": {
        "per_worker": {
            "concurrent_requests": 1,  # Synchronous
            "memory_mb": 256,
            "requests_per_minute": 120,
            "cpu_percent": 10
        },
        "scaling_limits": {
            "min_workers": 4,
            "max_workers_by_cpu": "(2 * CPU_CORES) + 1",
            "max_workers_by_memory": "TOTAL_MEMORY_GB * 0.6 / 0.256",
            "optimal": "min(cpu_based, memory_based)"
        },
        "bottlenecks": [
            "Database connection pool",
            "Redis connection pool", 
            "File descriptor limits",
            "Memory pressure"
        ]
    },
    "background_workers": {
        "per_worker": {
            "jobs_per_minute": 30,
            "memory_mb": 512,
            "timeout_default": 300,
            "timeout_long": 3600
        },
        "queue_limits": {
            "default_max": 10000,  # Jobs in queue
            "warning_threshold": 5000,
            "critical_threshold": 9000
        }
    },
    "scheduler": {
        "max_scheduled_jobs": 100,
        "min_interval_seconds": 60,
        "concurrent_execution_limit": 1
    }
}

def calculate_worker_limits(hardware_specs):
    """Calculate optimal worker configuration."""
    
    cpu_cores = hardware_specs["cpu_cores"]
    memory_gb = hardware_specs["memory_gb"]
    
    # CPU-based limit
    cpu_based = (2 * cpu_cores) + 1
    
    # Memory-based limit (60% of RAM for workers, 256MB each)
    memory_based = int((memory_gb * 0.6) / 0.256)
    
    # Optimal is the lower of the two
    optimal = min(cpu_based, memory_based)
    
    return {
        "gunicorn_workers": max(4, optimal),
        "background_workers": {
            "default": max(2, int(optimal * 0.3)),
            "long": max(1, int(optimal * 0.2)),
            "short": max(1, int(optimal * 0.1))
        },
        "max_database_connections": min(int(optimal * 2.5), 500),
        "constraints": {
            "cpu_limited": cpu_based < memory_based,
            "memory_limited": memory_based < cpu_based
        }
    }
```

### Concurrent User Capacity

| Configuration | Supported Concurrent Users | Peak Requests/Min |
|---------------|---------------------------|-------------------|
| Small (2 CPU, 4GB RAM) | 20-30 | 240 |
| Medium (4 CPU, 8GB RAM) | 50-80 | 600 |
| Large (8 CPU, 16GB RAM) | 150-200 | 1500 |
| Enterprise (16 CPU, 32GB RAM) | 400-500 | 3600 |
| Cluster (4x Large) | 1000+ | 6000+ |

---

## 3. Network Assumptions

### Bandwidth Requirements

```python
NETWORK_REQUIREMENTS = {
    "bandwidth": {
        "per_concurrent_user": {
            "average_kbps": 50,
            "peak_kbps": 200,
            "form_load_kb": 500,
            "report_load_kb": 2000
        },
        "total_estimation": {
            "formula": "concurrent_users * 0.2 * 50",
            "unit": "kbps",
            "recommendation": "1.5x headroom for peaks"
        }
    },
    "latency": {
        "acceptable": {
            "api_response_ms": 500,
            "form_load_ms": 1500,
            "report_generation_ms": 5000
        },
        "degraded": {
            "api_response_ms": 1000,
            "form_load_ms": 3000,
            "report_generation_ms": 10000
        },
        "unacceptable": {
            "api_response_ms": 3000,
            "form_load_ms": 5000,
            "report_generation_ms": 30000
        }
    },
    "connection_limits": {
        "database_pool_max": 500,
        "redis_pool_max": 1000,
        "http_keepalive_seconds": 5,
        "tcp_backlog": 511
    }
}
```

---

## 4. Deployment Constraints

### Infrastructure Limits

```python
DEPLOYMENT_CONSTRAINTS = {
    "single_server": {
        "max_concurrent_users": 200,
        "max_data_volume_gb": 500,
        "max_request_rate_per_minute": 2000,
        "scaling": "Vertical only",
        "reliability": "Single point of failure",
        "use_case": "Small business, < 50 users"
    },
    "application_cluster": {
        "max_concurrent_users": 1000,
        "max_data_volume_gb": 2000,
        "max_request_rate_per_minute": 10000,
        "scaling": "Horizontal app servers",
        "reliability": "High (with DB redundancy)",
        "use_case": "Mid-market, 50-500 users"
    },
    "enterprise_cluster": {
        "max_concurrent_users": 5000,
        "max_data_volume_gb": 10000,
        "max_request_rate_per_minute": 50000,
        "scaling": "Full horizontal",
        "reliability": "Very High",
        "use_case": "Enterprise, 500+ users"
    },
    "saas_multi_tenant": {
        "max_tenants": 1000,
        "max_users_per_tenant": 100,
        "isolation": "Database-level",
        "scaling": "Tenant sharding",
        "use_case": "ERP SaaS provider"
    }
}
```

---

## 5. Security Threat Model

### Threat Assessment Matrix

```python
SECURITY_THREAT_MODEL = {
    "threats": {
        "data_exfiltration": {
            "likelihood": "Medium",
            "impact": "High",
            "mitigations": [
                "Field-level permissions",
                "API rate limiting",
                "Audit logging",
                "Data encryption at rest"
            ],
            "monitoring": [
                "Unusual query volumes",
                "Bulk export detection",
                "Off-hours access"
            ]
        },
        "privilege_escalation": {
            "likelihood": "Low",
            "impact": "Critical",
            "mitigations": [
                "Role-based access control",
                "Regular permission audits",
                "Principle of least privilege",
                "Multi-factor authentication"
            ],
            "monitoring": [
                "Permission changes",
                "Role assignments",
                "Admin activity"
            ]
        },
        "injection_attacks": {
            "likelihood": "Low",
            "impact": "Critical",
            "mitigations": [
                "Parameterized queries",
                "Input validation",
                "ORM usage",
                "WAF rules"
            ],
            "monitoring": [
                "SQL injection patterns",
                "Error log analysis",
                "Request anomalies"
            ]
        },
        "dos_attacks": {
            "likelihood": "Medium",
            "impact": "Medium",
            "mitigations": [
                "Rate limiting",
                "Request throttling",
                "CDN integration",
                "Auto-scaling"
            ],
            "monitoring": [
                "Request rate spikes",
                "Resource exhaustion",
                "Error rate increases"
            ]
        }
    },
    "compliance_requirements": {
        "gdpr": {
            "data_residency": "EU required",
            "right_to_deletion": True,
            "consent_tracking": True,
            "audit_retention_years": 7
        },
        "sox": {
            "financial_data_integrity": True,
            "audit_trail": True,
            "access_controls": True,
            "change_management": True
        },
        "pci_dss": {
            "card_data_encryption": True,
            "network_segmentation": True,
            "regular_scanning": True,
            "access_logging": True
        }
    }
}
```

---

## 6. ERP Complexity Boundaries

### Complexity Limits

```python
COMPLEXITY_BOUNDARIES = {
    "workflows": {
        "max_states": 10,
        "max_transitions": 30,
        "max_conditions_per_transition": 5,
        "performance_impact": "Form load time increases 500ms per 5 states"
    },
    "custom_fields": {
        "per_doctype_max": 100,
        "recommended_max": 50,
        "performance_impact": "1-2ms per 10 fields on save"
    },
    "custom_scripts": {
        "client_script_max_lines": 200,
        "server_script_max_lines": 500,
        "complexity_warning": "Refactor if > 100 lines"
    },
    "integrations": {
        "max_active_webhooks": 20,
        "max_api_calls_per_minute": 1000,
        "max_scheduled_syncs": 50,
        "performance_impact": "Each webhook adds 50-100ms latency"
    },
    "reports": {
        "max_execution_time_seconds": 60,
        "max_rows_returned": 10000,
        "max_joins": 5,
        "performance_impact": "Exponential with each join"
    }
}

def validate_complexity(doctype_config, workflow_config, integration_config):
    """Validate system complexity is within boundaries."""
    
    violations = []
    
    # Check custom fields
    if len(doctype_config.get("custom_fields", [])) > COMPLEXITY_BOUNDARIES["custom_fields"]["per_doctype_max"]:
        violations.append({
            "type": "custom_fields",
            "severity": "HIGH",
            "message": f"Custom fields exceed maximum ({COMPLEXITY_BOUNDARIES['custom_fields']['per_doctype_max']})"
        })
    
    # Check workflow complexity
    workflow = workflow_config
    if len(workflow.get("states", [])) > COMPLEXITY_BOUNDARIES["workflows"]["max_states"]:
        violations.append({
            "type": "workflow_states",
            "severity": "MEDIUM",
            "message": f"Workflow states exceed recommended maximum"
        })
    
    # Check integrations
    if len(integration_config.get("webhooks", [])) > COMPLEXITY_BOUNDARIES["integrations"]["max_active_webhooks"]:
        violations.append({
            "type": "webhooks",
            "severity": "MEDIUM",
            "message": f"Active webhooks exceed recommended maximum"
        })
    
    return {
        "valid": len(violations) == 0,
        "violations": violations,
        "recommendations": [
            "Consider breaking complex DocTypes into separate entities",
            "Simplify workflows - use sub-workflows for complex processes",
            "Batch API calls to reduce integration overhead"
        ]
    }
```

---

## 7. Tradeoff Decision Matrix

### Explicit Tradeoffs

```python
TRADEOFF_DECISIONS = {
    "performance_vs_cost": {
        "description": "Faster queries vs infrastructure cost",
        "options": {
            "optimize_queries": {
                "cost": "Development time",
                "performance_gain": "High",
                "scalability": "Good",
                "recommendation": "Always first choice"
            },
            "add_caching": {
                "cost": "Redis infrastructure",
                "performance_gain": "Medium",
                "scalability": "Good",
                "recommendation": "For read-heavy workloads"
            },
            "scale_vertically": {
                "cost": "Higher server cost",
                "performance_gain": "Linear",
                "scalability": "Limited (hardware ceiling)",
                "recommendation": "Short-term fix only"
            },
            "scale_horizontally": {
                "cost": "Complex infrastructure",
                "performance_gain": "High",
                "scalability": "Excellent",
                "recommendation": "Long-term solution"
            }
        }
    },
    "consistency_vs_availability": {
        "description": "Data consistency vs system availability",
        "options": {
            "strict_consistency": {
                "availability": "Reduced during conflicts",
                "consistency": "Strong",
                "use_case": "Financial transactions"
            },
            "eventual_consistency": {
                "availability": "High",
                "consistency": "Eventual",
                "use_case": "Reports, analytics"
            }
        }
    },
    "customization_vs_upgradeability": {
        "description": "Custom features vs ease of upgrades",
        "options": {
            "hooks_only": {
                "customization": "Limited",
                "upgradeability": "Excellent",
                "maintenance": "Low",
                "recommendation": "Preferred for all customizations"
            },
            "override_classes": {
                "customization": "High",
                "upgradeability": "Moderate (review needed)",
                "maintenance": "Medium",
                "recommendation": "When hooks insufficient"
            },
            "core_modification": {
                "customization": "Unlimited",
                "upgradeability": "Poor",
                "maintenance": "High",
                "recommendation": "NEVER - fork instead"
            }
        }
    },
    "real_time_vs_batch": {
        "description": "Real-time processing vs batch processing",
        "options": {
            "real_time": {
                "latency": "Low",
                "throughput": "Limited",
                "resource_usage": "High",
                "use_case": "User-facing operations"
            },
            "batch": {
                "latency": "High",
                "throughput": "Very High",
                "resource_usage": "Controlled",
                "use_case": "Reports, data processing"
            },
            "hybrid": {
                "latency": "Medium",
                "throughput": "High",
                "resource_usage": "Medium",
                "use_case": "Complex workflows"
            }
        }
    }
}

def make_tradeoff_decision(tradeoff_type, requirements):
    """Recommend tradeoff decision based on requirements."""
    
    tradeoff = TRADEOFF_DECISIONS.get(tradeoff_type)
    
    if not tradeoff:
        return {"error": f"Unknown tradeoff type: {tradeoff_type}"}
    
    # Score each option based on requirements
    scores = {}
    
    for option_name, option in tradeoff["options"].items():
        score = 0
        
        for req, weight in requirements.items():
            if req in option:
                score += weight * option[req]
        
        scores[option_name] = score
    
    # Return best option
    best = max(scores, key=scores.get)
    
    return {
        "recommended": best,
        "scores": scores,
        "rationale": tradeoff["options"][best],
        "alternatives": [k for k in scores if k != best]
    }
```

---

## Summary: Constraint Checklist

**Before accepting project scope:**

- [ ] Data volume within supported limits
- [ ] Concurrent user count within capacity
- [ ] Integration count within limits
- [ ] Workflow complexity manageable
- [ ] Custom field count reasonable
- [ ] Network bandwidth sufficient
- [ ] Security requirements met
- [ ] Compliance requirements understood
- [ ] Tradeoffs explicitly accepted
- [ ] Scaling path defined
