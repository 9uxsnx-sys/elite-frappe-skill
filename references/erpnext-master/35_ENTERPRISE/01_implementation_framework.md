# Enterprise Implementation System

ERP implementation framework with requirement discovery, gap analysis, phased rollout, and formalized pricing logic engine.

---

## 1. ERP Implementation Framework

### Requirement Discovery Template

```python
# Structured requirement discovery

class RequirementDiscovery:
    """Systematic requirement discovery framework."""
    
    DISCOVERY_DIMENSIONS = {
        "business": {
            "industry": ["Trading", "Retail", "Manufacturing", "Services", "Contracting"],
            "company_size": ["Small (< 50)", "Medium (50-200)", "Large (200-1000)", "Enterprise (> 1000)"],
            "business_model": ["B2B", "B2C", "B2B2C", "D2C"],
            "revenue_range": ["< 10M", "10M-50M", "50M-200M", "> 200M"]
        },
        "operational": {
            "locations": "number_of_branches",
            "warehouse_count": "number",
            "production_facilities": "number",
            "channel_mix": ["Direct", "Distributor", "Retail", "Online"]
        },
        "technical": {
            "current_system": ["Excel", "Legacy ERP", "SAP", "Oracle", "Custom"],
            "integration_needs": ["Bank", "E-commerce", "Government", "Shipping", "CRM"],
            "infrastructure": ["Cloud", "On-premise", "Hybrid"]
        },
        "compliance": {
            "vat_registered": "boolean",
            "vat_phase": ["Phase 1", "Phase 2", "Not Required"],
            "multi_currency": "boolean",
            "audit_requirements": ["Internal", "External", "Statutory"]
        }
    }
    
    MODULE_PRIORITIES = [
        ("Accounting", "core"),
        ("Sales", "core"),
        ("Purchase", "core"),
        ("Stock", "core"),
        ("CRM", "operational"),
        ("Manufacturing", "advanced"),
        ("HR & Payroll", "operational"),
        ("Projects", "advanced"),
        ("Website", "optional"),
        ("Quality", "optional"),
        ("Maintenance", "optional"),
        ("Assets", "optional")
    ]
    
    def conduct_discovery_session(self, client_data):
        """Conduct structured discovery session."""
        
        discovery = {
            "profile": self._profile_client(client_data),
            "modules": self._identify_required_modules(client_data),
            "complexity": self._assess_complexity(client_data),
            "risks": self._identify_implementation_risks(client_data),
            "timeline": self._estimate_timeline(client_data)
        }
        
        return discovery
    
    def _profile_client(self, data):
        """Create client profile from discovery data."""
        
        return {
            "industry_vertical": data.get("industry"),
            "size_category": self._categorize_size(data.get("employee_count")),
            "transaction_volume": self._estimate_volume(data),
            "complexity_score": self._calculate_complexity_score(data),
            "compliance_burden": self._assess_compliance(data),
            "integration_complexity": len(data.get("integrations", []))
        }
    
    def _identify_required_modules(self, data):
        """Identify required ERP modules."""
        
        required = []
        
        # Core always required
        required.extend(["Accounting", "Sales", "Purchase", "Stock"])
        
        # Conditional modules
        if data.get("has_manufacturing"):
            required.append("Manufacturing")
        
        if data.get("employee_count", 0) > 20:
            required.append("HR & Payroll")
        
        if data.get("has_projects"):
            required.append("Projects")
        
        if data.get("ecommerce_enabled"):
            required.append("Website")
        
        if data.get("quality_management"):
            required.append("Quality")
        
        return required
    
    def _calculate_complexity_score(self, data):
        """Calculate implementation complexity (0-100)."""
        
        score = 0
        
        # User count factor (0-20)
        users = data.get("user_count", 10)
        score += min(users / 5, 20)
        
        # Multi-company factor (0-15)
        if data.get("company_count", 1) > 1:
            score += min((data["company_count"] - 1) * 5, 15)
        
        # Integration factor (0-20)
        score += len(data.get("integrations", [])) * 4
        
        # Customization factor (0-20)
        if data.get("custom_workflows"):
            score += 15
        if data.get("custom_reports"):
            score += 5
        
        # Data migration factor (0-15)
        migration_complexity = {
            "Excel": 5,
            "Legacy ERP": 15,
            "SAP": 20,
            "Oracle": 20,
            "Custom": 15,
            "None": 0
        }
        score += migration_complexity.get(data.get("current_system"), 10)
        
        # Compliance factor (0-10)
        if data.get("vat_phase") == "Phase 2":
            score += 10
        elif data.get("vat_phase") == "Phase 1":
            score += 5
        
        return min(score, 100)
    
    def _estimate_timeline(self, data):
        """Estimate implementation timeline in weeks."""
        
        complexity = self._calculate_complexity_score(data)
        modules = len(self._identify_required_modules(data))
        
        # Base timeline
        base_weeks = 8
        
        # Module additions
        module_weeks = modules * 2
        
        # Complexity multiplier
        if complexity > 70:
            complexity_multiplier = 1.5
        elif complexity > 50:
            complexity_multiplier = 1.3
        else:
            complexity_multiplier = 1.0
        
        # Data migration
        migration_weeks = {
            "Excel": 2,
            "Legacy ERP": 6,
            "SAP": 8,
            "Oracle": 8,
            "Custom": 6,
            "None": 0
        }
        
        total = (base_weeks + module_weeks) * complexity_multiplier
        total += migration_weeks.get(data.get("current_system"), 4)
        
        return {
            "minimum_weeks": int(total * 0.8),
            "recommended_weeks": int(total),
            "conservative_weeks": int(total * 1.3),
            "phases": self._define_phases(total, modules)
        }
    
    def _define_phases(self, total_weeks, modules):
        """Define implementation phases."""
        
        return [
            {
                "name": "Discovery & Design",
                "duration_weeks": max(2, int(total_weeks * 0.15)),
                "activities": ["Requirements", "Gap Analysis", "Solution Design"]
            },
            {
                "name": "Foundation Setup",
                "duration_weeks": max(2, int(total_weeks * 0.15)),
                "activities": ["Company Setup", "Chart of Accounts", "Users & Roles"]
            },
            {
                "name": "Core Module Implementation",
                "duration_weeks": int(total_weeks * 0.35),
                "activities": ["Accounting", "Sales", "Purchase", "Stock"]
            },
            {
                "name": "Advanced Modules",
                "duration_weeks": int(total_weeks * 0.20),
                "activities": modules[4:] if len(modules) > 4 else []
            },
            {
                "name": "Data Migration & Testing",
                "duration_weeks": max(2, int(total_weeks * 0.10)),
                "activities": ["Data Migration", "UAT", "Integration Testing"]
            },
            {
                "name": "Go-Live & Support",
                "duration_weeks": max(2, int(total_weeks * 0.05)),
                "activities": ["Go-Live", "Hypercare", "Knowledge Transfer"]
            }
        ]
```

