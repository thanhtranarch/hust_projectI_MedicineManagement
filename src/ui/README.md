# UI Module - Quick Reference

## Overview

This module contains all user interface components refactored from the legacy `MediManager.py` monolithic file.

## Structure

```
src/ui/
├── base/                   # Base classes
│   ├── base_window.py      # BaseWindow for QMainWindow
│   └── base_dialog.py      # BaseDialog for QDialog
│
├── windows/                # Main application windows
│   ├── main_window.py      # Dashboard
│   ├── supplier_window.py  # Supplier management
│   ├── customer_window.py  # Customer management
│   ├── staff_window.py     # Staff management
│   ├── medicine_window.py  # Medicine management
│   ├── invoice_window.py   # Invoice management
│   ├── stock_window.py     # Stock management
│   └── logs_window.py      # Activity logs
│
├── dialogs/                # Dialog windows
│   ├── login_dialog.py     # Login
│   ├── register_dialog.py  # Registration
│   ├── report_dialog.py    # Report export options
│   ├── supplier_information_dialog.py
│   ├── customer_information_dialog.py
│   ├── staff_information_dialog.py
│   ├── medicine_information_dialog.py
│   ├── medicine_add_dialog.py
│   ├── invoice_information_dialog.py
│   ├── create_invoice_dialog.py
│   ├── stock_information_dialog.py
│   └── create_stock_dialog.py
│
└── forms/                  # Qt Designer .ui files
    └── *.ui
```

## Quick Start

### Creating a New Window

```python
from src.ui.base import BaseWindow

class MyWindow(BaseWindow):
    def __init__(self, context):
        super().__init__(context, 'my_window.ui', 'My Window Title')

        # Connect UI elements
        self.save_btn.clicked.connect(self.save_data)

        # Load data
        self.load_data()

    def load_data(self):
        # Load logic here
        pass
```

### Creating a New Dialog

```python
from src.ui.base import BaseDialog

class MyDialog(BaseDialog):
    def __init__(self, context, item_id, parent=None):
        super().__init__(context, 'my_dialog.ui', 'Dialog Title', parent)

        self.item_id = item_id
        self.load_data()

    def load_data(self):
        # Load logic here
        pass
```

## Common Patterns

### Table with Search

```python
def load_data(self):
    sql = "SELECT * FROM table_name"
    self.db.execute(sql)
    results = self.db.fetchall()

    self.tableWidget.setRowCount(len(results))
    # ... populate table ...

def search_data(self):
    keyword = self.search_input.text().lower()
    for row in range(self.tableWidget.rowCount()):
        item = self.tableWidget.item(row, 1)
        match = keyword in item.text().lower()
        self.tableWidget.setRowHidden(row, not match)
```

### Edit/View Mode Toggle

```python
def toggle_edit_mode(self):
    self.edit_mode = not self.edit_mode

    # Toggle fields
    self.field_name.setReadOnly(not self.edit_mode)

    # Change button
    self.btn.setText("Save" if self.edit_mode else "Edit")

    if self.edit_mode:
        # Store original data
        self.original_data = self.get_form_data()
    else:
        # Save data
        self.save_data()
```

### Navigation

```python
def goto_main(self):
    from src.ui.windows.main_window import MainWindow
    self.main_window = MainWindow(self.context)
    self.main_window.show()
    self.close()
```

## Utility Methods (from Base Classes)

### Messages

```python
self.show_success("Operation successful!")
self.show_error("An error occurred")
self.show_warning("Warning message")
```

### Confirmation

```python
if self.confirm_action("Delete this item?"):
    # Proceed with deletion
    pass
```

### Logging

```python
self.log_action("User performed action X")
```

## Best Practices

1. **Always inherit from base classes** - Don't create standalone QMainWindow/QDialog
2. **Use constants** - Import from `src.utils.constants`
3. **Validate input** - Use helpers from `src.utils.helpers`
4. **Error handling** - Always use try/except for database operations
5. **Log actions** - Log important user actions
6. **Refresh data** - Refresh parent window after dialog closes

## Common Issues

### Issue: UI file not found
**Solution**: Make sure UI file is in `src/ui/forms/` and filename is correct

### Issue: Icon not showing
**Solution**: Icons should be in `assets/icons/`

### Issue: Database error
**Solution**: Always check `.env` configuration and use parameterized queries

---

For more details, see [ARCHITECTURE.md](../../docs/ARCHITECTURE.md) and [UI_REFACTORING.md](../../docs/UI_REFACTORING.md)
