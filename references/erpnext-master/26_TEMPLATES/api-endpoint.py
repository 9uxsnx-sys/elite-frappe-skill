# ERPNext API Endpoint Template
# Place this file in: custom_app/api.py

import frappe
from frappe import _
from frappe.utils import flt, getdate, nowdate


# ============================================
# GET APIs
# ============================================

@frappe.whitelist()
def get_customer_info(customer):
    """
    Get customer information
    
    Args:
        customer: Customer name/code
    
    Returns:
        dict: Customer details
    """
    if not frappe.db.exists("Customer", customer):
        frappe.throw(_("Customer {0} not found").format(customer))
    
    customer_doc = frappe.get_doc("Customer", customer)
    
    return {
        "name": customer_doc.name,
        "customer_name": customer_doc.customer_name,
        "customer_type": customer_doc.customer_type,
        "credit_limit": customer_doc.credit_limit,
        "territory": customer_doc.territory,
        "customer_group": customer_doc.customer_group,
    }


@frappe.whitelist()
def get_item_price(item_code, price_list="Standard Selling"):
    """
    Get item price from price list
    
    Args:
        item_code: Item code
        price_list: Price list name
    
    Returns:
        float: Item price
    """
    from erpnext.stock.get_item_details import get_item_price
    
    price = get_item_price({
        "item_code": item_code,
        "price_list": price_list,
    })
    
    return price or 0


@frappe.whitelist()
def get_stock_balance(item_code, warehouse=None):
    """
    Get stock balance for item
    
    Args:
        item_code: Item code
        warehouse: Warehouse name (optional)
    
    Returns:
        float: Stock quantity
    """
    from erpnext.stock.utils import get_stock_balance
    
    if warehouse:
        return get_stock_balance(item_code, warehouse)
    else:
        # Get total stock across all warehouses
        total = frappe.db.sql("""
            SELECT SUM(actual_qty) 
            FROM `tabStock Ledger Entry`
            WHERE item_code = %s
        """, (item_code,))[0][0]
        return flt(total)


@frappe.whitelist()
def get_outstanding_invoices(customer):
    """
    Get outstanding invoices for customer
    
    Args:
        customer: Customer name
    
    Returns:
        list: List of outstanding invoices
    """
    invoices = frappe.get_all("Sales Invoice",
        filters={
            "customer": customer,
            "docstatus": 1,
            "outstanding_amount": [">", 0]
        },
        fields=["name", "posting_date", "grand_total", "outstanding_amount"]
    )
    
    return invoices


# ============================================
# POST APIs
# ============================================

@frappe.whitelist()
def create_sales_invoice(customer, items):
    """
    Create Sales Invoice
    
    Args:
        customer: Customer name
        items: JSON string of items list
    
    Returns:
        str: Sales Invoice name
    """
    import json
    
    items = json.loads(items) if isinstance(items, str) else items
    
    si = frappe.get_doc({
        "doctype": "Sales Invoice",
        "customer": customer,
        "company": frappe.db.get_single_value("Global Defaults", "default_company"),
        "items": items
    })
    si.insert()
    
    return si.name


@frappe.whitelist()
def create_payment_entry(payment_type, party, amount, paid_to, reference=None):
    """
    Create Payment Entry
    
    Args:
        payment_type: "Receive" or "Pay"
        party: Customer or Supplier name
        amount: Payment amount
        paid_to: Account to credit (bank/cash)
        reference: Sales Invoice reference (optional)
    
    Returns:
        str: Payment Entry name
    """
    pe = frappe.get_doc({
        "doctype": "Payment Entry",
        "payment_type": payment_type,
        "party_type": "Customer" if payment_type == "Receive" else "Supplier",
        "party": party,
        "paid_amount": amount,
        "received_amount": amount,
        "paid_to": paid_to,
    })
    
    if reference:
        pe.append("references", {
            "reference_doctype": "Sales Invoice",
            "reference_name": reference,
            "allocated_amount": amount
        })
    
    pe.insert()
    pe.submit()
    
    return pe.name


# ============================================
# UPDATE APIs
# ============================================

@frappe.whitelist()
def update_customer_credit_limit(customer, credit_limit):
    """
    Update customer credit limit
    
    Args:
        customer: Customer name
        credit_limit: New credit limit
    
    Returns:
        bool: Success
    """
    frappe.db.set_value("Customer", customer, "credit_limit", flt(credit_limit))
    return True


@frappe.whitelist()
def cancel_document(doctype, docname):
    """
    Cancel a document
    
    Args:
        doctype: Document type
        docname: Document name
    
    Returns:
        bool: Success
    """
    doc = frappe.get_doc(doctype, docname)
    doc.cancel()
    return True


# ============================================
# SEARCH APIs
# ============================================

@frappe.whitelist()
def search_customers(search_term):
    """
    Search customers by name or code
    
    Args:
        search_term: Search string
    
    Returns:
        list: Matching customers
    """
    customers = frappe.get_all("Customer",
        filters={
            "customer_name": ["like", f"%{search_term}%"]
        },
        fields=["name", "customer_name", "customer_type"],
        limit=10
    )
    
    return customers


@frappe.whitelist()
def search_items(search_term, item_group=None):
    """
    Search items by name or code
    
    Args:
        search_term: Search string
        item_group: Filter by item group (optional)
    
    Returns:
        list: Matching items
    """
    filters = {"item_name": ["like", f"%{search_term}%"]}
    
    if item_group:
        filters["item_group"] = item_group
    
    items = frappe.get_all("Item",
        filters=filters,
        fields=["name", "item_name", "item_group", "stock_uom"],
        limit=10
    )
    
    return items


# ============================================
# BULK APIs
# ============================================

@frappe.whitelist()
def bulk_create_customers(customers_data):
    """
    Bulk create customers
    
    Args:
        customers_data: JSON string of customers list
    
    Returns:
        dict: Created customers
    """
    import json
    
    customers_data = json.loads(customers_data) if isinstance(customers_data, str) else customers_data
    created = []
    errors = []
    
    for customer_data in customers_data:
        try:
            customer = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": customer_data.get("customer_name"),
                "customer_type": customer_data.get("customer_type", "Company"),
                "customer_group": customer_data.get("customer_group", "All Customer Groups"),
                "territory": customer_data.get("territory", "All Territories"),
            })
            customer.insert()
            created.append(customer.name)
        except Exception as e:
            errors.append({
                "customer_name": customer_data.get("customer_name"),
                "error": str(e)
            })
    
    return {"created": created, "errors": errors}


# ============================================
# CUSTOM QUERY APIs
# ============================================

@frappe.whitelist()
def get_sales_summary(from_date, to_date, customer=None):
    """
    Get sales summary report
    
    Args:
        from_date: Start date
        to_date: End date
        customer: Filter by customer (optional)
    
    Returns:
        dict: Sales summary
    """
    filters = {
        "posting_date": ["between", [from_date, to_date]],
        "docstatus": 1
    }
    
    if customer:
        filters["customer"] = customer
    
    invoices = frappe.get_all("Sales Invoice",
        filters=filters,
        fields=[
