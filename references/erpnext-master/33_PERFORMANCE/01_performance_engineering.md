# Performance Engineering Layer

Load modeling, scaling strategies, caching architecture, and optimization patterns for enterprise Frappe/ERPNext deployments.

---

## 1. Load Modeling Framework

### Capacity Planning Model

```python
# Performance capacity calculator
class CapacityModel:
    """
    Calculate system capacity based on:
    - Concurrent users
    - Transaction rate
    - Data volume
    - Query complexity
    """
    
    BASELINE_METRICS = {
        # Single worker capacity assumptions
        "requests_per_minute": 120,
        "api_calls_per_minute": 200,
        "background_jobs_per_minute": 30,
        "report_generation_time": 10,  # seconds for 10k records
    }
    
    def __init__(self, config):
        self.concurrent_users = config.get("concurrent_users", 50)
        self.transactions_per_user = config.get("transactions_per_user", 10)  # per hour
        self.avg_records_per_query = config.get("avg_records_per_query", 1000)
        self.peak_multiplier = config.get("peak_multiplier", 2.5)
    
    def calculate_worker_requirement(self):
        """Calculate gunicorn workers needed."""
        
        # Base calculation
        requests_per_hour = self.concurrent_users * self.transactions_per_user
        requests_per_minute = requests_per_hour / 60
        
        # Add API overhead (assume 2:1 ratio of API to form requests)
        api_calls_per_minute = requests_per_minute * 2
        
        # Apply peak multiplier
        peak_requests = requests_per_minute * self.peak_multiplier
        peak_api = api_calls_per_minute * self.peak_multiplier
        
        # Calculate workers
        workers_for_requests = peak_requests / self.BASELINE_METRICS["requests_per_minute"]
        workers_for_api = peak_api / self.BASELINE_METRICS["api_calls_per_minute"]
        
        total_workers = max(workers_for_requests, workers_for_api)
        
        return {
            "recommended_workers": int(total_workers * 1.5),  # 50% headroom
            "min_workers": int(total_workers),
            "requests_per_minute": peak_requests,
            "api_calls_per_minute": peak_api,
            "breakdown": {
                "form_requests": workers_for_requests,
                "api_requests": workers_for_api
            }
        }
    
    def calculate_background_workers(self):
        """Calculate background job workers needed."""
        
        # Assume 30% of transactions generate background jobs
        job_rate = (self.concurrent_users * self.transactions_per_user * 0.3) / 60
        
        # Queue-specific requirements
        return {
            "default": max(2, int(job_rate / 10)),
            "short": max(1, int(job_rate / 20)),
            "long": max(1, int(job_rate / 30)),
            "scheduler": 1
        }
    
    def estimate_database_connections(self):
        """Estimate MariaDB connection pool size."""
        workers = self.calculate_worker_requirement()["recommended_workers"]
        bg_workers = sum(self.calculate_background_workers().values())
        
        # Each worker needs 2 connections (read + write)
        # Background jobs need 1 connection each
        # Add 20% headroom + base connections
        
        total = (workers * 2) + bg_workers
        with_headroom = int(total * 1.2) + 10
        
        return {
            "recommended_pool_size": min(with_headroom, 500),  # MariaDB limit
            "min_connections": total,
            "max_connections": min(with_headroom, 500)
        }

# Usage example
config = {
    "concurrent_users": 500,
    "transactions_per_user": 20,
    "avg_records_per_query": 5000,
    "peak_multiplier": 3.0
}

model = CapacityModel(config)
workers = model.calculate_worker_requirement()
bg_workers = model.calculate_background_workers()
db_connections = model.estimate_database_connections()
```

### Record Count Thresholds

| Volume Tier | Records | Implications | Required Actions |
|-------------|---------|--------------|------------------|
| **Small** | < 10k | Standard ORM acceptable | None |
| **Medium** | 10k - 100k | Add indexes | Index filter fields |
| **Large** | 100k - 500k | Query optimization | Query builder, caching |
| **Enterprise** | 500k - 2M | Background processing | Async operations, partitioning |
| **Massive** | > 2M | Architecture review | Read replicas, data warehousing |

### Performance Thresholds

