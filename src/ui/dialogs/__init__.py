"""
Dialog windows for various operations
"""

from .login_dialog import LoginDialog
from .register_dialog import RegisterDialog
from .supplier_information_dialog import SupplierInformationDialog
from .customer_information_dialog import CustomerInformationDialog
from .staff_information_dialog import StaffInformationDialog
from .medicine_information_dialog import MedicineInformationDialog
from .medicine_add_dialog import MedicineAddDialog
from .invoice_information_dialog import InvoiceInformationDialog
from .create_invoice_dialog import CreateInvoiceDialog
from .stock_information_dialog import StockInformationDialog
from .create_stock_dialog import CreateStockDialog
from .report_dialog import ReportDialog

__all__ = [
    'LoginDialog',
    'RegisterDialog',
    'SupplierInformationDialog',
    'CustomerInformationDialog',
    'StaffInformationDialog',
    'MedicineInformationDialog',
    'MedicineAddDialog',
    'InvoiceInformationDialog',
    'CreateInvoiceDialog',
    'StockInformationDialog',
    'CreateStockDialog',
    'ReportDialog',
]
