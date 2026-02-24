# Unit Testing Guide

## Quick Reference
Comprehensive guide to writing and running tests for Frappe/ERPNext applications.

## AI Prompt
```
When writing tests for Frappe:
1. Use frappe.test_runner for integration tests
2. Write unit tests for business logic
3. Test edge cases and error conditions
4. Mock external dependencies
5. Run tests before every deployment
```

---

## Test Structure

### Test File Location
```
my_app/
├── my_app/
│   └── test/
│       ├── __init__.py
│       ├── test_my_app.py        # Main test file
│       ├── test_utils.py         # Utility tests
│       └── fixtures/
│           └── test_data.json    # Test data
```

### Test File Template
```python
# my_app/my_app/test/test_my_app.py
import frappe
import unittest

class TestMyApp(unittest.TestCase):
    def setUp(self):
        """Run before each test"""
        frappe.set_user("Administrator")
    
    def tearDown(self):
        """Run after each test"""
        pass
    
    def test_document_creation(self):
        """Test creating a document"""
        doc = frappe.get_doc({
            "doctype": "Project Task",
            "title": "Test Task"
        })
        doc.insert()
        
        self.assertTrue(doc.name)
        self.assertEqual(doc.status, "Open")
        
        # Cleanup
        doc.delete()
    
    def test_validation(self):
        """Test validation logic"""
        doc = frappe.get_doc({
            "doctype": "Project Task",
            "title": "Test Task",
            "start_date": "2024-01-31",
            "end_date": "2024-01-01"  # Invalid: before start
        })
        
        with self.assertRaises(frappe.ValidationError):
            doc.insert()
```

---

## Running Tests

### Basic Commands
```bash
# Run all tests
bench run-tests

# Run tests for specific app
bench --app my_app run-tests

# Run specific test file
bench run-tests --app my_app --test-module my_app.my_app.test.test_my_app

# Run specific test class
bench run-tests --app my_app --test-module my_app.my_app.test.test_my_app.TestMyApp

# Run specific test method
bench run-tests --app my_app --test-module my_app.my_app.test.test_my_app.TestMyApp.test_document_creation
```

### Pytest Integration
```bash
# Install pytest
pip install pytest pytest-frappe

# Run with pytest
bench --site site1.local pytest my_app.my_app.test.test_my_app -v

# Run with coverage
bench --site site1.local pytest my_app.my_app.test --cov=my_app --cov-report=html
```

---

## Test Fixtures

### Creating Test Data
```python
import frappe

def create_test_company():
    """Create test company"""
    if frappe.db.exists("Company", "Test Company"):
        return frappe.get_doc("Company", "Test Company")
    
    company = frappe.get_doc({
        "doctype": "Company",
        "company_name": "Test Company",
        "abbr": "TC",
        "default_currency": "USD",
        "country": "United States"
    })
    company.insert()
    return company

def create_test_customer():
    """Create test customer"""
    if frappe.db.exists("Customer", "Test Customer"):
        return frappe.get_doc("Customer", "Test Customer")
    
    customer = frappe.get_doc({
        "doctype": "Customer",
        "customer_name": "Test Customer",
        "customer_type": "Company",
        "customer_group": "All Customer Groups",
        "territory": "All Territories"
    })
    customer.insert()
    return customer
```

### Using Fixtures in Tests
```python
class TestSalesInvoice(unittest.TestCase):
    def setUp(self):
        self.company = create_test_company()
        self.customer = create_test_customer()
    
    def test_create_invoice(self):
        invoice = frappe.get_doc({
            "doctype": "Sales Invoice",
            "customer": self.customer.name,
            "company": self.company.name,
            "due_date": "2024-12-31",
            "items": [{
                "item_code": "_Test Item",
                "qty": 1,
                "rate": 100
            }]
        })
        invoice.insert()
        
        self.assertTrue(invoice.name)
        self.assertEqual(invoice.customer, self.customer.name)
```

---

## Mocking

### Mocking Database Calls
```python
from unittest.mock import patch, MagicMock

@patch('frappe.db.get_value')
def test_with_mock(self, mock_get_value):
    """Test with mocked database"""
    mock_get_value.return_value = "Test Value"
    
    # Your code that calls frappe.db.get_value
    result = get_customer_name("CUST-001")
    
    self.assertEqual(result, "Test Value")
```

