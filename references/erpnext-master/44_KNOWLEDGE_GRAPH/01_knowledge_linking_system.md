# Knowledge Linking System

Cross-reference graph connecting DocTypes to lifecycles, hooks to performance, scaling to architecture, and failure scenarios into a navigable knowledge network.

---

## 1. Knowledge Graph Architecture

### Graph Structure

```
KNOWLEDGE_GRAPH = {
    "nodes": {
        # DocTypes (Core Entities)
        "Sales Order": {
            "type": "doctype",
            "category": "transactional",
            "fields": 45,
            "submittable": True,
            "linked_doctypes": ["Customer", "Item", "Company"]
        },
        "Customer": {
            "type": "doctype",
            "category": "master",
            "fields": 35,
            "submittable": False,
            "linked_doctypes": ["Territory", "Customer Group"]
        },
        "Item": {
            "type": "doctype",
            "category": "master",
            "fields": 60,
            "submittable": False,
            "linked_doctypes": ["Item Group", "Brand", "UOM"]
        },
        
        # Lifecycle Hooks
        "validate": {
            "type": "lifecycle_hook",
            "trigger": "before_save",
            "use_for": ["validation", "calculation", "enrichment"],
            "performance_impact": "Sync - keep < 500ms"
        },
        "on_submit": {
            "type": "lifecycle_hook",
            "trigger": "after_submit",
            "use_for": ["side_effects", "notifications", "integrations"],
            "performance_impact": "Can enqueue async tasks"
        },
        "on_cancel": {
            "type": "lifecycle_hook",
            "trigger": "after_cancel",
            "use_for": ["cleanup", "reversals", "audit"],
            "performance_impact": "Must handle reversals correctly"
        },
        
        # Architecture Patterns
        "service_layer": {
            "type": "pattern",
            "complexity": "medium",
            "use_when": ["complex_validation", "multi_doctype_logic"],
            "benefits": ["testability", "separation", "reusability"]
        },
        "event_driven": {
            "type": "pattern",
            "complexity": "high",
            "use_when": ["audit_requirements", "loose_coupling", "replay_needed"],
            "benefits": ["traceability", "scalability", "flexibility"]
        },
        "cqrs": {
            "type": "pattern",
            "complexity": "high",
            "use_when": ["read_write_asymmetry", "complex_reporting"],
            "benefits": ["performance", "scalability"]
        },
        
        # Performance Topics
        "indexing": {
            "type": "performance",
            "category": "database",
            "impact": "High for >50k records",
            "tradeoffs": ["Write slowdown", "Storage overhead"]
        },
        "caching": {
            "type": "performance",
            "category": "application",
            "impact": "High for read-heavy",
            "tradeoffs": ["Stale data", "Invalidation complexity"]
        },
        "background_jobs": {
            "type": "performance",
            "category": "async",
            "impact": "Essential for >500ms operations",
            "tradeoffs": ["Eventual consistency", "Queue management"]
        },
        
        # Scaling Strategies
        "vertical_scaling": {
            "type": "scaling",
            "limit": "Hardware ceiling",
            "cost_model": "Linear",
            "use_case": "Short-term, < 200 users"
        },
        "horizontal_scaling": {
            "type": "scaling",
            "limit": "Database bottleneck",
            "cost_model": "Sub-linear with efficiency",
            "use_case": "Long-term, > 200 users"
        },
        "database_sharding": {
            "type": "scaling",
            "limit": "Complexity",
            "cost_model": "High",
            "use_case": "Multi-tenant SaaS, > 10M records"
        },
        
        # Architecture Blueprints
        "multi_company": {
            "type": "blueprint",
            "components": ["Company isolation", "Consolidated reporting"],
            "complexity": "Medium",
            "performance_considerations": ["Query scoping", "Permission filtering"]
        },
        "manufacturing": {
            "type": "blueprint",
            "components": ["BOM", "Work Order", "Job Card", "Quality"],
            "complexity": "High",
            "performance_considerations": ["Cost rollup", "Capacity planning"]
        },
        
        # Failure Scenarios
        "volume_failure": {
            "type": "failure",
            "trigger": "500k+ records",
            "symptoms": ["Slow queries", "Connection exhaustion", "Timeouts"],
            "prevention": ["Indexing", "Partitioning", "Archiving"]
        },
        "concurrency_failure": {
            "type": "failure",
            "trigger": "5k+ concurrent users",
            "symptoms": ["Worker saturation", "Memory exhaustion", "DB locks"],
            "prevention": ["Worker scaling", "Connection pooling", "Caching"]
        },
        "redis_failure": {
            "type": "failure",
            "trigger": "Cache/store outage",
            "symptoms": ["Session loss", "Queue loss", "Stampede"],
            "prevention": ["Persistence", "HA setup", "Graceful degradation"]
        }
    },
    
    "edges": {
        # DocType -> Lifecycle
        "Sales Order": {
            "uses_lifecycle": ["validate", "on_submit", "on_cancel"],
            "has_hooks": ["before_insert", "after_insert", "on_update"],
            "performance_sensitivity": "High"
        },
        "Customer": {
            "uses_lifecycle": ["validate"],
            "has_hooks": ["on_update"],
            "performance_sensitivity": "Medium"
        },
        
        # Lifecycle -> Performance
        "validate": {
            "requires_performance": ["Sync execution", "< 500ms", "No external calls"],
            "optimization_strategies": ["Query optimization", "Caching", "Lazy loading"]
        },
        "on_submit": {
            "requires_performance": ["Enqueue async", "Progress tracking", "Error handling"],
            "optimization_strategies": ["Batch processing", "Queue segmentation"]
        },
        
        # Performance -> Scaling
        "indexing": {
            "enables_scaling": ["Query performance", "User capacity"],
            "limitation": "Can't index away design flaws"
        },
        "background_jobs": {
            "enables_scaling": ["User experience", "Throughput"],
            "tradeoff": "Eventual consistency"
        },
        
        # Scaling -> Architecture
        "horizontal_scaling": {
            "requires_architecture": ["Stateless design", "Shared cache", "Session externalization"],
            "enables_blueprint": ["enterprise_deployment", "saas_multi_tenant"]
        },
        "database_sharding": {
            "requires_architecture": ["Shard key design", "Cross-shard queries minimized"],
            "enables_blueprint": ["massive_scale_saas"]
        },
        
        # Architecture -> Failure Prevention
        "multi_company": {
            "prevents_failure": ["data_leakage", "cross_tenant_access"],
            "requires_vigilance": ["Query scoping", "Permission enforcement"]
        },
        "manufacturing": {
            "risk_areas": ["cost_rollup_performance", "bom_explosion_depth"],
            "mitigation": ["Caching", "Background processing"]
        },
        
        # Failure -> Architecture Response
        "volume_failure": {
            "solved_by": ["partitioning", "archiving", "read_replicas"],
            "prevention_architecture": ["data_warehouse", "etl_pipeline"]
        },
        "concurrency_failure": {
            "solved_by": ["horizontal_scaling", "load_balancing", "caching"],
            "prevention_architecture": ["cluster_deployment", "cdn"]
        }
    }
}
```

