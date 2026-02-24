# Advanced Engineering Layer

Event-driven ERP architecture, CQRS patterns, DDD mapping, service-layer abstraction, and data warehouse export architecture.

---

## 1. Event-Driven ERP Architecture

### Event Sourcing Pattern

```python
# advanced/event_driven_architecture.py

import frappe
from datetime import datetime
from typing import List, Dict, Any

class DomainEvent:
    """
    Immutable domain event capturing business occurrence.
    
    WHY: Enables audit trail, replay, and loose coupling.
    WHEN: Complex workflows requiring traceability.
    LIMITATIONS: Eventual consistency, storage overhead.
    """
    
    def __init__(self, 
                 event_type: str, 
                 aggregate_id: str,
                 payload: Dict[str, Any],
                 metadata: Dict[str, Any] = None):
        self.event_id = frappe.generate_hash()
        self.event_type = event_type
        self.aggregate_id = aggregate_id
        self.payload = payload
        self.timestamp = datetime.utcnow().isoformat()
        self.version = 1
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "version": self.version,
            "metadata": self.metadata
        }

class EventStore:
    """
    Append-only event store for event sourcing.
    
    Stores all domain events for replay and audit.
    """
    
    def append(self, event: DomainEvent):
        """Append event to store."""
        
        doc = frappe.get_doc({
            "doctype": "Event Store",
            "event_id": event.event_id,
            "event_type": event.event_type,
            "aggregate_id": event.aggregate_id,
            "aggregate_type": event.metadata.get("aggregate_type"),
            "payload": frappe.as_json(event.payload),
            "timestamp": event.timestamp,
            "version": event.version
        })
        
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
    
    def get_events(self, 
                   aggregate_id: str = None,
                   event_type: str = None,
                   since: datetime = None) -> List[DomainEvent]:
        """Retrieve events with filtering."""
        
        filters = {}
        
        if aggregate_id:
            filters["aggregate_id"] = aggregate_id
        if event_type:
            filters["event_type"] = event_type
        if since:
            filters["timestamp"] [">=", since.isoformat()]
        
        events = frappe.get_all("Event Store",
            filters=filters,
            fields=["*"],
            order_by="timestamp asc"
        )
        
        return [self._rehydrate(e) for e in events]
    
    def _rehydrate(self, event_data) -> DomainEvent:
        """Reconstruct event from stored data."""
        
        return DomainEvent(
            event_type=event_data.event_type,
            aggregate_id=event_data.aggregate_id,
            payload=frappe.parse_json(event_data.payload),
            metadata={"aggregate_type": event_data.aggregate_type}
        )

class EventBus:
    """
    Pub/sub event bus for decoupled communication.
    
    WHY: Decouples event producers from consumers.
    WHEN: Multiple handlers need to react to same event.
    """
    
    _subscribers: Dict[str, List] = {}
    
    @classmethod
    def subscribe(cls, event_type: str, handler):
        """Subscribe handler to event type."""
        
        if event_type not in cls._subscribers:
            cls._subscribers[event_type] = []
        
        cls._subscribers[event_type].append(handler)
    
    @classmethod
    def publish(cls, event: DomainEvent):
        """Publish event to all subscribers."""
        
        # Persist first
        EventStore().append(event)
        
        # Notify subscribers
        handlers = cls._subscribers.get(event.event_type, [])
        
        for handler in handlers:
            try:
                frappe.enqueue(
                    method=handler,
                    event=event.to_dict(),
                    queue="default",
                    timeout=300
                )
            except Exception as e:
                frappe.log_error(f"Event handler failed: {e}")

# Example: Sales Order Event Sourcing
class SalesOrderAggregate:
    """
    Sales Order aggregate with event sourcing.
    
    Reconstructs state from event stream.
    """
    
    def __init__(self, order_id: str = None):
        self.order_id = order_id
        self.customer = None
        self.items = []
        self.status = "Draft"
        self.version = 0
        self.uncommitted_events = []
    
    def apply_event(self, event: DomainEvent):
        """Apply event to mutate state."""
        
        handlers = {
            "sales_order.created": self._on_created,
            "sales_order.item_added": self._on_item_added,
            "sales_order.submitted": self._on_submitted,
            "sales_order.cancelled": self._on_cancelled
        }
        
        handler = handlers.get(event.event_type)
        if handler:
            handler(event.payload)
            self.version += 1
    
    def create(self, customer: str, delivery_date: str):
        """Create new sales order."""
        
        event = DomainEvent(
            event_type="sales_order.created",
            aggregate_id=frappe.generate_hash()[:10],
            payload={
                "customer": customer,
                "delivery_date": delivery_date,
                "created_by": frappe.session.user
            },
            metadata={"aggregate_type": "Sales Order"}
        )
        
        self.apply_event(event)
        self.uncommitted_events.append(event)
        
        return self
    
    def submit(self):
        """Submit sales order."""
        
        if self.status != "Draft":
            raise ValueError("Can only submit draft orders")
        
        event = DomainEvent(
            event_type="sales_order.submitted",
            aggregate_id=self.order_id,
            payload={
                "submitted_by": frappe.session.user,
                "submitted_at": datetime.utcnow().isoformat(),
                "total_amount": sum(item["amount"] for item in self.items)
            }
        )
        
        self.apply_event(event)
        self.uncommitted_events.append(event)
    
    def save(self):
        """Save uncommitted events."""
        
        store = EventStore()
        for event in self.uncommitted_events:
            store.append(event)
        
        self.uncommitted_events = []
    
    @classmethod
    def load(cls, order_id: str) -> "SalesOrderAggregate":
        """Reconstruct aggregate from event history."""
        
        aggregate = cls(order_id)
        events = EventStore().get_events(aggregate_id=order_id)
        
        for event in events:
            aggregate.apply_event(event)
        
        return aggregate
    
    # Event handlers
    def _on_created(self, payload):
        self.order_id = self.order_id or payload.get("aggregate_id")
        self.customer = payload["customer"]
        self.status = "Draft"
    
    def _on_item_added(self, payload):
        self.items.append(payload)
    
    def _on_submitted(self, payload):
        self.status = "Submitted"
    
    def _on_cancelled(self, payload):
        self.status = "Cancelled"

# Event handlers
@EventBus.subscribe("sales_order.submitted")
def handle_order_submitted(event):
    """Handler: Notify inventory on order submission."""
    
    payload = event["payload"]
    
    # Reserve inventory
    frappe.enqueue(
        "advanced.inventory.reserve_stock",
        order_id=event["aggregate_id"],
        items=payload.get("items", [])
    )
    
    # Notify customer
    frappe.enqueue(
        "advanced.notifications.send_customer_notification",
        order_id=event["aggregate_id"],
        notification_type="order_confirmed"
    )
    
    # Update analytics
    frappe.enqueue(
        "advanced.analytics.record_order_metrics",
        order_data=payload
    )
```