### Gap Analysis Methodology

```python
class GapAnalyzer:
    """Systematic gap analysis for ERP implementation."""
    
    GAP_CATEGORIES = {
        "standard": "Covered by standard ERPNext",
        "configuration": "Requires configuration/customization",
        "customization": "Requires custom development",
        "integration": "Requires third-party integration",
        "process_change": "Requires business process change",
        "out_of_scope": "Not feasible or recommended"
    }
    
    def analyze_gaps(self, requirements, current_state):
        """Analyze gaps between requirements and ERP capabilities."""
        
        gaps = []
        
        for req in requirements:
            gap = self._assess_single_requirement(req, current_state)
            gaps.append(gap)
        
        return {
            "gaps": gaps,
            "summary": self._summarize_gaps(gaps),
            "recommendations": self._generate_recommendations(gaps),
            "effort_estimate": self._estimate_gap_effort(gaps)
        }
    
    def _assess_single_requirement(self, requirement, current_state):
        """Assess single requirement gap."""
        
        # Check if standard ERPNext covers it
        standard_coverage = self._check_standard_coverage(requirement)
        
        if standard_coverage["covered"]:
            return {
                "requirement": requirement,
                "category": "standard",
                "effort_hours": standard_coverage["config_hours"],
                "approach": "Standard functionality"
            }
        
        # Check if configuration/customization needed
        if standard_coverage["configurable"]:
            return {
                "requirement": requirement,
                "category": "configuration",
                "effort_hours": standard_coverage["config_hours"] + 8,
                "approach": f"Configuration: {standard_coverage['approach']}"
            }
        
        # Check if custom development needed
        if standard_coverage["customizable"]:
            complexity = requirement.get("complexity", "medium")
            effort = {"simple": 16, "medium": 40, "complex": 80}[complexity]
            
            return {
                "requirement": requirement,
                "category": "customization",
                "effort_hours": effort,
                "approach": f"Custom {requirement.get('type', 'DocType')}"
            }
        
        # Integration required
        if requirement.get("requires_integration"):
            return {
                "requirement": requirement,
                "category": "integration",
                "effort_hours": 40,
                "approach": f"Integration with {requirement['integration_target']}"
            }
        
        return {
            "requirement": requirement,
            "category": "out_of_scope",
            "effort_hours": 0,
            "approach": "Out of scope - recommend alternative"
        }
    
    def _summarize_gaps(self, gaps):
        """Summarize gap analysis."""
        
        summary = {cat: [] for cat in self.GAP_CATEGORIES.keys()}
        
        for gap in gaps:
            summary[gap["category"]].append(gap)
        
        return {
            "by_category": {k: len(v) for k, v in summary.items()},
            "total_gaps": len(gaps),
            "total_customization_hours": sum(
                g["effort_hours"] for g in gaps if g["category"] == "customization"
            ),
            "total_integration_hours": sum(
                g["effort_hours"] for g in gaps if g["category"] == "integration"
            ),
            "out_of_scope_count": len(summary["out_of_scope"])
        }
    
    def _estimate_gap_effort(self, gaps):
        """Estimate total effort for gap closure."""
        
        total_hours = sum(g["effort_hours"] for g in gaps)
        
        # Add buffer
        buffer_factor = 1.3
        
        return {
            "development_hours": total_hours,
            "with_buffer": int(total_hours * buffer_factor),
            "in_days": int((total_hours * buffer_factor) / 8),
            "in_weeks": int((total_hours * buffer_factor) / 40)
        }
```