---

## 2. Cross-Reference Navigation

### DocType Knowledge Path

```python
# knowledge_graph/navigation.py

class KnowledgeNavigator:
    """Navigate the knowledge graph for contextual guidance."""
    
    def __init__(self):
        self.graph = KNOWLEDGE_GRAPH
    
    def get_doctype_journey(self, doctype_name):
        """
        Get complete knowledge path for a DocType.
        
        Path: DocType -> Lifecycle -> Hooks -> Performance -> Scaling -> Blueprint -> Failure
        """
        
        doctype = self.graph["nodes"].get(doctype_name)
        if not doctype:
            return {"error": f"DocType {doctype_name} not in knowledge graph"}
        
        journey = {
            "doctype": doctype,
            "lifecycle_path": self._get_lifecycle_path(doctype_name),
            "performance_considerations": self._get_performance_path(doctype_name),
            "scaling_requirements": self._get_scaling_path(doctype_name),
            "architecture_blueprints": self._get_blueprint_path(doctype_name),
            "failure_prevention": self._get_failure_path(doctype_name)
        }
        
        return journey
    
    def _get_lifecycle_path(self, doctype_name):
        """Get lifecycle and hooks for DocType."""
        
        edges = self.graph["edges"].get(doctype_name, {})
        lifecycles = edges.get("uses_lifecycle", [])
        hooks = edges.get("has_hooks", [])
        
        lifecycle_details = []
        
        for lifecycle in lifecycles:
            node = self.graph["nodes"].get(lifecycle, {})
            lifecycle_details.append({
                "name": lifecycle,
                "trigger": node.get("trigger"),
                "use_for": node.get("use_for", []),
                "performance_notes": node.get("performance_impact")
            })
        
        return {
            "lifecycles": lifecycle_details,
            "hooks": hooks,
            "recommendations": self._get_lifecycle_recommendations(lifecycles)
        }
    
    def _get_performance_path(self, doctype_name):
        """Get performance considerations for DocType."""
        
        edges = self.graph["edges"].get(doctype_name, {})
        sensitivity = edges.get("performance_sensitivity", "Medium")
        
        # Based on sensitivity, recommend strategies
        strategies = []
        
        if sensitivity == "High":
            strategies = [
                self.graph["nodes"]["indexing"],
                self.graph["nodes"]["caching"],
                self.graph["nodes"]["background_jobs"]
            ]
        elif sensitivity == "Medium":
            strategies = [
                self.graph["nodes"]["indexing"],
                self.graph["nodes"]["caching"]
            ]
        
        return {
            "sensitivity": sensitivity,
            "recommended_strategies": strategies,
            "thresholds": self._get_performance_thresholds(doctype_name)
        }
    
    def _get_scaling_path(self, doctype_name):
        """Get scaling strategy for DocType volume."""
        
        # Query for record count predictions
        scaling_needs = {
            "volume_tiers": {
                "reasonable": {"records": 100000, "strategy": "Standard"},
                "large": {"records": 500000, "strategy": "Optimization"},
                "enterprise": {"records": 2000000, "strategy": "Partitioning"}
            },
            "scaling_strategies": [
                self.graph["nodes"]["vertical_scaling"],
                self.graph["nodes"]["horizontal_scaling"]
            ]
        }
        
        return scaling_needs
    
    def _get_blueprint_path(self, doctype_name):
        """Get relevant architecture blueprints."""
        
        # Map DocType to relevant blueprints
        blueprint_mapping = {
            "Sales Order": ["multi_company", "api_first"],
            "Purchase Order": ["multi_company", "vendor_portal"],
            "Work Order": ["manufacturing", "multi_company"],
            "Stock Entry": ["multi_warehouse", "inventory_heavy"]
        }
        
        blueprints = blueprint_mapping.get(doctype_name, ["standard"])
        
        return {
            "relevant_blueprints": [
                self.graph["nodes"][bp] for bp in blueprints if bp in self.graph["nodes"]
            ],
            "design_considerations": self._get_blueprint_considerations(doctype_name)
        }
    
    def _get_failure_path(self, doctype_name):
        """Get failure scenarios and prevention."""
        
        # Identify relevant failure scenarios
        failure_mapping = {
            "Sales Order": ["volume_failure", "concurrency_failure"],
            "GL Entry": ["volume_failure"],
            "Stock Ledger Entry": ["volume_failure"]
        }
        
        failures = failure_mapping.get(doctype_name, [])
        
        return {
            "relevant_failures": [
                self.graph["nodes"][f] for f in failures if f in self.graph["nodes"]
            ],
            "prevention_strategies": self._get_prevention_strategies(failures)
        }
    
    def navigate_from_symptom(self, symptom):
        """
        Navigate from failure symptom to solution.
        
        Symptom -> Failure -> Architecture -> Pattern -> Implementation
        """
        
        # Map symptoms to failures
        symptom_map = {
            "slow_list_view": ["volume_failure", "index_missing"],
            "request_timeout": ["concurrency_failure", "background_job_needed"],
            "memory_exhaustion": ["concurrency_failure", "query_optimization"],
            "session_loss": ["redis_failure", "persistence_issue"]
        }
        
        failures = symptom_map.get(symptom, [])
        
        # Build solution path
        solution_path = []
        
        for failure in failures:
            failure_node = self.graph["nodes"].get(failure, {})
            
            # Get prevention strategies
            prevention = self.graph["edges"].get(failure, {}).get("solved_by", [])
            
            solution_path.append({
                "failure": failure,
                "symptoms": failure_node.get("symptoms", []),
                "solutions": prevention,
                "implementation": self._get_implementation_guide(prevention)
            })
        
        return solution_path
    
    def _get_lifecycle_recommendations(self, lifecycles):
        """Generate recommendations based on lifecycles."""
        
        recommendations = []
        
        if "validate" in lifecycles:
            recommendations.append({
                "hook": "validate",
                "pattern": "Keep validation logic in service layer",
                "anti_pattern": "Avoid external API calls in validate"
            })
        
        if "on_submit" in lifecycles:
            recommendations.append({
                "hook": "on_submit",
                "pattern": "Use enqueue for side effects",
                "anti_pattern": "Don't block for long operations"
            })
        
        return recommendations
    
    def _get_performance_thresholds(self, doctype_name):
        """Get performance thresholds for DocType."""
        
        return {
            "list_view_ms": 500,
            "form_load_ms": 1500,
            "save_operation_ms": 1000,
            "report_generation_s": 10,
            "concurrent_users": 200
        }
    
    def _get_blueprint_considerations(self, doctype_name):
        """Get blueprint-specific considerations."""
        
        return {
            "multi_company": ["Add company filter to all queries", "Test cross-company isolation"],
            "manufacturing": ["Consider BOM depth", "Plan cost rollup strategy"],
            "api_first": ["Design RESTful endpoints", "Implement rate limiting"]
        }
    
    def _get_prevention_strategies(self, failures):
        """Get prevention strategies for failures."""
        
        strategies = []
        
        for failure in failures:
            failure_node = self.graph["nodes"].get(failure, {})
            strategies.extend(failure_node.get("prevention", []))
        
        return strategies
    
    def _get_implementation_guide(self, strategies):
        """Get implementation guide for strategies."""
        
        guides = {
            "indexing": "See 33_PERFORMANCE/01_performance_engineering.md",
            "partitioning": "See 38_UPGRADE/01_upgrade_migration_intelligence.md",
            "archiving": "See 33_PERFORMANCE/01_performance_engineering.md",
            "horizontal_scaling": "See 36_BLUEPRINTS/01_system_design_blueprints.md",
            "caching": "See 33_PERFORMANCE/01_performance_engineering.md",
            "background_jobs": "See 39_TEMPLATES_V2/01_code_pattern_library.md"
        }
        
        return {s: guides.get(s, "Documentation available") for s in strategies}

# Usage examples
navigator = KnowledgeNavigator()

# Get complete journey for Sales Order
sales_order_journey = navigator.get_doctype_journey("Sales Order")

# Navigate from symptom
solution = navigator.navigate_from_symptom("slow_list_view")
```

