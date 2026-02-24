# ERPNext DocType Controller Template
# Place this file in: custom_app/doctype/custom_doctype/custom_doctype.py

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, nowdate


class CustomDocType(Document):
    # ============================================
    # LIFECYCLE HOOKS
    # ============================================
    
    def before_insert(self):
        """Called before document is inserted into database"""
        self.set_defaults()
        self.validate_unique_constraints()
    
    def before_naming(self):
        """Called before name is set (for custom naming)"""
        pass
    
    def autoname(self):
        """Custom naming logic - overrides default naming series"""
        # Example: CUSTOM-{customer}-{####}
        # self.name = f"CUSTOM-{self.customer}-{frappe.db.count('Custom DocType') + 1:04d}"
        pass
    
    def validate(self):
        """Main validation - called on save and before submit"""
        self.validate_required_fields()
        self.validate_dates()
        self.validate_quantities()
        self.calculate_totals()
        self.validate_against_stock()
    
    def before_save(self):
        """Called before document is saved"""
        self.update_status()
    
    def on_update(self):
        """Called after document is updated (insert or modify)"""
        self.update_related_documents()
    
    def after_insert(self):
        """Called after document is inserted"""
        self.send_notification()
    
    def before_submit(self):
        """Called before document is submitted"""
        self.check_permissions()
        self.validate_for_submit()
    
    def on_submit(self):
        """Called after document is submitted"""
        self.make_gl_entries()
        self.update_stock_ledger()
        self.create_related_documents()
        self.update_status()
    
    def before_cancel(self):
        """Called before document is cancelled"""
        self.check_if_cancel_allowed()
    
    def on_cancel(self):
        """Called after document is cancelled"""
        self.cancel_gl_entries()
        self.cancel_stock_ledger()
        self.cancel_related_documents()
    
    def on_trash(self):
        """Called before document is deleted"""
        self.check_if_delete_allowed()
    
    def after_delete(self):
        """Called after document is deleted"""
        self.cleanup_references()
    
    def on_update_after_submit(self):
        """Called when fields are updated on submitted document"""
        self.validate_update_after_submit()
    
    def before_rename(self, old_name, new_name, merge=False):
        """Called before document is renamed"""
        self.check_if_rename_allowed()
    
    def after_rename(self, old_name, new_name, merge=False):
        """Called after document is renamed"""
        self.update_references(old_name, new_name)
    
    # ============================================
    # VALIDATION METHODS
    # ============================================
    
    def validate_required_fields(self):
        """Validate required fields"""
        if not self.customer:
            frappe.throw(_("Customer is required"))
        
        if not self.items:
            frappe.throw(_("At least one item is required"))
    
    def validate_dates(self):
        """Validate date fields"""
        if self.from_date and self.to_date:
            if getdate(self.from_date) > getdate(self.to_date):
                frappe.throw(_("From Date cannot be after To Date"))
        
        if self.due_date and getdate(self.due_date) < getdate(self.posting_date):
            frappe.throw(_("Due Date cannot be before Posting Date"))
    
    def validate_quantities(self):
        """Validate quantity fields"""
        for item in self.items:
            if flt(item.qty) <= 0:
                frappe.throw(_("Quantity must be greater than 0 for item {0}").format(item.item_code))
            
            if flt(item.rate) < 0:
                frappe.throw(_("Rate cannot be negative for item {0}").format(item.item_code))
    
    def validate_against_stock(self):
        """Validate stock availability"""
        for item in self.items:
            if item.warehouse and item.qty:
                from erpnext.stock.utils import get_stock_balance
                available_qty = get_stock_balance(item.item_code, item.warehouse)
                if available_qty < item.qty:
                    frappe.throw(
                        _("Insufficient stock for item {0}. Available: {1}, Required: {2}").format(
                            item.item_code, available_qty, item.qty
                        )
                    )
    
    def validate_unique_constraints(self):
        """Check for duplicate records"""
        if frappe.db.exists("Custom DocType", {"customer": self.customer, "docstatus": 1}):
            frappe.throw(_("Record already exists for this customer"))
    
    # ============================================
    # CALCULATION METHODS
    # ============================================
    
    def calculate_totals(self):
        """Calculate document totals"""
        self.total_qty = 0
        self.total_amount = 0
        
        for item in self.items:
            item.amount = flt(item.qty) * flt(item.rate)
            self.total_qty += flt(item.qty)
            self.total_amount += item.amount
        
        self.calculate_taxes()
        self.grand_total = self.total_amount + self.total_tax
    
    def calculate_taxes(self):
        """Calculate taxes"""
        self.total_tax = 0
        
        for tax in self.taxes:
            if tax.charge_type == "On Net Total":
                tax.tax_amount = flt(self.total_amount) * flt(tax.rate) / 100
            elif tax.charge_type == "Actual":
                pass  # tax_amount is already set
            self.total_tax += flt(tax.tax_amount)
    
    # ============================================
    # LEDGER METHODS
    # ============================================
    
    def make_gl_entries(self):
        """Create General Ledger entries"""
        from erpnext.accounts.general_ledger import make_gl_entries
        
        gl_entries = []
        
        # Debit entry
        gl_entries.append(
            self.get_gl_dict({
                "account": self.debit_account,
                "party_type": "Customer",
                "party": self.customer,
                "debit": self.grand_total,
                "credit": 0,
                "against": self.credit_account,
            })
        )
        
        # Credit entry
        gl_entries.append(
            self.get_gl_dict({
                "account": self.credit_account,
                "debit": 0,
                "credit": self.total_amount,
                "against": self.customer,
            })
        )
        
        # Tax entries
        for tax in self.taxes:
            gl_entries.append(
                self.get_gl_dict({
                    "account": tax.account_head,
                    "debit": 0,
                    "credit": tax.tax_amount,
                    "against": self.customer,
                })
            )
        
        make_gl_entries(gl_entries, cancel=0)
    
    def cancel_gl_entries(self):
        """Cancel GL entries on document cancellation"""
        from erpnext.accounts.general_ledger import make_gl_entries
        make_gl_entries(self.get_gl_entries(), cancel=1)
    
    def update_stock_ledger(self):
        """Update stock ledger entries"""
        from erpnext.stock.stock_ledger import make_sl_entries
        
        sl_entries = []
        for item in self.items:
            sl_entries.append({
                "item_code": item.item_code,
                "warehouse": item.warehouse,
                "actual_qty": -flt(item.qty),  # Negative for issue
                "voucher_no": self.name,
                "voucher_type": self.doctype,
                "posting_date": self.posting_date,
                "valuation_rate": item.valuation_rate,
            })
 