---

## 2. CQRS-Style Read/Write Separation

### Command Query Responsibility Segregation

```python
# advanced/cqrs_pattern.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any
import frappe

# Commands (Write Model)
class Command(ABC):
    """Base command class."""
    
    @abstractmethod
    def execute(self):
        """Execute command."""
        pass

class CreateSalesOrderCommand(Command):
    """Command to create sales order."""
    
    def __init__(self, customer: str, items: List[Dict], delivery_date: str):
        self.customer = customer
        self.items = items
        self.delivery_date = delivery_date
    
    def execute(self):
        """Execute create command."""
        
        # Validation
        self._validate_customer()
        self._validate_items()
        
        # Create aggregate
        order = frappe.get_doc({
            "doctype": "Sales Order",
            "customer": self.customer,
            "delivery_date": self.delivery_date,
            "items": self.items
        })
        
        order.insert()
        
        # Publish event
        event = {
            "event_type": "sales_order.created",
            "order_id": order.name,
            "customer": self.customer,
            "total": order.grand_total
        }
        
        # Update read model
        ReadModelUpdater().update_on_create(event)
        
        return order.name
    
    def _validate_customer(self):
        if not frappe.db.exists("Customer", self.customer):
            raise ValueError(f"Customer {self.customer} not found")
    
    def _validate_items(self):
        if not self.items:
            raise ValueError("At least one item required")

class SubmitSalesOrderCommand(Command):
    """Command to submit sales order."""
    
    def __init__(self, order_id: str):
        self.order_id = order_id
    
    def execute(self):
        """Execute submit command."""
        
        order = frappe.get_doc("Sales Order", self.order_id)
        
        if order.docstatus != 0:
            raise ValueError("Order already processed")
        
        order.submit()
        
        # Update read model
        ReadModelUpdater().update_on_submit({
            "order_id": self.order_id,
            "status": "Submitted",
            "submitted_at": frappe.utils.now()
        })
        
        return True

# Read Model (Query side)
class SalesOrderReadModel:
    """
    Optimized read model for queries.
    
    WHY: Fast queries without joins, optimized for specific views.
    WHEN: Complex reporting, high-read scenarios.
    """
    
    def get_customer_orders_summary(self, customer: str) -> Dict:
        """Get customer order summary - single query, no joins."""
        
        # Read from denormalized view
        result = frappe.db.sql("""
            SELECT 
                total_orders,
                total_amount,
                last_order_date,
                open_orders_count
            FROM `tabCustomer Order Summary`
            WHERE customer = %s
        """, customer, as_dict=1)
        
        return result[0] if result else None
    
    def get_sales_dashboard(self, filters: Dict) -> List[Dict]:
        """Get pre-aggregated sales data."""
        
        # Use materialized view
        conditions = []
        values = []
        
        if filters.get("from_date"):
            conditions.append("date >= %s")
            values.append(filters["from_date"])
        
        if filters.get("to_date"):
            conditions.append("date <= %s")
            values.append(filters["to_date"])
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        return frappe.db.sql(f"""
            SELECT 
                date,
                customer,
                total_sales,
                order_count,
                avg_order_value
            FROM `tabSales Dashboard Daily`
            WHERE {where_clause}
            ORDER BY date DESC
        """, tuple(values), as_dict=1)

class ReadModelUpdater:
    """
    Updates read models when write model changes.
    
    Keeps read and write models eventually consistent.
    """
    
    def update_on_create(self, event: Dict):
        """Update read model on order creation."""
        
        # Update customer summary
        frappe.db.sql("""
            INSERT INTO `tabCustomer Order Summary`
            (customer, total_orders, total_amount, last_order_date)
            VALUES (%s, 1, %s, CURDATE())
            ON DUPLICATE KEY UPDATE
                total_orders = total_orders + 1,
                total_amount = total_amount + %s,
                last_order_date = GREATEST(last_order_date, CURDATE())
        """, (event["customer"], event["total"], event["total"]))
        
        # Update daily dashboard
        frappe.db.sql("""
            INSERT INTO `tabSales Dashboard Daily`
            (date, total_sales, order_count)
            VALUES (CURDATE(), %s, 1)
            ON DUPLICATE KEY UPDATE
                total_sales = total_sales + %s,
                order_count = order_count + 1
        """, (event["total"], event["total"]))
    
    def update_on_submit(self, event: Dict):
        """Update read model on order submission."""
        
        # Update status in read model
        frappe.db.sql("""
            UPDATE `tabSales Order Read Model`
            SET status = %s,
                submitted_at = %s
            WHERE order_id = %s
        """, (event["status"], event["submitted_at"], event["order_id"]))

# Command handler
class CommandHandler:
    """
    Central command handler with transaction management.
    """
    
    def handle(self, command: Command):
        """Execute command with proper error handling."""
        
        try:
            frappe.db.savepoint("command")
            
            result = command.execute()
            
            frappe.db.commit()
            return {"success": True, "result": result}
            
        except Exception as e:
            frappe.db.rollback()
            
            # Log error
            frappe.log_error(f"Command failed: {e}")
            
            return {"success": False, "error": str(e)}
```