---

## 3. Interactive Knowledge Queries

### Query Patterns

```python
# knowledge_graph/queries.py

class KnowledgeQueries:
    """Common knowledge graph queries."""
    
    def __init__(self, graph):
        self.graph = graph
    
    def find_anti_patterns(self, context):
        """Find anti-patterns for given context."""
        
        # Based on context (doctype, volume, complexity)
        anti_patterns = {
            "high_volume_doctype": [
                "Missing indexes on filter fields",
                "Synchronous external API calls",
                "Loading all records in memory"
            ],
            "complex_workflow": [
                "Business logic in client scripts",
                "Fat controller methods",
                "Hard-coded company logic"
            ],
            "multi_company": [
                "Missing company filters",
                "Cross-company data leakage",
                "Permission bypass"
            ]
        }
        
        return anti_patterns.get(context, [])
    
    def recommend_patterns(self, requirements):
        """Recommend patterns based on requirements."""
        
        patterns = []
        
        if requirements.get("audit_required"):
            patterns.append({
                "pattern": "event_driven",
                "reason": "Full audit trail of all changes",
                "see": "42_ADVANCED/01_advanced_engineering.md"
            })
        
        if requirements.get("high_read_volume"):
            patterns.append({
                "pattern": "cqrs",
                "reason": "Separate read optimization",
                "see": "42_ADVANCED/01_advanced_engineering.md"
            })
        
        if requirements.get("complex_validation"):
            patterns.append({
                "pattern": "service_layer",
                "reason": "Centralized, testable validation",
                "see": "39_TEMPLATES_V2/01_code_pattern_library.md"
            })
        
        return patterns
    
    def estimate_risk(self, architecture_plan):
        """Estimate risk for architecture plan."""
        
        risk_factors = []
        
        # Check for scale risks
        if architecture_plan.get("projected_records", 0) > 500000:
            risk_factors.append({
                "type": "volume",
                "level": "High",
                "mitigation": "Add partitioning strategy"
            })
        
        if architecture_plan.get("concurrent_users", 0) > 500:
            risk_factors.append({
                "type": "concurrency",
                "level": "High",
                "mitigation": "Plan horizontal scaling"
            })
        
        if len(architecture_plan.get("integrations", [])) > 10:
            risk_factors.append({
                "type": "complexity",
                "level": "Medium",
                "mitigation": "Add integration monitoring"
            })
        
        return {
            "overall_risk": "High" if any(r["level"] == "High" for r in risk_factors) else "Medium",
            "factors": risk_factors,
            "risk_mitigation_priority": [r for r in risk_factors if r["level"] == "High"]
        }
    
    def generate_learning_path(self, skill_level, goal):
        """Generate learning path from current to target."""
        
        paths = {
            "beginner_to_intermediate": {
                "steps": [
                    "Master DocType fundamentals (00_FOUNDATION)",
                    "Learn hooks and controllers (01_CORE_SYSTEM)",
                    "Practice with templates (20_TEMPLATES)",
                    "Study anti-patterns (32_ANTI_PATTERNS)"
                ],
                "estimated_time": "4-6 weeks"
            },
            "intermediate_to_advanced": {
                "steps": [
                    "Study performance engineering (33_PERFORMANCE)",
                    "Master security framework (34_SECURITY)",
                    "Learn service layer patterns (39_TEMPLATES_V2)",
                    "Practice with blueprints (36_BLUEPRINTS)"
                ],
                "estimated_time": "6-8 weeks"
            },
            "advanced_to_architect": {
                "steps": [
                    "Master event-driven architecture (42_ADVANCED)",
                    "Study system constraints (40_CONSTRAINTS)",
                    "Learn failure scenarios (41_FAILURE)",
                    "Practice estimation and strategy (43_STRATEGY)"
                ],
                "estimated_time": "8-12 weeks"
            }
        }
        
        return paths.get(f"{skill_level}_to_{goal}", {})
```