### Mocking External Services
```python
from unittest.mock import patch

@patch('my_app.utils.send_email')
def test_email_sending(self, mock_send_email):
    """Test email sending"""
    mock_send_email.return_value = True
    
    result = notify_user("user@test.com", "Test Subject")
    
    mock_send_email.assert_called_once_with(
        "user@test.com", 
        "Test Subject"
    )
    self.assertTrue(result)
```

---

## Integration Tests

### Testing DocType Operations
```python
class TestSalesWorkflow(unittest.TestCase):
    def setUp(self):
        # Create test data
        self.customer = create_test_customer()
        self.item = frappe.get_doc("Item", "_Test Item")
    
    def test_sales_order_flow(self):
        """Test complete sales order flow"""
        # Create Sales Order
        so = frappe.get_doc({
            "doctype": "Sales Order",
            "customer": self.customer.name,
            "delivery_date": "2024-12-31",
            "items": [{
                "item_code": self.item.name,
                "qty": 10,
                "rate": 100
            }]
        })
        so.insert()
        
        # Submit Order
        so.submit()
        self.assertEqual(so.docstatus, 1)
        
        # Create Delivery Note
        dn = frappe.get_doc({
            "doctype": "Delivery Note",
            "customer": self.customer.name,
            "items": [{
                "item_code": self.item.name,
                "qty": 10,
                "so_detail": so.items[0].name
            }]
        })
        dn.insert()
        dn.submit()
        
        # Create Sales Invoice
        si = frappe.get_doc({
            "doctype": "Sales Invoice",
            "customer": self.customer.name,
            "items": [{
                "item_code": self.item.name,
                "qty": 10,
                "rate": 100,
                "dn_detail": dn.items[0].name
            }]
        })
        si.insert()
        si.submit()
        
        self.assertEqual(si.docstatus, 1)
```

### Testing API Endpoints
```python
import requests

class TestAPI(unittest.TestCase):
    base_url = "http://site1.local"
    
    def test_api_authentication(self):
        """Test API login"""
        response = requests.post(
            f"{self.base_url}/api/method/login",
            data={
                "usr": "Administrator",
                "pwd": "admin"
            }
        )
        self.assertEqual(response.status_code, 200)
    
    def test_get_items(self):
        """Test getting items via API"""
        session = requests.Session()
        session.post(
            f"{self.base_url}/api/method/login",
            data={"usr": "Administrator", "pwd": "admin"}
        )
        
        response = session.get(
            f"{self.base_url}/api/method/my_app.api.get_items"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
```

---

## Test Coverage

### Coverage Configuration
```ini
# pytest.ini
[pytest]
testpaths = my_app/my_app/test
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --cov=my_app --cov-report=html --cov-report=term

[coverage:run]
source = my_app
omit = 
    */test/*
    */migrations/*
    */__pycache__/*
```

### Running with Coverage
```bash
# Generate coverage report
bench --site site1.local pytest my_app --cov=my_app --cov-report=html

# View HTML report
open htmlcov/index.html

# Minimum coverage requirement
# Add to CI/CD pipeline
bench --site site1.local pytest --cov=my_app --cov-fail-under=80
```

---

## Best Practices

### Test Organization
1. **One test file per module**: `test_utils.py`, `test_api.py`, `test_hooks.py`
2. **Descriptive test names**: `test_should_create_invoice_with_valid_data`
3. **AAA Pattern**: Arrange, Act, Assert
4. **Isolate tests**: Each test should be independent

### Test Data Management
1. **Create fresh data** in setUp
2. **Clean up** in tearDown
3. **Use factories** for complex objects
4. **Don't rely on existing data**

### What to Test
- ✅ Business logic
- ✅ Validation rules
- ✅ API endpoints
- ✅ Workflows
- ✅ Permission checks
- ❌ Don't test Frappe internals
- ❌ Don't test third-party services (mock them)

---

## CI/CD Integration

### GitHub Actions
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Bench
      run: |
        pip install bench
        bench init frappe-bench
        cd frappe-bench
        bench get-app ../.
    
    - name: Run Tests
      run: |
        cd frappe-bench
        bench --site test.local install-app my_app
        bench --site test.local pytest --cov=my_app --cov-fail-under=80
```

---

## Related Topics
- [Bench Commands](../00_FOUNDATION/03_bench-commands.md)
- [App Development](../00_FOUNDATION/04_app-development.md)
- [Error Handling & Debugging](../22_DEBUGGING/02_error-handling-debugging.md)
