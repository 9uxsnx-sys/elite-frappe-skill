# Item Master

## Quick Reference
Item is the product/service master. Contains pricing, stock, tax, and accounting info. Items can have variants, be stockable or non-stockable, and belong to groups.

## AI Prompt
\`\`\`
When working with items:
1. Check if item is stock vs non-stock
2. Verify UOM and conversion factors
3. Set correct item group for reporting
4. Configure tax templates
5. Set valuation method for stock items
\`\`\`

---

## Item DocType

### Key Fields
| Field | Type | Description |
|-------|------|-------------|
| item_code | Data | Unique identifier |
| item_name | Data | Display name |
| item_group | Link | Categorization |
| stock_uom | Link | Base unit of measure |
| is_stock_item | Check | Track inventory |
| is_sales_item | Check | Sellable |
| is_purchase_item | Check | Purchasable |
| has_variants | Check | Has variants |
| variant_of | Link | Parent template |
| valuation_rate | Currency | Stock value rate |

### Item Types
| Type | Stock | Sales | Purchase |
|------|-------|-------|----------|
| Stock Item | Yes | Yes | Yes |
| Service | No | Yes | Optional |
| Non-Stock | No | Yes | Yes |
| Template | No | No | No |
| Variant | Yes | Yes | Yes |

### Creating Item
\`\`\`python
item = frappe.get_doc({
    "doctype": "Item",
    "item_code": "LAPTOP-001",
    "item_name": "Laptop 15-inch",
    "item_group": "Products",
    "stock_uom": "Nos",
    "is_stock_item": 1,
    "is_sales_item": 1,
    "is_purchase_item": 1,
    "valuation_rate": 35000,
    "standard_rate": 45000,
    "description": "15-inch Laptop with 8GB RAM"
})
item.insert()
\`\`\`

---

## Item Groups

### Structure
\`\`\`
All Item Groups
├── Products
│   ├── Electronics
│   │   ├── Laptops
│   │   └── Mobiles
│   └── Furniture
├── Services
│   ├── Consulting
│   └── Support
└── Raw Materials
\`\`\`

### Creating Item Group
\`\`\`python
group = frappe.get_doc({
    "doctype": "Item Group",
    "item_group_name": "Laptops",
    "parent_item_group": "Electronics"
})
group.insert()
\`\`\`

---

## Unit of Measure (UOM)

### Common UOMs
- Nos (Numbers)
- Kg (Kilograms)
- Mtr (Meters)
- Ltr (Liters)
- Box
- Pack

### UOM Conversion
\`\`\`python
item = frappe.get_doc({
    "doctype": "Item",
    "item_code": "WIRE-001",
    "item_name": "Electrical Wire",
    "stock_uom": "Mtr",
    "uoms": [
        {"uom": "Mtr", "conversion_factor": 1},
        {"uom": "Km", "conversion_factor": 1000},
        {"uom": "Feet", "conversion_factor": 0.3048}
    ]
})
item.insert()
\`\`\`

---

## Item Variants

### Template Item
\`\`\`python
template = frappe.get_doc({
    "doctype": "Item",
    "item_code": "TSHIRT",
    "item_name": "T-Shirt",
    "item_group": "Products",
    "stock_uom": "Nos",
    "has_variants": 1,
    "variant_based_on": "Item Attribute",
    "attributes": [
        {"attribute": "Colour"},
        {"attribute": "Size"}
    ]
})
template.insert()
\`\`\`

### Creating Variant
\`\`\`python
# Method 1: Auto-create
from erpnext.controllers.item_variant import create_variant
variant = create_variant("TSHIRT", {"Colour": "Red", "Size": "M"})
variant.item_code = "TSHIRT-RED-M"
variant.insert()

# Method 2: Manual
variant = frappe.get_doc({
    "doctype": "Item",
    "variant_of": "TSHIRT",
    "item_code": "TSHIRT-BLUE-L",
    "item_name": "T-Shirt Blue Large",
    "stock_uom": "Nos",
    "attributes": [
        {"attribute": "Colour", "attribute_value": "Blue"},
        {"attribute": "Size", "attribute_value": "L"}
    ]
})
variant.insert()
\`\`\`

---

## Item Pricing

### Item Price DocType
\`\`\`python
price = frappe.get_doc({
    "doctype": "Item Price",
    "item_code": "LAPTOP-001",
    "price_list": "Standard Selling",
    "price_list_rate": 45000,
    "currency": "INR",
    "valid_from": "2024-01-01"
})
price.insert()
\`\`\`

### Getting Price
\`\`\`python
from erpnext.stock.get_item_details import get_item_price

price = get_item_price({
    "item_code": "LAPTOP-001",
    "price_list": "Standard Selling",
    "currency": "INR"
})
\`\`\`

### Price Lists
| Price List Type | Purpose |
|-----------------|---------|
| Standard Selling | Default selling price |
| Standard Buying | Default purchase price |
| Custom | Customer/Supplier specific |

---

## Item Defaults

Set company-specific defaults for items.

\`\`\`python
item = frappe.get_doc({
    "doctype": "Item",
    "item_code": "LAPTOP-001",
    "item_defaults": [{
        "company": "My Company Ltd",
        "default_warehouse": "Stores - MC",
        "default_supplier": "XYZ Ltd",
        "buying_cost_center": "Operations - MC",
        "selling_cost_center": "Sales - MC",
        "income_account": "Sales - MC",
        "expense_account": "Cost of Goods Sold - MC"
    }]
})
item.insert()
\`\`\`

---

## Stock Items vs Non-Stock

### Stock Item
\`\`\`python
item = frappe.get_doc({
    "doctype": "Item",
    "item_code": "LAPTOP-001",
    "is_stock_item": 1,
    "valuation_rate": 35000,  # Required
    "stock_uom": "Nos",
    "item_defaults": [{
        "company": "My Company Ltd",
        "default_warehouse": "Stores - MC"
    }]
})
\`\`\`

### Non-Stock/Service Item
\`\`\`python
item = frappe.get_doc({
    "doctype": "Item",
    "item_code": "SVC-001",
    "item_name": "Consulting Service",
    "is_stock_item": 0,
    "stock_uom": "Nos",
    "is_sales_item": 1
})
\`\`\`

---

## Item API

### Get Item Details
\`\`\`python
from erpnext.stock.get_item_details import get_item_details

details = get_item_details({
    "item_code": "LAPTOP-001",
    "company": "My Company Ltd",
    "customer": "ABC Corp",
    "qty": 1,
    "doctype": "Sales Invoice"
})
# Returns: rate, warehouse, tax template, etc.
\`\`\`

### Get Stock Balance
\`\`\`python
from erpnext.stock.utils import get_stock_balance

# Current balance
balance = get_stock_balance("LAPTOP-001", "Stores - MC")

# Balance at date
balance = get_stock_balance(
    "LAPTOP-001", 
    "Stores - MC", 
    "2024-01-31"
)

# Stock projection
from erpnext.stock.utils import get_stock_value_on
value = get_stock_value_on("Stores - MC", "2024-01-31", "LAPTOP-001")
\`\`\`

### Get Item Tax Template
\`\`\`python
tax_template = frappe.db.get_value("Item", "LAPTOP-001", "item_tax_template")
\`\`\`

---

## Common Patterns

### Get or Create Item
\`\`\`python
def get_or_create_item(item_code, item_name=None, item_group="Products"):
    if frappe.db.exists("Item", item_code):
        return frappe.get_doc("Item", item_code)
    
    item = frappe.get_doc({
        "doctype": "Item",
        "item_code": item_code,
        "item_name": item_name or item_code,
        "item_group": item_group,
        "stock_uom": "Nos",
        "is_stock_item": 0,
        "is_sales_item": 1
    })
    item.insert()
    return item
\`\`\`

### Check Item Availability
\`\`\`python
def check_stock(item_code, warehouse, required_qty):
    current_qty = get_stock_balance(item_code, warehouse)
    if current_qty < required_qty:
        frappe.throw(f"Insufficient stock. Available: {current_qty}")
    return True
\`\`\`

---

## Related Topics
- [Price Lists](./03_price-lists.md)
- [Stock Entry](../05_STOCK_INVENTORY/02_stock-entry.md)
- [Item Variants](../05_STOCK_INVENTORY/08_item-variants.md)