---

## 2. Module Prioritization Logic

```python
class ModulePrioritizer:
    """Prioritize module implementation sequence."""
    
    DEPENDENCY_GRAPH = {
        "Accounting": [],
        "Sales": ["Accounting", "Stock"],
        "Purchase": ["Accounting", "Stock"],
        "Stock": [],
        "Manufacturing": ["Stock", "Purchase"],
        "CRM": ["Sales"],
        "HR & Payroll": ["Accounting"],
        "Projects": ["Accounting", "Sales"],
        "Assets": ["Accounting"],
        "Quality": ["Stock", "Purchase"]
    }
    
    def prioritize_modules(self, required_modules, constraints=None):
        """Generate prioritized module implementation sequence."""
        
        # Build dependency tree
        sequence = self._topological_sort(required_modules)
        
        # Apply constraints
        if constraints:
            sequence = self._apply_constraints(sequence, constraints)
        
        # Group into phases
        phases = self._group_into_phases(sequence)
        
        return {
            "sequence": sequence,
            "phases": phases,
            "duration_estimate": self._estimate_sequence_duration(sequence),
            "critical_path": self._identify_critical_path(sequence)
        }
    
    def _topological_sort(self, modules):
        """Sort modules by dependency."""
        
        # Kahn's algorithm
        in_degree = {m: 0 for m in modules}
        adj = {m: [] for m in modules}
        
        for module in modules:
            deps = self.DEPENDENCY_GRAPH.get(module, [])
            for dep in deps:
                if dep in modules:
                    adj[dep].append(module)
                    in_degree[module] += 1
        
        # Start with modules having no dependencies
        queue = [m for m in modules if in_degree[m] == 0]
        result = []
        
        while queue:
            module = queue.pop(0)
            result.append(module)
            
            for neighbor in adj[module]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return result
    
    def _group_into_phases(self, sequence):
        """Group modules into implementation phases."""
        
        phases = {
            "foundation": [],
            "core": [],
            "operational": [],
            "advanced": []
        }
        
        core_modules = ["Accounting", "Sales", "Purchase", "Stock"]
        
        for module in sequence:
            if module in core_modules:
                if module == "Accounting":
                    phases["foundation"].append(module)
                else:
                    phases["core"].append(module)
            elif module in ["CRM", "HR & Payroll", "Projects"]:
                phases["operational"].append(module)
            else:
                phases["advanced"].append(module)
        
        return phases
    
    def _estimate_sequence_duration(self, sequence):
        """Estimate duration for module sequence."""
        
        module_duration = {
            "Accounting": 2,
            "Sales": 2,
            "Purchase": 1.5,
            "Stock": 2,
            "CRM": 1,
            "Manufacturing": 3,
            "HR & Payroll": 2,
            "Projects": 1.5,
            "Assets": 1,
            "Quality": 1,
            "Website": 1.5
        }
        
        total_weeks = sum(module_duration.get(m, 2) for m in sequence)
        
        # Add 20% for overlaps and dependencies
        return int(total_weeks * 0.8)
```

---

## 3. Estimation & Pricing Logic Engine

### DocType Complexity Scoring