```python
PERFORMANCE_THRESHOLDS = {
    # API Response Times
    "api_response_p95": 500,  # ms
    "api_response_p99": 1000,  # ms
    "list_view_load": 2000,  # ms for 50 records
    "form_load": 1500,  # ms
    "report_generation": 30000,  # ms
    
    # Database Operations
    "single_query": 100,  # ms for <10k records
    "batch_query": 500,  # ms for <100k records
    "count_query": 50,  # ms
    
    # Background Jobs
    "job_completion": 300,  # seconds
    "job_timeout": 3600,  # seconds (1 hour)
    
    # Memory
    "request_memory": 256,  # MB per request
    "background_job_memory": 512,  # MB
}

def check_performance_violation(operation_type, duration_ms):
    """Check if operation violates performance thresholds."""
    threshold = PERFORMANCE_THRESHOLDS.get(operation_type)
    
    if not threshold:
        return None
    
    if duration_ms > threshold:
        return {
            "violation": True,
            "threshold": threshold,
            "actual": duration_ms,
            "severity": "CRITICAL" if duration_ms > threshold * 2 else "WARNING"
        }
    
    return {"violation": False}
```

---

## 2. Bench Scaling Guide

### Gunicorn Worker Configuration

```python
# config/production.py

def calculate_optimal_workers():
    """
    Calculate optimal gunicorn workers.
    
    Formula: (2 * CPU_CORES) + 1
    Then adjust based on memory and load.
    """
    import multiprocessing
    import psutil
    
    cpu_cores = multiprocessing.cpu_count()
    total_memory_gb = psutil.virtual_memory().total / (1024**3)
    
    # Base calculation
    base_workers = (2 * cpu_cores) + 1
    
    # Memory constraint (256MB per worker)
    memory_constrained = int((total_memory_gb * 0.6 * 1024) / 256)
    
    # Take minimum
    optimal = min(base_workers, memory_constrained)
    
    return {
        "workers": max(4, optimal),  # Minimum 4 workers
        "worker_class": "gthread",
        "threads": 4,
        "worker_connections": 1000,
        "max_requests": 1000,
        "max_requests_jitter": 50,
        "timeout": 120,
        "keepalive": 5,
        "preload_app": True
    }

# common_site_config.json
WORKER_CONFIG = {
    "gunicorn_workers": 16,
    "gunicorn_worker_class": "gthread",
    "gunicorn_threads": 4,
    "gunicorn_timeout": 120,
    "gunicorn_keepalive": 5
}
```

### Background Worker Partitioning

```python
# Background job queue architecture

QUEUE_CONFIG = {
    "queues": [
        {
            "name": "default",
            "workers": 4,
            "timeout": 300,
            "jobs": ["email", "notification", "scheduled_task"]
        },
        {
            "name": "short",
            "workers": 2,
            "timeout": 60,
            "jobs": ["cache_warmup", "index_update", "quick_calculation"]
        },
        {
            "name": "long",
            "workers": 3,
            "timeout": 3600,
            "jobs": ["report", "import", "export", "data_migration"]
        },
        {
            "name": "heavy",
            "workers": 2,
            "timeout": 7200,
            "jobs": ["bulk_operation", "reindex", "cleanup"]
        }
    ]
}

def route_job_to_queue(job_type, estimated_duration=30):
    """Route job to appropriate queue based on characteristics."""
    
    if estimated_duration < 60:
        return "short"
    elif estimated_duration < 300:
        return "default"
    elif estimated_duration < 3600:
        return "long"
    else:
        return "heavy"

def enqueue_with_routing(method, **kwargs):
    """Enqueue job with automatic queue routing."""
    
    estimated_duration = kwargs.pop("estimated_duration", 30)
    queue = route_job_to_queue(method, estimated_duration)
    
    return frappe.enqueue(
        method=method,
        queue=queue,
        timeout=QUEUE_CONFIG["queues"][queue]["timeout"],
        **kwargs
    )
```

### Worker Count Estimation Formula