---

## 3. Domain-Driven Design Mapping

### DDD Patterns in Frappe

```python
# advanced/ddd_mapping.py

"""
Mapping Domain-Driven Design concepts to Frappe/ERPNext.

Domain-Driven Design Concept -> Frappe Implementation:
- Entity -> DocType with identity
- Value Object -> Child Table row or separate DocType
- Aggregate Root -> DocType with lifecycle
- Domain Event -> Event Bus + DocEvents
- Repository -> frappe.get_doc() + frappe.get_all()
- Domain Service -> Custom controller or separate service class
- Application Service -> API endpoint or workflow
- Bounded Context -> Separate Frappe App
"""

from typing import List, Optional
from dataclasses import dataclass
from enum import Enum

# Value Objects
@dataclass(frozen=True)
class Money:
    """
    Value Object: Immutable monetary amount.
    
    WHY: Encapsulates currency logic, prevents floating-point errors.
    """
    amount: float
    currency: str = "USD"
    
    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)
    
    def multiply(self, factor: float) -> "Money":
        return Money(self.amount * factor, self.currency)
    
    def __str__(self):
        return f"{self.currency} {self.amount:.2f}"

@dataclass(frozen=True)
class Address:
    """Value Object: Shipping/billing address."""
    
    street: str
    city: str
    state: str
    postal_code: str
    country: str
    
    def to_dict(self):
        return {
            "address_line1": self.street,
            "city": self.city,
            "state": self.state,
            "pincode": self.postal_code,
            "country": self.country
        }

# Domain Services
class PricingService:
    """
    Domain Service: Encapsulates pricing logic.
    
    WHY: Pricing logic spans multiple aggregates (Customer, Item, Promotions).
    """
    
    def calculate_price(self, 
                       item_code: str, 
                       customer: str,
                       qty: float,
                       uom: str = None) -> Money:
        """Calculate final price with all discounts."""
        
        # Base price from item
        item = frappe.get_doc("Item", item_code)
        base_price = Money(item.standard_rate)
        
        # Apply customer-specific pricing
        customer_price = self._get_customer_price(item_code, customer)
        if customer_price:
            base_price = customer_price
        
        # Apply quantity breaks
        if qty >= 100:
            base_price = base_price.multiply(0.95)  # 5% volume discount
        
        # Apply promotional discounts
        promo_discount = self._get_promotional_discount(item_code, customer)
        if promo_discount:
            base_price = base_price.multiply(1 - promo_discount)
        
        return base_price.multiply(qty)
    
    def _get_customer_price(self, item_code: str, customer: str) -> Optional[Money]:
        """Get customer-specific price if exists."""
        
        price_list = frappe.db.get_value("Customer", customer, "default_price_list")
        
        if not price_list:
            return None
        
        price = frappe.db.get_value("Item Price",
            {"item_code": item_code, "price_list": price_list},
            "price_list_rate"
        )
        
        return Money(price) if price else None
    
    def _get_promotional_discount(self, item_code: str, customer: str) -> float:
        """Get active promotional discount."""
        
        # Check active promotions
        promotions = frappe.get_all("Promotional Scheme",
            filters={
                "docstatus": 1,
                "apply_on": "Item Code",
                "items": ["like", f'%"item_code": "{item_code}"%']
            }
        )
        
        if promotions:
            # Return first active promotion discount
            promo = frappe.get_doc("Promotional Scheme", promotions[0].name)
            return promo.price_discount * 0.01  # Convert percentage
        
        return 0.0

# Aggregate Root
class OrderAggregate:
    """
    Aggregate Root: Sales Order.
    
    Maintains consistency boundary for order + items.
    """
    
    def __init__(self, doc: frappe.Document = None):
        self._doc = doc
        self._items: List[OrderLineItem] = []
        
        if doc:
            self._hydrate_from_doc()
    
    def add_item(self, 
                item_code: str, 
                qty: float,
                pricing_service: PricingService = None):
        """Add item to order with pricing."""
        
        # Calculate price
        pricing = pricing_service or PricingService()
        price = pricing.calculate_price(
            item_code, 
            self._doc.customer,
            qty
        )
        
        line_item = OrderLineItem(
            item_code=item_code,
            qty=qty,
            rate=Money(price.amount / qty),
            amount=price
        )
        
        self._items.append(line_item)
        self._recalculate_totals()
    
    def remove_item(self, item_code: str):
        """Remove item from order."""
        
        self._items = [i for i in self._items if i.item_code != item_code]
        self._recalculate_totals()
    
    def apply_discount(self, discount_percent: float):
        """Apply order-level discount."""
        
        if discount_percent < 0 or discount_percent > 100:
            raise ValueError("Invalid discount percentage")
        
        total = sum(item.amount.amount for item in self._items)
        discount_amount = total * (discount_percent / 100)
        
        self._doc.discount_amount = discount_amount
        self._recalculate_totals()
    
    def can_submit(self) -> bool:
        """Check if order can be submitted."""
        
        if not self._items:
            return False
        
        if not self._doc.delivery_date:
            return False
        
        if self._doc.grand_total <= 0:
            return False
        
        return True
    
    def save(self):
        """Save aggregate to database."""
        
        # Update doc with items
        self._doc.items = []
        for item in self._items:
            self._doc.append("items", {
                "item_code": item.item_code,
                "qty": item.qty,
                "rate": item.rate.amount,
                "amount": item.amount.amount
            })
        
        self._doc.save()
    
    def _recalculate_totals(self):
        """Recalculate order totals."""
        
        total = sum(item.amount.amount for item in self._items)
        
        self._doc.total = total
        self._doc.grand_total = total - (self._doc.discount_amount or 0)
    
    def _hydrate_from_doc(self):
        """Hydrate aggregate from database document."""
        
        for item in self._doc.items:
            self._items.append(OrderLineItem(
                item_code=item.item_code,
                qty=item.qty,
                rate=Money(item.rate),
                amount=Money(item.amount)
            ))

# Entity within Aggregate
@dataclass
class OrderLineItem:
    """Entity: Order line item (has identity within aggregate)."""
    
    item_code: str
    qty: float
    rate: Money
    amount: Money

# Bounded Context mapping
BOUNDED_CONTEXTS = {
    "sales": {
        "aggregates": ["Sales Order", "Quotation", "Delivery Note"],
        "services": ["PricingService", "DiscountService"],
        "integration_events": ["OrderSubmitted", "OrderCancelled"]
    },
    "inventory": {
        "aggregates": ["Stock Entry", "Bin", "Serial No"],
        "services": ["StockValidationService", "ReservationService"],
        "integration_events": ["StockReserved", "StockMoved"]
    },
    "accounting": {
        "aggregates": ["GL Entry", "Journal Entry", "Payment Entry"],
        "services": ["LedgerPostingService", "ReconciliationService"],
        "integration_events": ["PaymentReceived", "InvoicePaid"]
    }
}
```

