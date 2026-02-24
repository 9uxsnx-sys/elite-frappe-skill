# Frappe DocType Controller Template
# Place this file in: custom_app/doctype/[doctype]/[doctype].py

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, nowdate


class CustomDocType(Document):
    # ============================================
    # LIFECYCLE HOOKS
    # ============================================
    
    def before_insert(self):
        """Called before document is inserted"""
        pass
    
    def validate(self):
        """Main validation - called on save"""
        self.validate_required()
        self.validate_business_rules()
    
    def before_save(self):
        """Called before saving"""
        pass
    
    def on_update(self):
        """Called after saving"""
        pass
    
    def after_insert(self):
        """Called after insertion"""
        pass
    
    def before_submit(self):
        """Called before submission"""
        pass
    
    def on_submit(self):
        """Called after submission"""
        pass
    
    def before_cancel(self):
        """Called before cancellation"""
        pass
    
    def on_cancel(self):
        """Called after cancellation"""
        pass
    
    def on_trash(self):
        """Called before deletion"""
        pass
    
    # ============================================
    # VALIDATION METHODS
    # ============================================
    
    def validate_required(self):
        """Validate required fields"""
        if not self.subject:
            frappe.throw(_("Subject is required"))
    
    def validate_business_rules(self):
        """Validate business logic"""
        pass
    
    # ============================================
    # CUSTOM METHODS
    # ============================================
    
    def 