```python
def estimate_workers(concurrent_users, transaction_mix):
    """
    Comprehensive worker estimation.
    
    Args:
        concurrent_users: Expected concurrent users
        transaction_mix: Dict with keys: light, medium, heavy, batch
    """
    
    # Transaction weights (requests per minute per user)
    weights = {
        "light": 2,    # Simple form loads
        "medium": 1,   # Complex saves
        "heavy": 0.3,  # Reports
        "batch": 0.1   # Bulk operations
    }
    
    total_rpm = 0
    for tx_type, pct in transaction_mix.items():
        user_tx = concurrent_users * pct * weights[tx_type]
        total_rpm += user_tx
    
    # Add 30% headroom for API calls
    total_rpm *= 1.3
    
    # Calculate workers (120 req/min per worker)
    workers = int((total_rpm / 120) * 1.5)  # 50% headroom
    
    return {
        "gunicorn_workers": max(4, workers),
        "background_workers": {
            "default": max(2, int(workers * 0.3)),
            "long": max(1, int(workers * 0.2)),
            "short": max(1, int(workers * 0.1))
        },
        "total_workers": workers
    }

# Example usage
estimation = estimate_workers(
    concurrent_users=200,
    transaction_mix={
        "light": 0.5,
        "medium": 0.3,
        "heavy": 0.15,
        "batch": 0.05
    }
)
```

---

## 3. Redis Memory Strategy

### Caching Architecture

```python
# Multi-layer caching strategy

CACHE_STRATEGY = {
    "layers": {
        "L1": {
            "type": "in_memory",
            "ttl": 60,  # seconds
            "max_size": 1000,  # entries
            "use_for": ["user_session", "current_user", "defaults"]
        },
        "L2": {
            "type": "redis_local",
            "ttl": 300,  # 5 minutes
            "max_size_mb": 256,
            "use_for": ["doc_meta", "permission_cache", "settings"]
        },
        "L3": {
            "type": "redis_shared",
            "ttl": 3600,  # 1 hour
            "max_size_mb": 1024,
            "use_for": ["reports", "dashboards", "reference_data"]
        }
    }
}

def get_cache_key(doctype, name, version="v1"):
    """Generate consistent cache keys."""
    return f"frappe:{version}:{doctype}:{name}"

def cached_document(doctype, name, ttl=300):
    """Get document with caching."""
    cache_key = get_cache_key(doctype, name)
    
    # Try cache
    cached = frappe.cache.get_value(cache_key)
    if cached:
        return cached
    
    # Fetch and cache
    doc = frappe.get_doc(doctype, name)
    frappe.cache.set_value(cache_key, doc.as_dict(), expires_in_sec=ttl)
    
    return doc.as_dict()

def invalidate_document_cache(doctype, name):
    """Invalidate document cache on update."""
    cache_key = get_cache_key(doctype, name)
    frappe.cache.delete_value(cache_key)
    
    # Invalidate list caches
    list_pattern = f"frappe:*:{doctype}:list:*"
    frappe.cache.delete_keys(list_pattern)
```

### Cache Warming Strategy

```python
def warm_critical_caches():
    """Warm caches for critical data."""
    
    critical_data = {
        "DocType": ["User", "Role", "Company", "Customer", "Item"],
        "Report": ["Accounts Receivable", "Stock Balance", "Sales Analytics"],
        "Settings": ["System Settings", "Accounts Settings", "Stock Settings"]
    }
    
    for doctype, names in critical_data.items():
        for name in names:
            try:
                if frappe.db.exists(doctype, name):
                    doc = frappe.get_doc(doctype, name)
                    cache_key = get_cache_key(doctype, name)
                    frappe.cache.set_value(
                        cache_key, 
                        doc.as_dict(),
                        expires_in_sec=3600
                    )
            except Exception as e:
                frappe.log_error(f"Cache warming failed for {doctype}/{name}: {e}")
    
    frappe.cache.set_value("cache_last_warmed", now(), expires_in_sec=7200)

# Schedule as hourly background job
scheduler_events = {
    "hourly": ["custom_app.cache.warm_critical_caches"]
}
```

### Redis Memory Optimization