---

## 4. Service-Layer Abstraction

### Service Architecture

```python
# advanced/service_layer.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import frappe

class ApplicationService(ABC):
    """
    Base class for application services.
    
    WHY: Encapsulates use case logic, coordinates domain objects.
    WHEN: Complex operations spanning multiple aggregates.
    """
    
    def __init__(self):
        self._errors = []
    
    @abstractmethod
    def execute(self, command: Dict) -> Dict:
        """Execute use case."""
        pass
    
    def _validate(self, command: Dict) -> bool:
        """Validate command. Override in subclass."""
        return True
    
    def _log_error(self, message: str):
        """Log error."""
        self._errors.append(message)
        frappe.log_error(message)
    
    def _get_result(self) -> Dict:
        """Get execution result."""
        return {
            "success": len(self._errors) == 0,
            "errors": self._errors if self._errors else None
        }

class OrderCreationService(ApplicationService):
    """
    Application Service: Create order with all validations.
    
    Coordinates: Customer validation, pricing, inventory check.
    """
    
    def execute(self, command: Dict) -> Dict:
        """
        Execute order creation.
        
        Command: {
            "customer": str,
            "items": [{"item_code": str, "qty": float}],
            "delivery_date": str,
            "payment_terms": str
        }
        """
        
        try:
            # Validate
            if not self._validate_customer(command["customer"]):
                return self._get_result()
            
            if not self._validate_items(command["items"]):
                return self._get_result()
            
            # Check inventory
            if not self._check_inventory(command["items"]):
                return self._get_result()
            
            # Calculate pricing
            pricing = self._calculate_pricing(command)
            
            # Check credit limit
            if not self._check_credit_limit(command["customer"], pricing["total"]):
                return self._get_result()
            
            # Create order
            order = self._create_order(command, pricing)
            
            # Reserve inventory
            self._reserve_inventory(order.name, command["items"])
            
            # Send notifications
            self._send_notifications(order)
            
            return {
                "success": True,
                "order_id": order.name,
                "total": pricing["total"]
            }
            
        except Exception as e:
            self._log_error(f"Order creation failed: {e}")
            return self._get_result()
    
    def _validate_customer(self, customer: str) -> bool:
        """Validate customer exists and is active."""
        
        if not frappe.db.exists("Customer", customer):
            self._log_error(f"Customer {customer} not found")
            return False
        
        status = frappe.db.get_value("Customer", customer, "disabled")
        if status:
            self._log_error(f"Customer {customer} is disabled")
            return False
        
        return True
    
    def _validate_items(self, items: List[Dict]) -> bool:
        """Validate all items exist and are active."""
        
        for item in items:
            if not frappe.db.exists("Item", item["item_code"]):
                self._log_error(f"Item {item['item_code']} not found")
                return False
        
        return True
    
    def _check_inventory(self, items: List[Dict]) -> bool:
        """Check sufficient inventory for all items."""
        
        for item in items:
            available = frappe.db.get_value("Bin",
                {"item_code": item["item_code"]},
                "actual_qty"
            ) or 0
            
            if available < item["qty"]:
                self._log_error(
                    f"Insufficient inventory for {item['item_code']}: "
                    f"available {available}, required {item['qty']}"
                )
                return False
        
        return True
    
    def _calculate_pricing(self, command: Dict) -> Dict:
        """Calculate pricing for order."""
        
        pricing_service = PricingService()
        
        total = 0
        item_prices = []
        
        for item in command["items"]:
            price = pricing_service.calculate_price(
                item["item_code"],
                command["customer"],
                item["qty"]
            )
            
            total += price.amount
            item_prices.append({
                "item_code": item["item_code"],
                "qty": item["qty"],
                "rate": price.amount / item["qty"],
                "amount": price.amount
            })
        
        return {
            "total": total,
            "items": item_prices
        }
    
    def _check_credit_limit(self, customer: str, amount: float) -> bool:
        """Check customer credit limit."""
        
        credit_limit = frappe.db.get_value("Customer", customer, "credit_limit")
        
        if credit_limit and amount > credit_limit:
            outstanding = frappe.db.get_value("Customer", customer, "outstanding_amount")
            
            if outstanding + amount > credit_limit:
                self._log_error(
                    f"Order exceeds credit limit for {customer}. "
                    f"Limit: {credit_limit}, Current: {outstanding}, New: {amount}"
                )
                return False
        
        return True
    
    def _create_order(self, command: Dict, pricing: Dict) -> frappe.Document:
        """Create sales order document."""
        
        order = frappe.get_doc({
            "doctype": "Sales Order",
            "customer": command["customer"],
            "delivery_date": command["delivery_date"],
            "items": pricing["items"]
        })
        
        order.insert()
        return order
    
    def _reserve_inventory(self, order_id: str, items: List[Dict]):
        """Reserve inventory for order."""
        
        for item in items:
            frappe.enqueue(
                "advanced.inventory.reserve_stock",
                order_id=order_id,
                item_code=item["item_code"],
                qty=item["qty"]
            )
    
    def _send_notifications(self, order: frappe.Document):
        """Send order creation notifications."""
        
        # Notify customer
        frappe.enqueue(
            "advanced.notifications.send_order_confirmation",
            order_id=order.name,
            customer=order.customer
        )
        
        # Notify sales team if high value
        if order.grand_total > 10000:
            frappe.enqueue(
                "advanced.notifications.alert_sales_manager",
                order_id=order.name
            )

# Infrastructure Services
class NotificationService:
    """
    Infrastructure Service: Handle notifications.
    
    WHY: Abstracts notification channels (email, SMS, push).
    """
    
    def send_email(self, recipient: str, subject: str, template: str, context: Dict):
        """Send email notification."""
        
        frappe.sendmail(
            recipients=[recipient],
            subject=subject,
            template=template,
            args=context
        )
    
    def send_sms(self, phone: str, message: str):
        """Send SMS notification."""
        
        # Integration with SMS provider
        pass
    
    def send_push(self, user: str, title: str, body: str):
        """Send push notification."""
        
        frappe.publish_realtime(
            event="push_notification",
            message={"title": title, "body": body},
            user=user
        )

class AuditService:
    """
    Infrastructure Service: Audit logging.
    
    WHY: Centralized audit trail for compliance.
    """
    
    def log_action(self, 
                  user: str,
                  action: str,
                  entity_type: str,
                  entity_id: str,
                  changes: Dict = None):
        """Log audited action."""
        
        frappe.get_doc({
            "doctype": "Audit Log",
            "user": user,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "changes": frappe.as_json(changes) if changes else None,
            "timestamp": frappe.utils.now()
        }).insert(ignore_permissions=True)
```