```python
class DocTypeComplexityScorer:
    """Score DocType implementation complexity."""
    
    COMPLEXITY_FACTORS = {
        "field_count": {
            "weight": 0.2,
            "thresholds": [(10, 1), (30, 3), (50, 5), (100, 10)]
        },
        "child_table_count": {
            "weight": 0.25,
            "thresholds": [(0, 0), (1, 2), (3, 5), (5, 8)]
        },
        "workflow_complexity": {
            "weight": 0.2,
            "thresholds": [(0, 0), (3, 2), (5, 5), (8, 10)]
        },
        "integration_points": {
            "weight": 0.2,
            "thresholds": [(0, 0), (1, 3), (3, 7), (5, 12)]
        },
        "calculation_complexity": {
            "weight": 0.15,
            "thresholds": [("simple", 1), ("medium", 3), ("complex", 8), ("algorithmic", 15)]
        }
    }
    
    def score(self, requirements):
        """Calculate complexity score (0-100)."""
        
        score = 0
        breakdown = {}
        
        for factor, config in self.COMPLEXITY_FACTORS.items():
            value = requirements.get(factor, 0)
            
            # Find threshold
            points = 0
            for threshold, point in config["thresholds"]:
                if value >= threshold:
                    points = point
            
            weighted = points * config["weight"]
            score += weighted
            breakdown[factor] = {"raw": points, "weighted": weighted}
        
        return {
            "total": min(score, 100),
            "breakdown": breakdown,
            "category": self._categorize(score),
            "estimated_hours": self._hours_from_score(score)
        }
    
    def _categorize(self, score):
        """Categorize complexity."""
        if score < 20:
            return "Simple"
        elif score < 40:
            return "Medium"
        elif score < 60:
            return "Complex"
        elif score < 80:
            return "Very Complex"
        else:
            return "Enterprise"
    
    def _hours_from_score(self, score):
        """Estimate hours from score."""
        return int(score * 2)  # 2 hours per point
```

### Workflow Complexity Scoring

```python
class WorkflowComplexityScorer:
    """Score workflow implementation complexity."""
    
    def score_workflow(self, workflow_definition):
        """Score workflow complexity."""
        
        states = len(workflow_definition.get("states", []))
        transitions = len(workflow_definition.get("transitions", []))
        conditions = sum(1 for t in workflow_definition.get("transitions", []) if t.get("condition"))
        actions = sum(len(t.get("actions", [])) for t in workflow_definition.get("transitions", []))
        
        score = (
            states * 2 +
            transitions * 1.5 +
            conditions * 3 +
            actions * 2
        )
        
        return {
            "total": min(score, 50),
            "states": states,
            "transitions": transitions,
            "conditions": conditions,
            "actions": actions,
            "estimated_hours": int(score * 1.5),
            "category": "Simple" if score < 15 else "Medium" if score < 30 else "Complex"
        }
```

### Integration Cost Matrix

```python
INTEGRATION_COST_MATRIX = {
    "Bank Feed": {
        "complexity": "Medium",
        "base_hours": 40,
        "variations": {
            "Standard API": 40,
            "Custom API": 60,
            "File-based": 30,
            "SWIFT": 80
        }
    },
    "Payment Gateway": {
        "complexity": "Medium",
        "base_hours": 24,
        "variations": {
            "Stripe": 24,
            "PayPal": 24,
            "Custom": 40,
            "Regional": 32
        }
    },
    "E-commerce Platform": {
        "complexity": "High",
        "base_hours": 80,
        "variations": {
            "Shopify": 80,
            "WooCommerce": 72,
            "Magento": 120,
            "Custom": 160
        }
    },
    "Shipping Provider": {
        "complexity": "Low",
        "base_hours": 16,
        "variations": {
            "Standard API": 16,
            "Multi-provider": 40
        }
    },
    "Government Portal": {
        "complexity": "High",
        "base_hours": 120,
        "variations": {
            "ZATCA Phase 1": 80,
            "ZATCA Phase 2": 160,
            "GOSI": 120,
            "MUDAD": 80,
            "Custom": 200
        }
    },
    "CRM Integration": {
        "complexity": "Medium",
        "base_hours": 40,
        "variations": {
            "Salesforce": 56,
            "HubSpot": 40,
            "Zoho": 32,
            "Custom": 80
        }
    },
    "Business Intelligence": {
        "complexity": "Medium",
        "base_hours": 48,
        "variations": {
            "Power BI": 48,
            "Tableau": 56,
            "Custom Dashboard": 64
        }
    }
}

def estimate_integration(integration_type, variation="Standard", custom_requirements=None):
    """Estimate integration cost."""
    
    matrix = INTEGRATION_COST_MATRIX.get(integration_type)
    if not matrix:
        return {"error": f"Unknown integration type: {integration_type}"}
    
    base_hours = matrix["variations"].get(variation, matrix["base_hours"])
    
    # Add custom requirements
    if custom_requirements:
        base_hours += custom_requirements.get("additional_hours", 0)
    
    # Calculate cost (assuming $100/hour)
    cost = base_hours * 100
    
    return {
        "integration": integration_type,
        "variation": variation,
        "complexity": matrix["complexity"],
        "estimated_hours": base_hours,
        "estimated_cost_usd": cost,
        "timeline_weeks": max(1, int(base_hours / 40)),
        "risk_factors": [
            "API documentation quality",
            "Authentication complexity",
            "Data mapping complexity",
            "Error handling requirements"
        ]
    }
```