```python
# Redis configuration for production

REDIS_CONFIG = {
    "maxmemory": "2gb",
    "maxmemory_policy": "allkeys-lru",  # Evict least recently used
    "tcp_keepalive": 60,
    "timeout": 300,
    "tcp_backlog": 511,
    
    # Persistence
    "save": [
        "900 1",    # Save if 1 key changed in 15 min
        "300 10",   # Save if 10 keys changed in 5 min
        "60 10000"  # Save if 10000 keys changed in 1 min
    ],
    
    # Memory optimization
    "hash_max_ziplist_entries": 512,
    "hash_max_ziplist_value": 64,
    "list_max_ziplist_size": -2,
    "set_max_intset_entries": 512,
}

def optimize_redis_usage():
    """Optimize Redis memory usage."""
    
    # Clear expired keys
    redis = frappe.cache.redis
    
    # Get memory stats
    info = redis.info('memory')
    
    if info['used_memory'] > info['maxmemory'] * 0.9:
        # Memory pressure - clear non-essential caches
        patterns_to_clear = [
            "frappe:v1:Report:*",
            "frappe:v1:Query Report:*",
            "frappe:page:*"
        ]
        
        for pattern in patterns_to_clear:
            keys = redis.keys(pattern)
            for key in keys[:1000]:  # Limit batch size
                redis.delete(key)
        
        frappe.log_error("Redis memory pressure - cleared non-essential caches")
```

---

## 4. MariaDB Optimization

### Index Strategy

```python
# Index management utilities

CRITICAL_INDEXES = {
    "Sales Invoice": [
        ("customer", "posting_date"),
        ("company", "status"),
        ("posting_date",),
        ("status",)
    ],
    "Purchase Invoice": [
        ("supplier", "posting_date"),
        ("company", "status"),
        ("posting_date",)
    ],
    "Stock Ledger Entry": [
        ("item_code", "warehouse", "posting_date"),
        ("voucher_type", "voucher_no"),
        ("posting_date",)
    ]
}

def analyze_index_usage():
    """Analyze which indexes are being used."""
    
    query = """
        SELECT 
            OBJECT_SCHEMA,
            OBJECT_NAME,
            INDEX_NAME,
            COUNT_FETCH,
            COUNT_INSERT,
            COUNT_UPDATE,
            COUNT_DELETE
        FROM performance_schema.table_io_waits_summary_by_index_usage
        WHERE OBJECT_SCHEMA = %s
        AND COUNT_FETCH = 0
        AND INDEX_NAME != 'PRIMARY'
        ORDER BY OBJECT_NAME, INDEX_NAME
    """
    
    return frappe.db.sql(query, (frappe.db.database,), as_dict=True)

def recommend_indexes(doctype, sample_queries=None):
    """Recommend indexes based on query patterns."""
    
    meta = frappe.get_meta(doctype)
    recommendations = []
    
    # Analyze filter fields
    common_filters = [
        "customer", "supplier", "company", "posting_date", 
        "status", "item_code", "warehouse"
    ]
    
    for fieldname in common_filters:
        field = meta.get_field(fieldname)
        if not field:
            continue
        
        # Check if indexed
        if not (field.search_index or field.index):
            record_count = frappe.db.count(doctype)
            
            if record_count > 50000:
                recommendations.append({
                    "field": fieldname,
                    "priority": "HIGH" if record_count > 100000 else "MEDIUM",
                    "record_count": record_count,
                    "rationale": f"Field used in filters with {record_count} records"
                })
    
    return recommendations

def create_index(doctype, fields, index_name=None):
    """Safely create index on DocType table."""
    
    if isinstance(fields, str):
        fields = [fields]
    
    table = f"tab{doctype.replace(' ', '')}"
    index_name = index_name or f"idx_{'_'.join(fields)}"
    columns = ", ".join([f"`{f}`" for f in fields])
    
    try:
        frappe.db.sql(f"""
            ALTER TABLE `{table}`
            ADD INDEX `{index_name}` ({columns})
        """)
        
        frappe.db.commit()
        return {"success": True, "index": index_name}
        
    except Exception as e:
        if "Duplicate key name" in str(e):
            return {"success": True, "index": index_name, "note": "Already exists"}
        
        return {"success": False, "error": str(e)}
```

### Query Optimization Patterns

