"""
Main application windows
"""

from .main_window import MainWindow
from .supplier_window import SupplierWindow
from .logs_window import LogsWindow

# TODO: Add remaining windows as they are refactored
# from .customer_window import CustomerWindow
# from .staff_window import StaffWindow
# from .medicine_window import MedicineWindow
# from .invoice_window import InvoiceWindow
# from .stock_window import StockWindow

__all__ = [
    'MainWindow',
    'SupplierWindow',
    'LogsWindow',
]