---

## 5. Data Warehouse Export Architecture

### ETL Pipeline

```python
# advanced/data_warehouse_export.py

import frappe
from datetime import datetime, timedelta
from typing import Iterator, Dict, List

class DataWarehouseExporter:
    """
    Export operational data to data warehouse.
    
    WHY: Separates analytics workload from operational database.
    WHEN: Reporting queries impacting OLTP performance.
    """
    
    def __init__(self, warehouse_config: Dict):
        self.config = warehouse_config
        self.batch_size = 1000
    
    def export_incremental(self, 
                        entity_type: str,
                        since: datetime = None) -> Dict:
        """
        Export changed data since last sync.
        
        WHY: Minimizes export time and system impact.
        """
        
        if not since:
            since = datetime.now() - timedelta(hours=24)
        
        exporter = self._get_exporter(entity_type)
        
        total_exported = 0
        errors = []
        
        try:
            for batch in exporter.get_changed_records(since, self.batch_size):
                # Transform to warehouse schema
                transformed = [exporter.transform(r) for r in batch]
                
                # Load to warehouse
                self._load_to_warehouse(entity_type, transformed)
                
                total_exported += len(batch)
                
                # Checkpoint
                self._update_checkpoint(entity_type, batch[-1]["modified"])
                
                # Yield control
                frappe.db.commit()
            
            return {
                "success": True,
                "entity_type": entity_type,
                "records_exported": total_exported,
                "since": since.isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "entity_type": entity_type,
                "error": str(e),
                "records_exported": total_exported
            }
    
    def _get_exporter(self, entity_type: str):
        """Get appropriate exporter for entity type."""
        
        exporters = {
            "sales_orders": SalesOrderExporter(),
            "invoices": InvoiceExporter(),
            "customers": CustomerExporter(),
            "inventory": InventoryExporter()
        }
        
        return exporters.get(entity_type)
    
    def _load_to_warehouse(self, entity_type: str, records: List[Dict]):
        """Load records to data warehouse."""
        
        # This would integrate with your DW (Snowflake, BigQuery, Redshift)
        # For now, simulate with file export
        
        import json
        
        filename = f"/tmp/warehouse_export_{entity_type}_{datetime.now():%Y%m%d_%H%M%S}.jsonl"
        
        with open(filename, 'a') as f:
            for record in records:
                f.write(json.dumps(record) + '\n')
    
    def _update_checkpoint(self, entity_type: str, last_modified: datetime):
        """Update sync checkpoint."""
        
        frappe.cache.set_value(
            f"warehouse_checkpoint:{entity_type}",
            last_modified.isoformat()
        )

class EntityExporter(ABC):
    """Base class for entity exporters."""
    
    @abstractmethod
    def get_changed_records(self, since: datetime, batch_size: int) -> Iterator[List[Dict]]:
        """Get records changed since timestamp."""
        pass
    
    @abstractmethod
    def transform(self, record: Dict) -> Dict:
        """Transform to warehouse schema."""
        pass

class SalesOrderExporter(EntityExporter):
    """Export sales orders to warehouse."""
    
    def get_changed_records(self, since: datetime, batch_size: int) -> Iterator[List[Dict]]:
        """Get changed sales orders in batches."""
        
        offset = 0
        
        while True:
            records = frappe.get_all("Sales Order",
                filters={"modified": [">=", since]},
                fields=["*"],
                order_by="modified",
                limit_page_length=batch_size,
                limit_start=offset
            )
            
            if not records:
                break
            
            yield records
            offset += batch_size
    
    def transform(self, record: Dict) -> Dict:
        """Transform to star schema."""
        
        return {
            "order_key": record["name"],
            "customer_key": record["customer"],
            "order_date": record["transaction_date"],
            "delivery_date": record["delivery_date"],
            "status": record["status"],
            "total_amount": record["grand_total"],
            "currency": record["currency"],
            "created_timestamp": record["creation"],
            "modified_timestamp": record["modified"]
        }

class InvoiceExporter(EntityExporter):
    """Export invoices to warehouse."""
    
    def get_changed_records(self, since: datetime, batch_size: int) -> Iterator[List[Dict]]:
        """Get changed invoices in batches."""
        
        offset = 0
        
        while True:
            records = frappe.get_all("Sales Invoice",
                filters={"modified": [">=", since]},
                fields=["*"],
                order_by="modified",
                limit_page_length=batch_size,
                limit_start=offset
            )
            
            if not records:
                break
            
            yield records
            offset += batch_size
    
    def transform(self, record: Dict) -> Dict:
        """Transform to fact table format."""
        
        return {
            "invoice_key": record["name"],
            "order_key": record.get("sales_order"),
            "customer_key": record["customer"],
            "invoice_date": record["posting_date"],
            "due_date": record["due_date"],
            "total_amount": record["grand_total"],
            "outstanding_amount": record["outstanding_amount"],
            "is_paid": record["outstanding_amount"] == 0,
            "payment_terms_days": (record["due_date"] - record["posting_date"]).days if record.get("due_date") else None
        }

# Scheduler configuration
scheduler_events = {
    "hourly": [
        "advanced.data_warehouse_export.run_incremental_export"
    ],
    "daily": [
        "advanced.data_warehouse_export.run_full_export"
    ]
}

def run_incremental_export():
    """Run incremental exports for all entities."""
    
    exporter = DataWarehouseExporter({})
    
    entities = ["sales_orders", "invoices", "customers"]
    
    results = {}
    for entity in entities:
        results[entity] = exporter.export_incremental(entity)
    
    # Log results
    frappe.logger().info(f"Warehouse export results: {results}")
    
    return results
```

---

## Summary: Advanced Pattern Selection

| Pattern | Complexity | Use When | Avoid When |
|---------|-----------|----------|------------|
| Event Sourcing | High | Audit requirements, need replay | Simple CRUD, small scale |
| CQRS | High | Read/write asymmetry, complex reports | Simple apps, small data |
| DDD | Medium | Complex domain, changing requirements | Simple forms, CRUD apps |
| Service Layer | Medium | Multiple use cases, complex logic | Simple workflows |
| Data Warehouse | Medium | Analytics impact on OLTP | Small data, simple reports |
