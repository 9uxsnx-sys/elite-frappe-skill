// ERPNext Form Script Template
// Place this file in: custom_app/public/js/[doctype].js
// Or use Client Script DocType for server-side storage

// ============================================
// BASIC FORM EVENTS
// ============================================

frappe.ui.form.on('Sales Invoice', {
    // On form load
    refresh: function(frm) {
        // Add custom buttons
        frm.add_custom_button(__('Custom Action'), function() {
            custom_action(frm);
        }, __('Actions'));
        
        // Add indicator
        if (frm.doc.status === 'Overdue') {
            frm.dashboard.add_indicator(__('Overdue'), 'red');
        }
        
        // Show/hide fields
        frm.toggle_display('custom_field', frm.doc.custom_condition);
        
        // Set field properties
        frm.set_df_property('field_name', 'read_only', 1);
        frm.set_df_property('field_name', 'hidden', 0);
    },
    
    // On form setup (before load)
    setup: function(frm) {
        // Set up custom queries
        frm.set_query('customer', function() {
            return {
                filters: {
                    'disabled': 0,
                    'customer_group': 'Commercial'
                }
            };
        });
    },
    
    // On new document
    onload: function(frm) {
        if (frm.is_new()) {
            frm.set_value('posting_date', frappe.datetime.get_today());
        }
    },
    
    // Before save
    before_save: function(frm) {
        // Calculate custom values
        calculate_custom_totals(frm);
    },
    
    // After save
    after_save: function(frm) {
        frappe.show_alert(__('Document saved successfully'));
    }
});

// ============================================
// FIELD EVENTS
// ============================================

frappe.ui.form.on('Sales Invoice', {
    // On field change
    customer: function(frm, cdt, cdn) {
        if (frm.doc.customer) {
            // Fetch customer details
            frappe.db.get_value('Customer', frm.doc.customer, 
                ['customer_name', 'credit_limit', 'territory'])
                .then(r => {
                    if (r.message) {
                        frm.set_value('customer_name', r.message.customer_name);
                        check_credit_limit(frm, r.message.credit_limit);
                    }
                });
        }
    },
    
    // Date field change
    posting_date: function(frm) {
        // Set due date based on payment terms
        if (frm.doc.payment_terms_template) {
            frappe.model.with_doc('Payment Terms Template', 
                frm.doc.payment_terms_template, function() {
                    calculate_due_date(frm);
                });
        }
    }
});

// ============================================
// CHILD TABLE EVENTS
// ============================================

frappe.ui.form.on('Sales Invoice Item', {
    // On item add
    items_add: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        row.qty = 1; // Default qty
        frm.refresh_field('items');
    },
    
    // On item remove
    items_remove: function(frm, cdt, cdn) {
        calculate_totals(frm);
    },
    
    // On field change in child
    item_code: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (row.item_code) {
            frappe.db.get_value('Item', row.item_code, 
                ['item_name', 'stock_uom', 'standard_rate'])
                .then(r => {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, 'item_name', r.message.item_name);
                        frappe.model.set_value(cdt, cdn, 'uom', r.message.stock_uom);
                        frappe.model.set_value(cdt, cdn, 'rate', r.message.standard_rate);
                    }
                });
        }
    },
    
    qty: function(frm, cdt, cdn) {
        calculate_row_amount(frm, cdt, cdn);
        calculate_totals(frm);
    },
    
    rate: function(frm, cdt, cdn) {
        calculate_row_amount(frm, cdt, cdn);
        calculate_totals(frm);
    }
});

// ============================================
// CUSTOM FUNCTIONS
// ============================================

function calculate_row_amount(frm, cdt, cdn) {
    var row = locals[cdt][cdn];
    var amount = (row.qty || 0) * (row.rate || 0);
    frappe.model.set_value(cdt, cdn, 'amount', amount);
}

function calculate_totals(frm) {
    var total = 0;
    frm.doc.items.forEach(function(item) {
        total += (item.amount || 0);
    });
    frm.set_value('total_amount', total);
}

function calculate_custom_totals(frm) {
    // Custom calculation logic
    var custom_total = 0;
    frm.doc.items.forEach(function(item) {
        if (item.custom_charge) {
            custom_total += item.custom_charge;
        }
    });
    frm.doc.custom_total = custom_total;
}

function check_credit_limit(frm, credit_limit) {
    frappe.db.get_value('Customer', frm.doc.customer, 
        ['credit_limit', 'outstanding_amount'])
        .then(r => {
            if (r.message && frm.doc.grand_total > r.message.credit_limit) {
                frappe.msgprint({
                    title: __('Credit Limit Warning'),
                    message: __('Order exceeds credit limit'),
                    indicator: 'orange'
                });
            }
        });
}

function custom_action(frm) {
    frappe.confirm(
        __('Are you sure you want to perform this action?'),
        function() {
            // On Yes
            frappe.call({
                method: 'custom_app.api.custom_action',
                args: {
                    docname: frm.doc.name
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.show_alert(__('Action completed'));
                        frm.reload_doc();
                    }
                }
            });
        }
    );
}

// ============================================
// SERVER CALLS
// ============================================

function get_server_data(frm) {
    frappe.call({
        method: 'custom_app.api.get_data',
        args: {
            customer: frm.doc.customer
        },
        callback: function(r) {
            if (r.message) {
                console.log('Server data:', r.message);
            }
        }
    });
}

// Using frappe.db (for simple queries)
function get_item_details(item_code) {
    frappe.db.get_value('Item', item_code, 'standard_rate')
        .then(r => {
            if (r.message) {
                return r.message.standard_rate;
            }
        });
}

// ============================================
// DIALOG EXAMPLES
// ============================================

function show_custom_dialog(frm) {
    var d = new frappe.ui.Dialog({
        title: __('Custom Dialog'),
        fields: [
            {
                fieldname: 'item_code',
                fieldtype: 'Link',
                label: 'Item',
                options: 'Item',
                reqd: 1
            },
            {
                fieldname: 'qty',
                fieldtype: 'Float',
                label: 'Quantity',
                default: 1
            }
        ],
        primary_action: function(values) {
            // Add item to table
            var child = frm.add_child('items');
            child.item_code = values.item_code;
            child.qty = values.qty;
            frm.refresh_field('items');
            d.hide();
        }
    });
    d.show();
}

// ============================================
// FORM NAVIGATION
// ============================================

function navigate_to_related_doc(frm) {
    frappe.set_route('Form', 'Sales Order', frm.doc.sales_order);
}

// ============================================
// PRINT/CUSTOM ACTIONS
// ============================================

function print_custom_format(frm) {
    frappe.call({
        method: 'frappe.www.printview.get_html',
        args: {
            doc: frm.doc.name,
            format: 'Custom Print Format',
            doctype: frm.docty