---

## 4. Knowledge Graph Visualization

### Map Visualization

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         KNOWLEDGE GRAPH OVERVIEW                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐                │
│  │   DocTypes   │─────▶│  Lifecycle   │─────▶│  Performance │                │
│  │              │      │   Hooks      │      │              │                │
│  │ Sales Order  │      │              │      │ Indexing     │                │
│  │ Customer     │      │ validate     │      │ Caching      │                │
│  │ Item         │      │ on_submit    │      │ Background   │                │
│  │ ...          │      │ on_cancel    │      │ Jobs         │                │
│  └──────────────┘      └──────────────┘      └──────────────┘                │
│         │                    │                    │                          │
│         │                    │                    │                          │
│         ▼                    ▼                    ▼                          │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐                │
│  │   Security   │      │   Scaling    │      │ Architecture │                │
│  │              │      │              │      │  Blueprints  │                │
│  │ Permissions  │      │ Vertical     │      │              │                │
│  │ Roles        │      │ Horizontal   │      │ Multi-Company│                │
│  │ API Security │      │ Sharding     │      │ Manufacturing│                │
│  └──────────────┘      └──────────────┘      └──────────────┘                │
│         │                    │                    │                          │
│         └──────────────────────┼────────────────────┘                          │
│                                │                                               │
│                                ▼                                               │
│                       ┌──────────────┐                                        │
│                       │    Failure   │                                        │
│                       │   Scenarios  │                                        │
│                       │              │                                        │
│                       │ Volume       │                                        │
│                       │ Concurrency  │                                        │
│                       │ Redis        │                                        │
│                       └──────────────┘                                        │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘

