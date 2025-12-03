"""
Main application windows
"""

from .main_window import MainWindow
from .supplier_window import SupplierWindow
from .customer_window import CustomerWindow
from .staff_window import StaffWindow
from .medicine_window import MedicineWindow
from .invoice_window import InvoiceWindow
from .stock_window import StockWindow
from .logs_window import LogsWindow

__all__ = [
    'MainWindow',
    'SupplierWindow',
    'CustomerWindow',
    'StaffWindow',
    'MedicineWindow',
    'InvoiceWindow',
    'StockWindow',
    'LogsWindow',
]