```python
# Query optimization patterns for large datasets

class QueryOptimizer:
    """Optimize queries for large-scale ERP."""
    
    def __init__(self, doctype):
        self.doctype = doctype
        self.record_count = frappe.db.count(doctype)
    
    def should_use_query_builder(self, fields, filters):
        """Determine if query builder is needed over ORM."""
        
        # Use query builder for complex joins
        if self.record_count < 10000:
            return False  # ORM is fine
        
        # Check for aggregation
        if any(f.get("aggregation") for f in fields):
            return True
        
        # Check for complex filters
        if len(filters) > 3:
            return True
        
        return False
    
    def optimize_list_query(self, fields, filters, limit=20):
        """Generate optimized list query."""
        
        if self.should_use_query_builder(fields, filters):
            return self._build_optimized_query(fields, filters, limit)
        else:
            return frappe.get_list(
                self.doctype,
                fields=fields,
                filters=filters,
                limit=limit
            )
    
    def _build_optimized_query(self, fields, filters, limit):
        """Build query using frappe.qb for complex scenarios."""
        
        from frappe.query_builder import DocType
        
        dt = DocType(self.doctype)
        query = frappe.qb.from_(dt).select(*fields).limit(limit)
        
        # Add filters
        for field, condition in filters.items():
            if isinstance(condition, list):
                operator, value = condition[0], condition[1]
                if operator == "=":
                    query = query.where(dt[field] == value)
                elif operator == ">":
                    query = query.where(dt[field] > value)
                elif operator == "<":
                    query = query.where(dt[field] < value)
                elif operator == "in":
                    query = query.where(dt[field].isin(value))
            else:
                query = query.where(dt[field] == condition)
        
        return query.run(as_dict=True)
    
    def paginate_large_dataset(self, filters, page_size=1000):
        """Generator for paginating large datasets."""
        
        start = 0
        while True:
            batch = frappe.get_list(
                self.doctype,
                filters=filters,
                fields=["name"],
                limit_start=start,
                limit_page_length=page_size
            )
            
            if not batch:
                break
            
            yield batch
            start += page_size
            
            # Memory management
            if start % 10000 == 0:
                frappe.db.commit()
```

---

## 5. Background Job Partitioning

### Job Segmentation Strategy

```python
# Background job segmentation

JOB_SEGMENTS = {
    "email_notifications": {
        "queue": "short",
        "timeout": 60,
        "priority": "high",
        "max_retries": 3
    },
    "report_generation": {
        "queue": "long",
        "timeout": 1800,
        "priority": "medium",
        "max_retries": 1
    },
    "bulk_data_import": {
        "queue": "heavy",
        "timeout": 7200,
        "priority": "low",
        "max_retries": 2,
        "chunk_size": 500
    },
    "index_rebuild": {
        "queue": "heavy",
        "timeout": 3600,
        "priority": "low",
        "max_retries": 1
    }
}

def enqueue_segmented_job(job_type, method, **kwargs):
    """Enqueue job with segment-specific configuration."""
    
    segment = JOB_SEGMENTS.get(job_type, JOB_SEGMENTS["default"])
    
    return frappe.enqueue(
        method=method,
        queue=segment["queue"],
        timeout=segment["timeout"],
        job_name=f"{job_type}_{now()}",
        **kwargs
    )

def chunked_background_job(doctype, method, chunk_size=500):
    """Process large dataset in background with chunking."""
    
    total_records = frappe.db.count(doctype)
    chunks = (total_records // chunk_size) + 1
    
    job_ids = []
    
    for i in range(chunks):
        job = frappe.enqueue(
            method="custom_app.jobs.process_chunk",
            doctype=doctype,
            method=method,
            chunk_start=i * chunk_size,
            chunk_size=chunk_size,
            queue="long",
            timeout=600,
            job_name=f"{doctype}_chunk_{i}"
        )
        job_ids.append(job.id)
    
    return {
        "total_chunks": chunks,
        "job_ids": job_ids,
        "estimated_completion": f"{chunks * 5} minutes"
    }
```

### Job Monitoring

