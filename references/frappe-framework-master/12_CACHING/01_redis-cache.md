# Redis Cache

## Quick Reference
Frappe uses Redis for caching. Access via frappe.cache. Set/get values, use decorators for auto-caching.

## AI Prompt
```
When using cache:
1. Use frappe.cache.set_value/get_value
2. Use @frappe.cache() decorator for functions
3. Set appropriate TTL
4. Clear cache when data changes
5. Don't cache sensitive data
```

---

## Basic Operations

### Set Value
```python
# Simple set
frappe.cache.set_value("my_key", "my_value")

# With TTL (seconds)
frappe.cache.set_value("my_key", "my_value", expires_in_sec=3600)

# Set hash
frappe.cache.hset("my_hash", "field", "value")
```

### Get Value
```python
# Simple get
value = frappe.cache.get_value("my_key")

# Get with default
value = frappe.cache.get_value("my_key", "default_value")

# Get hash
value = frappe.cache.hget("my_hash", "field")

# Get all hash
values = frappe.cache.hgetall("my_hash")
```

### Delete Value
```python
# Delete single
frappe.cache.delete_value("my_key")

# Delete pattern
frappe.cache.delete_keys("my_prefix_*")

# Clear all
frappe.clear_cache()
```

---

## Cache Decorator

```python
# Cache function result
@frappe.cache()
def get_expensive_data(param):
    # Expensive computation
    return heavy_calculation(param)

# First call - computes and caches
result = get_expensive_data("value")

# Second call - returns cached
result = get_expensive_data("value")

# Clear specific cache
get_expensive_data.clear_cache("value")
```

### With Key Generator
```python
@frappe.cache(key_generator=lambda p: f"data:{p}")
def get_data(param):
    return compute(param)

# Cache key: "data:value"
```

---

## Cache Patterns

### Configuration Cache
```python
@frappe.cache()
def get_app_settings():
    return frappe.get_single("App Settings").as_dict()

# Use throughout app
settings = get_app_settings()
```

### List Cache
```python
@frappe.cache()
def get_active_items():
    return frappe.get_all("Item",
        filters={"status": "Active"},
        fields=["name", "item_name"]
    )

# Clear on item update
def on_update(doc, method):
    get_active_items.clear_cache()
```

### User-Specific Cache
```python
def get_user_preferences(user):
    cache_key = f"user_prefs:{user}"
    prefs = frappe.cache.get_value(cache_key)
    
    if prefs is None:
        prefs = compute_preferences(user)
        frappe.cache.set_value(cache_key, prefs, expires_in_sec=3600)
    
    return prefs
```

---

## Cache Invalidation

```python
# In hooks.py
doc_events = {
    "Item": {
        "on_update": "app.cache.clear_item_cache",
        "on_trash": "app.cache.clear_item_cache"
    }
}

# In cache.py
def clear_item_cache(doc, method):
    # Clear specific cache
    get_active_items.clear_cache()
    
    # Clear pattern
    frappe.cache.delete_keys(f"item:*{doc.name}*")
```

---

## Related Topics
- [Cache Strategies](./02_cache-strategies.md)