### Maintenance Load Calculation

```python
def calculate_maintenance_load(implementation_specs):
    """Calculate ongoing maintenance load."""
    
    # Base maintenance (standard ERP)
    base_hours_per_month = 8
    
    # Additional for customizations
    custom_doctypes = implementation_specs.get("custom_doctypes", 0)
    custom_workflows = implementation_specs.get("custom_workflows", 0)
    integrations = len(implementation_specs.get("integrations", []))
    
    customization_hours = (
        custom_doctypes * 2 +  # 2 hours per custom DocType
        custom_workflows * 1 +   # 1 hour per workflow
        integrations * 4         # 4 hours per integration
    )
    
    # User support load
    user_count = implementation_specs.get("user_count", 10)
    support_hours = user_count * 0.5  # 0.5 hours per user per month
    
    total_monthly = base_hours_per_month + customization_hours + support_hours
    
    return {
        "base_maintenance": base_hours_per_month,
        "customization_maintenance": customization_hours,
        "user_support": support_hours,
        "total_monthly_hours": total_monthly,
        "recommended_support_tier": "Standard" if total_monthly < 20 else "Premium" if total_monthly < 50 else "Enterprise",
        "annual_estimate_hours": total_monthly * 12
    }
```

### Hosting Cost Estimation

```python
def estimate_hosting_cost(requirements):
    """Estimate hosting infrastructure costs."""
    
    users = requirements.get("user_count", 10)
    companies = requirements.get("company_count", 1)
    transaction_volume = requirements.get("monthly_transactions", 1000)
    storage_gb = requirements.get("storage_gb", 10)
    
    # Calculate resources
    concurrent_users = users * 0.2  # 20% concurrent
    
    # Server sizing
    if concurrent_users < 10:
        server_tier = "Small"
        vcpu = 2
        ram_gb = 4
        cost_per_month = 50
    elif concurrent_users < 50:
        server_tier = "Medium"
        vcpu = 4
        ram_gb = 8
        cost_per_month = 100
    elif concurrent_users < 150:
        server_tier = "Large"
        vcpu = 8
        ram_gb = 16
        cost_per_month = 200
    else:
        server_tier = "Enterprise"
        vcpu = 16
        ram_gb = 32
        cost_per_month = 400
    
    # Storage
    storage_cost = storage_gb * 0.10  # $0.10 per GB
    
    # Backup (20% of storage)
    backup_cost = storage_gb * 0.20 * 0.10
    
    # Database (RDS equivalent)
    db_cost = cost_per_month * 0.3
    
    total = cost_per_month + storage_cost + backup_cost + db_cost
    
    return {
        "server_tier": server_tier,
        "vcpu": vcpu,
        "ram_gb": ram_gb,
        "server_cost": cost_per_month,
        "storage_gb": storage_gb,
        "storage_cost": storage_cost,
        "backup_cost": backup_cost,
        "database_cost": db_cost,
        "total_monthly": round(total, 2),
        "total_annual": round(total * 12, 2),
        "cost_per_user": round(total / users, 2)
    }
```

---

## Summary: Implementation Planning Checklist

**Pre-implementation:**

- [ ] Requirement discovery completed
- [ ] Gap analysis finalized
- [ ] Modules prioritized
- [ ] Phased rollout plan approved
- [ ] Data migration strategy defined
- [ ] Integration architecture designed
- [ ] User training plan created
- [ ] Change management plan approved
- [ ] Go-live risk matrix documented
- [ ] Pricing and contracts signed

**During implementation:**

- [ ] Weekly status reports
- [ ] Phase gates passed
- [ ] UAT completed per phase
- [ ] Documentation updated
- [ ] Training delivered
- [ ] Data migrated and validated
- [ ] Integrations tested

**Post-implementation:**

- [ ] Hypercare period completed
- [ ] Knowledge transfer finished
- [ ] Support handover done
- [ ] Performance baseline established
- [ ] Success metrics reviewed
