# Contributing to MediManager

Cảm ơn bạn quan tâm đến việc đóng góp cho MediManager! Tài liệu này cung cấp hướng dẫn về cách phát triển và đóng góp vào dự án.

## Cấu trúc dự án

Dự án được tổ chức theo **Clean Architecture**. Vui lòng đọc [ARCHITECTURE.md](ARCHITECTURE.md) để hiểu rõ về kiến trúc.

## Quy tắc lập trình

### 1. Python Code Style

Tuân theo [PEP 8](https://pep8.org/) với một số quy ước:

```python
# ✅ Good
def calculate_total_price(quantity, unit_price):
    """
    Calculate total price for medicine purchase

    Args:
        quantity (int): Quantity of medicine
        unit_price (float): Price per unit

    Returns:
        float: Total price
    """
    return quantity * unit_price


# ❌ Bad
def calc(q, p):
    return q*p  # No documentation, unclear names
```

### 2. Naming Conventions

- **Classes**: `PascalCase` (e.g., `DatabaseManager`, `InvoiceService`)
- **Functions/Methods**: `snake_case` (e.g., `get_user_info`, `create_invoice`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_CONNECTIONS`, `DEFAULT_TIMEOUT`)
- **Private methods**: `_leading_underscore` (e.g., `_validate_input`)

### 3. Imports

Tổ chức imports theo thứ tự:

```python
# 1. Standard library
import os
import sys
from datetime import datetime

# 2. Third-party packages
from PyQt6.QtWidgets import QMainWindow
import psycopg2

# 3. Local imports
from src.config import Settings
from src.core import DBManager
```

### 4. Docstrings

Sử dụng Google-style docstrings:

```python
def create_invoice(customer_id, items, staff_id):
    """
    Create a new invoice for customer purchase

    This function creates an invoice record and associated invoice details.
    It also updates the medicine stock quantities.

    Args:
        customer_id (int): ID of the customer
        items (list): List of dicts with medicine_id, quantity, price
        staff_id (str): ID of the staff creating the invoice

    Returns:
        int: ID of the created invoice

    Raises:
        ValueError: If items list is empty
        DatabaseError: If database operation fails

    Example:
        >>> items = [
        ...     {'medicine_id': 1, 'quantity': 2, 'price': 50000},
        ...     {'medicine_id': 2, 'quantity': 1, 'price': 30000}
        ... ]
        >>> invoice_id = create_invoice(customer_id=5, items=items, staff_id='admin')
        >>> print(invoice_id)
        123
    """
    pass
```

## Quy trình phát triển

### 1. Thêm tính năng mới

#### Step 1: Tạo Service (nếu cần)

```python
# src/services/medicine_service.py

from src.core import AppContext
from src.utils.constants import MSG_SUCCESS_SAVE, MSG_ERROR_SAVE


class MedicineService:
    """Service for medicine-related business logic"""

    def __init__(self, context: AppContext):
        self.context = context
        self.db = context.db_manager

    def add_medicine(self, medicine_data):
        """Add new medicine to inventory"""
        try:
            sql = """
                INSERT INTO medicine (medicine_name, generic_name, ...)
                VALUES (%s, %s, ...)
            """
            self.db.execute(sql, tuple(medicine_data.values()))
            self.db.commit()

            # Log action
            self.context.log_action(f"Added medicine: {medicine_data['medicine_name']}")

            return True, MSG_SUCCESS_SAVE
        except Exception as e:
            self.db.rollback()
            return False, MSG_ERROR_SAVE
```

#### Step 2: Update Service Module

```python
# src/services/__init__.py

from .report_service import ReportService
from .medicine_service import MedicineService  # Add this

__all__ = ['ReportService', 'MedicineService']
```

#### Step 3: Sử dụng trong UI

```python
# src/ui/windows/medicine_window.py

from src.services import MedicineService


class MedicineWindow(QMainWindow):
    def __init__(self, context):
        super().__init__()
        self.context = context
        self.medicine_service = MedicineService(context)

    def on_save_clicked(self):
        medicine_data = self.get_form_data()
        success, message = self.medicine_service.add_medicine(medicine_data)

        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Error", message)
```

### 2. Thêm Configuration

```python
# src/config/settings.py

class Settings:
    # ... existing settings ...

    # New setting
    MAX_INVOICE_ITEMS = 50
    INVOICE_DUE_DAYS = 30
```

### 3. Thêm Constants

```python
# src/utils/constants.py

# New constants
INVOICE_STATUS_DRAFT = 'draft'
INVOICE_STATUS_CONFIRMED = 'confirmed'

INVOICE_STATUSES = [
    INVOICE_STATUS_DRAFT,
    INVOICE_STATUS_CONFIRMED,
    # ... others
]
```

### 4. Thêm Helper Function

```python
# src/utils/helpers.py

def format_date(date, format_type='display'):
    """
    Format date based on type

    Args:
        date: Date object or string
        format_type: 'display' or 'database'

    Returns:
        str: Formatted date string
    """
    from src.utils.constants import DATE_FORMAT_DISPLAY, DATE_FORMAT_DATABASE

    formats = {
        'display': DATE_FORMAT_DISPLAY,
        'database': DATE_FORMAT_DATABASE
    }

    if isinstance(date, str):
        return date

    return date.strftime(formats.get(format_type, DATE_FORMAT_DISPLAY))
```

## Database Changes

### 1. Schema Changes

Khi thay đổi schema, update file `supabase_schema.sql`:

```sql
-- Add new column to medicine table
ALTER TABLE medicine
ADD COLUMN manufacturer TEXT;

-- Add index for performance
CREATE INDEX idx_medicine_manufacturer ON medicine(manufacturer);
```

### 2. Migration Script

Tạo script migration nếu cần:

```python
# migrations/001_add_manufacturer.py

def upgrade(db_manager):
    """Add manufacturer column to medicine table"""
    sql = "ALTER TABLE medicine ADD COLUMN manufacturer TEXT;"
    db_manager.execute(sql)
    db_manager.commit()

def downgrade(db_manager):
    """Remove manufacturer column"""
    sql = "ALTER TABLE medicine DROP COLUMN manufacturer;"
    db_manager.execute(sql)
    db_manager.commit()
```

## Testing

### Unit Tests (Future)

```python
# tests/test_medicine_service.py

import unittest
from unittest.mock import Mock, MagicMock

from src.services import MedicineService


class TestMedicineService(unittest.TestCase):
    def setUp(self):
        self.mock_context = Mock()
        self.mock_db = Mock()
        self.mock_context.db_manager = self.mock_db

        self.service = MedicineService(self.mock_context)

    def test_add_medicine_success(self):
        # Arrange
        medicine_data = {
            'medicine_name': 'Aspirin',
            'generic_name': 'Acetylsalicylic acid'
        }

        # Act
        success, message = self.service.add_medicine(medicine_data)

        # Assert
        self.assertTrue(success)
        self.mock_db.execute.assert_called_once()
        self.mock_db.commit.assert_called_once()
```

## Git Workflow

### Branch Naming

- `feature/` - New features (e.g., `feature/add-barcode-scanning`)
- `bugfix/` - Bug fixes (e.g., `bugfix/fix-invoice-calculation`)
- `refactor/` - Code refactoring (e.g., `refactor/extract-auth-service`)
- `docs/` - Documentation (e.g., `docs/update-api-docs`)

### Commit Messages

Sử dụng conventional commits:

```
feat: add barcode scanning for medicines
fix: correct invoice total calculation
refactor: extract authentication to service layer
docs: update architecture documentation
style: format code according to PEP 8
test: add unit tests for medicine service
chore: update dependencies
```

### Pull Request

1. Tạo branch mới từ `main`
2. Commit changes với clear messages
3. Push và create PR
4. Request review
5. Merge sau khi được approve

## Code Review Checklist

Khi review code, kiểm tra:

- [ ] Code tuân theo PEP 8
- [ ] Functions có docstrings đầy đủ
- [ ] Không có hardcoded values (sử dụng constants/config)
- [ ] Error handling đầy đủ
- [ ] Database operations có rollback khi error
- [ ] User actions được log
- [ ] Không có SQL injection vulnerabilities
- [ ] UI messages user-friendly
- [ ] Code được organize đúng layer (config/core/service/ui)

## Best Practices

### 1. Separation of Concerns

```python
# ❌ Bad - UI logic mixed with business logic
class MedicineWindow(QMainWindow):
    def save_medicine(self):
        # Get form data
        name = self.name_input.text()

        # Business logic mixed in UI
        sql = "INSERT INTO medicine ..."
        self.db.execute(sql, ...)
        self.db.commit()


# ✅ Good - Separated layers
class MedicineWindow(QMainWindow):
    def save_medicine(self):
        # Get form data
        data = self.get_form_data()

        # Delegate to service
        self.medicine_service.add_medicine(data)
```

### 2. Error Handling

```python
# ✅ Good
try:
    result = self.medicine_service.add_medicine(data)
    QMessageBox.information(self, "Success", MSG_SUCCESS_SAVE)
except ValueError as e:
    QMessageBox.warning(self, "Validation Error", str(e))
except DatabaseError as e:
    QMessageBox.critical(self, "Database Error", MSG_ERROR_SAVE)
    logger.error(f"Database error: {e}")
```

### 3. Use Constants

```python
# ❌ Bad
if status == 'pending':
    ...

# ✅ Good
from src.utils.constants import PAYMENT_STATUS_PENDING

if status == PAYMENT_STATUS_PENDING:
    ...
```

### 4. Configuration

```python
# ❌ Bad
max_items = 50

# ✅ Good
from src.config import Settings

max_items = Settings.MAX_INVOICE_ITEMS
```

## Resources

- [PEP 8 Style Guide](https://pep8.org/)
- [Python Docstring Conventions](https://www.python.org/dev/peps/pep-0257/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)

## Questions?

Nếu có thắc mắc, vui lòng:
1. Đọc [ARCHITECTURE.md](ARCHITECTURE.md)
2. Tạo issue trên GitHub
3. Liên hệ maintainer

---

**Happy Coding!** 🚀