```python
class JobMonitor:
    """Monitor background job performance."""
    
    def get_queue_status(self):
        """Get current queue status."""
        
        from frappe.utils.background_jobs import get_jobs
        
        queues = ["default", "short", "long", "heavy"]
        status = {}
        
        for queue in queues:
            jobs = get_jobs(queue)
            status[queue] = {
                "pending": len([j for j in jobs if not j.get("started")]),
                "running": len([j for j in jobs if j.get("started") and not j.get("ended")]),
                "failed": len([j for j in jobs if j.get("status") == "failed"]),
                "oldest_job_age": self._get_oldest_job_age(jobs)
            }
        
        return status
    
    def detect_job_stalls(self, max_age_minutes=30):
        """Detect jobs that have been running too long."""
        
        from frappe.core.doctype.rq_job.rq_job import RQJob
        
        stalled = []
        
        jobs = frappe.get_all("RQ Job",
            filters={"status": "started"},
            fields=["name", "job_id", "queue", "creation", "method"]
        )
        
        for job in jobs:
            age = time_diff_in_minutes(now(), job.creation)
            
            if age > max_age_minutes:
                stalled.append({
                    "job": job,
                    "age_minutes": age,
                    "action": "kill" if age > max_age_minutes * 2 else "warn"
                })
        
        return stalled
    
    def rebalance_queues(self):
        """Rebalance workers across queues based on load."""
        
        status = self.get_queue_status()
        
        # Simple rebalancing logic
        recommendations = {}
        
        for queue, stats in status.items():
            if stats["pending"] > 50:
                recommendations[queue] = "increase_workers"
            elif stats["pending"] == 0 and stats["running"] == 0:
                recommendations[queue] = "decrease_workers"
        
        return recommendations
```

---

## 6. Caching Strategy Blueprint

### Multi-Level Caching Architecture

```python
# Enterprise caching architecture

class EnterpriseCacheManager:
    """
    Multi-level caching for enterprise deployments.
    
    L1: Process-local cache (fastest, smallest)
    L2: Redis local instance
    L3: Redis shared/cluster
    """
    
    def __init__(self):
        self.l1_cache = {}  # In-process
        self.l1_max_size = 100
        
    def get(self, key, level="auto"):
        """Get from cache with automatic level selection."""
        
        # Try L1 first
        if key in self.l1_cache:
            return self.l1_cache[key]["value"]
        
        # Try Redis
        value = frappe.cache.get_value(key)
        
        if value and level in ["auto", "L1"]:
            # Promote to L1
            self._l1_set(key, value)
        
        return value
    
    def set(self, key, value, ttl=300, level="L2"):
        """Set cache value at specified level."""
        
        if level == "L1":
            self._l1_set(key, value, ttl)
        elif level == "L2":
            frappe.cache.set_value(key, value, expires_in_sec=ttl)
        elif level == "L3":
            # Use shared Redis with longer TTL
            frappe.cache.set_value(key, value, expires_in_sec=ttl * 2)
    
    def _l1_set(self, key, value, ttl=60):
        """Set in L1 cache with LRU eviction."""
        
        if len(self.l1_cache) >= self.l1_max_size:
            # Evict oldest
            oldest = min(self.l1_cache, key=lambda k: self.l1_cache[k]["time"])
            del self.l1_cache[oldest]
        
        self.l1_cache[key] = {
            "value": value,
            "time": now()
        }
    
    def invalidate_pattern(self, pattern):
        """Invalidate all keys matching pattern."""
        
        redis = frappe.cache.redis
        keys = redis.keys(pattern)
        
        if keys:
            redis.delete(*keys)
        
        # Clear L1 cache for matching keys
        for key in list(self.l1_cache.keys()):
            if pattern.replace("*", "") in key:
                del self.l1_cache[key]

# Usage patterns

def get_cached_report(report_name, filters):
    """Get report with intelligent caching."""
    
    cache_key = f"report:{report_name}:{hash(str(filters))}"
    
    # Try cache first
    result = cache_manager.get(cache_key)
    
    if result:
        return result
    
    # Generate report
    result = generate_report(report_name, filters)
    
    # Cache with appropriate TTL based on report type
    ttl = 3600 if "monthly" in report_name else 300
    cache_manager.set(cache_key, result, ttl=ttl, level="L3")
    
    return result
```

### Cache Invalidation Patterns

```python
# Cache invalidation on document changes

def on_document_change(doc, method):
    """Invalidate related caches on document change."""
    
    # Invalidate document cache
    cache_key = f"doc:{doc.doctype}:{doc.name}"
    frappe.cache.delete_value(cache_key)
    
    # Invalidate list caches
    list_patterns = [
        f"list:{doc.doctype}:*",
        f"report:*:{doc.doctype}:*"
    ]
    
    for pattern in list_patterns:
        frappe.cache.delete_keys(pattern)
    
    # Invalidate related DocTypes
    related = get_related_doctypes(doc.doctype)
    for related_dt in related:
        frappe.cache.delete_value(f"meta:{related_dt}")

def get_related_doctypes(doctype):
    """Get DocTypes that reference this one."""
    
    meta = frappe.get_meta(doctype)
    
    # Find DocTypes with Link fields to this
    referencing = frappe.get_all("DocField",
        filters={
            "fieldtype": "Link",
            "options": doctype
        },
        fields=["parent"],
        distinct=True
    )
    
    return [r.parent for r in referencing]
```