NAVIGATION PATH EXAMPLE:
Sales Order → on_submit → Performance (Enqueue) → Scaling (Async) 
→ Blueprint (Event-Driven) → Failure (Queue Overflow Prevention)
```

---

## 5. Quick Reference Index

### Topic Cross-Reference

| Start With | Leads To | For Understanding |
|------------|----------|-------------------|
| DocType Design | 00_FOUNDATION, 01_CORE_SYSTEM | Core concepts |
| Slow Performance | 33_PERFORMANCE, 32_ANTI_PATTERNS | Optimization |
| Security Issue | 34_SECURITY | Hardening |
| Complex Workflow | 42_ADVANCED, 39_TEMPLATES_V2 | Architecture |
| Scale Planning | 40_CONSTRAINTS, 36_BLUEPRINTS | Capacity |
| Failure Recovery | 41_FAILURE | Resilience |
| Implementation | 35_ENTERPRISE, 43_STRATEGY | Delivery |

### Skill Level Pathways

```
BEGINNER PATH:
SKILL.md → 00_FOUNDATION → 01_CORE_SYSTEM → 20_TEMPLATES → 22_DEBUGGING

INTERMEDIATE PATH:
30_COGNITIVE → 32_ANTI_PATTERNS → 33_PERFORMANCE → 34_SECURITY → 35_ENTERPRISE

ADVANCED PATH:
36_BLUEPRINTS → 38_UPGRADE → 39_TEMPLATES_V2 → 40_CONSTRAINTS → 41_FAILURE

ARCHITECT PATH:
42_ADVANCED → 43_STRATEGY → 44_KNOWLEDGE_GRAPH (recursive refinement)
```

---

**This knowledge graph transforms isolated documentation into an interconnected cognitive system.**

Navigate by: DocType → Need → Pattern → Implementation → Verification