---

## 7. Large Dataset Pagination Standard

### Streaming Query Pattern

```python
class StreamingQuery:
    """Stream large dataset without memory exhaustion."""
    
    def __init__(self, doctype, filters=None, fields=None):
        self.doctype = doctype
        self.filters = filters or {}
        self.fields = fields or ["name"]
        self.chunk_size = 1000
    
    def stream(self):
        """Generator yielding documents in chunks."""
        
        last_name = None
        
        while True:
            # Get chunk
            chunk_filters = self.filters.copy()
            
            if last_name:
                chunk_filters["name"] = [">", last_name]
            
            chunk = frappe.get_list(
                self.doctype,
                filters=chunk_filters,
                fields=self.fields,
                order_by="name",
                limit_page_length=self.chunk_size
            )
            
            if not chunk:
                break
            
            # Yield documents
            for doc_data in chunk:
                doc = frappe.get_doc(self.doctype, doc_data.name)
                yield doc
            
            last_name = chunk[-1].name
            
            # Memory management
            frappe.db.commit()
    
    def process_in_batches(self, processor_fn):
        """Process all documents with batching."""
        
        batch = []
        results = []
        
        for doc in self.stream():
            batch.append(doc)
            
            if len(batch) >= self.chunk_size:
                results.extend(processor_fn(batch))
                batch = []
                frappe.db.commit()
        
        # Process remaining
        if batch:
            results.extend(processor_fn(batch))
        
        return results

# Usage
def reindex_all_items():
    """Reindex all items without memory issues."""
    
    stream = StreamingQuery("Item", fields=["name", "item_code"])
    
    def process_batch(batch):
        for item in batch:
            update_search_index(item)
        return ["ok"] * len(batch)
    
    results = stream.process_in_batches(process_batch)
    return f"Processed {len(results)} items"
```

---

## 8. Async Event Architecture

### Event-Driven Pattern

```python
# Event-driven architecture for decoupled processing

class EventBus:
    """Simple event bus for async processing."""
    
    def __init__(self):
        self.handlers = {}
    
    def subscribe(self, event_type, handler):
        """Subscribe handler to event type."""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
    
    def publish(self, event_type, payload):
        """Publish event to all handlers."""
        
        handlers = self.handlers.get(event_type, [])
        
        for handler in handlers:
            # Queue each handler as background job
            frappe.enqueue(
                method=handler,
                event_type=event_type,
                payload=payload,
                queue="default",
                timeout=300
            )

# Event definitions
EVENTS = {
    "sales_invoice_submitted": [
        "custom_app.events.update_customer_balance",
        "custom_app.events.notify_sales_team",
        "custom_app.events.sync_to_crm"
    ],
    "stock_entry_completed": [
        "custom_app.events.update_inventory_dashboard",
        "custom_app.events.check_reorder_levels"
    ]
}

# Usage in controller
class SalesInvoice(Document):
    def on_submit(self):
        # ... core logic ...
        
        # Fire async events
        event_bus.publish("sales_invoice_submitted", {
            "name": self.name,
            "customer": self.customer,
            "amount": self.grand_total
        })
```

---

## Summary: Performance Checklist

**Before deploying to production:**

- [ ] Capacity model calculated for expected load
- [ ] Gunicorn workers configured (2*CPU + 1)
- [ ] Background workers partitioned by queue
- [ ] Redis memory limits configured
- [ ] MariaDB indexes added for >50k tables
- [ ] Query builder used for complex aggregations
- [ ] Caching strategy defined for hot data
- [ ] Background jobs used for >500ms operations
- [ ] Pagination implemented for large datasets
- [ ] Job monitoring in place
- [ ] Database connection pool sized correctly
- [ ] Load testing completed at 2x expected peak
