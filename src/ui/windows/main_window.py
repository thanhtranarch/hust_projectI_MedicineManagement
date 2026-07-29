"""
Main application window - Dashboard and navigation hub
"""

from PyQt6.QtWidgets import QLabel, QTableWidgetItem
from PyQt6.QtCore import QTimer, Qt
from datetime import datetime

from src.ui.base import BaseWindow
from src.services import ReportService
from src.utils.constants import EXPIRY_WARNING_DAYS, URGENT_EXPIRY_DAYS
from src.utils.helpers import format_currency, format_date, format_time


class MainWindow(BaseWindow):
    """
    Main application window with dashboard and navigation

    Features:
    - Stock overview
    - Expiring medicines warning
    - Today's invoices
    - Navigation menu
    - Export reports
    """

    def __init__(self, context):
        """
        Initialize main window

        Args:
            context: Application context with logged-in user
        """
        super().__init__(context, 'main.ui', 'MediManager - Dashboard')

        # Services
        self.report_service = ReportService(context)

        # Setup UI components
        self._setup_status_bar()
        self._connect_menu_actions()
        self._connect_button_actions()
        self._setup_tables()

        # Load initial data
        self.load_stock_overview()
        self.load_outdate_warning()
        self.load_today_invoice()

    def _setup_status_bar(self):
        """Setup status bar with user info and time"""
        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: gray; font-size: 11px;")
        self.statusBar().addPermanentWidget(self.status_label)

        # Timer for status updates
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_status_info)
        self.status_timer.start(1000)  # Update every second
        self.update_status_info()

    def _connect_menu_actions(self):
        """Connect menu bar actions"""
        self.actionSupplier.triggered.connect(self.goto_supplier)
        self.actionMedicine.triggered.connect(self.goto_medicine)
        self.actionStock.triggered.connect(self.goto_stock)
        self.actionCustomer.triggered.connect(self.goto_customer)
        self.actionStaff.triggered.connect(self.goto_staff)
        self.actionInvoice.triggered.connect(self.goto_invoice)
        self.actionLog_out.triggered.connect(self.goto_login)
        self.actionLogs.triggered.connect(self.goto_logs)

    def _connect_button_actions(self):
        """Connect button click actions"""
        self.export_report.clicked.connect(self.show_report_dialog)
        self.stock_detail.clicked.connect(self.goto_medicine)
        self.warning_detail.clicked.connect(self.goto_medicine)
        self.invoice_detail.clicked.connect(self.goto_invoice)
        self.invoice_create.clicked.connect(self.show_create_invoice)
        self.invoice_daily.cellClicked.connect(self.handle_invoice_detail_click)

    def _setup_tables(self):
        """Setup table sorting"""
        self.outdate_medicine.setSortingEnabled(True)
        self.stock_medicine.setSortingEnabled(True)
        self.invoice_daily.setSortingEnabled(True)

    def update_status_info(self):
        """Update status bar with current info"""
        current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        user_id = self.context.staff_id or "Unknown"
        self.status_label.setText(f"User: {user_id} | {current_time}")

    @staticmethod
    def _fill_table(table, rows):
        """Fill a table with pre-formatted strings, one tuple per row."""
        table.setSortingEnabled(False)
        table.setRowCount(len(rows))

        for row_idx, values in enumerate(rows):
            for col_idx, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row_idx, col_idx, item)

        table.setSortingEnabled(True)

    def load_stock_overview(self):
        """Load stock overview table"""
        try:
            self.db.execute("""
                SELECT medicine_id, medicine_name, unit, stock_quantity,
                       batch_number, sale_price
                FROM medicine
                ORDER BY medicine_name
            """)
            self._fill_table(self.stock_medicine, [
                (str(mid), name or '', unit or '', str(qty if qty is not None else 0),
                 batch or '', format_currency(price))
                for mid, name, unit, qty, batch, price in self.db.fetchall()
            ])

        except Exception as e:
            self.show_error(f"Error loading stock overview: {e}")

    def load_outdate_warning(self):
        """Load expiring medicines warning table"""
        try:
            days_left = self.context.sql.days_until('expiration_date')
            self.db.execute(f"""
                SELECT medicine_id, medicine_name, stock_quantity, unit, batch_number,
                       expiration_date, {days_left} AS days_left
                FROM medicine
                WHERE expiration_date IS NOT NULL
                  AND {days_left} BETWEEN 0 AND {EXPIRY_WARNING_DAYS}
                ORDER BY expiration_date ASC
            """)
            self._fill_table(self.outdate_medicine, [
                (str(mid), name or '', str(qty if qty is not None else 0), unit or '',
                 batch or '', format_date(expiry), str(days),
                 self._expiry_status(days))
                for mid, name, qty, unit, batch, expiry, days in self.db.fetchall()
            ])

        except Exception as e:
            self.show_error(f"Error loading expiry warnings: {e}")

    @staticmethod
    def _expiry_status(days_left):
        """Severity marker matching the legend shown under the table."""
        if days_left is None:
            return ''
        return '!' if days_left <= URGENT_EXPIRY_DAYS else '⚠'

    def load_today_invoice(self):
        """Load today's invoices"""
        try:
            self.db.execute(f"""
                SELECT i.invoice_id, i.invoice_date, c.customer_name,
                       i.total_amount, i.staff_id, i.payment_status
                FROM invoice i
                LEFT JOIN customer c ON i.customer_id = c.customer_id
                WHERE {self.context.sql.date_of('i.invoice_date')} = {self.context.sql.today}
                ORDER BY i.invoice_date DESC
            """)
            self._fill_table(self.invoice_daily, [
                (str(inv_id), format_time(dt), customer or 'Khách lẻ',
                 format_currency(total), staff or '', status or '')
                for inv_id, dt, customer, total, staff, status in self.db.fetchall()
            ])

        except Exception as e:
            self.show_error(f"Error loading today's invoices: {e}")

    def refresh_data(self):
        """Refresh all dashboard data"""
        self.load_stock_overview()
        self.load_outdate_warning()
        self.load_today_invoice()

    # Navigation methods
    def goto_supplier(self):
        """Navigate to supplier management"""
        from src.ui.windows.supplier_window import SupplierWindow
        self.supplier_window = SupplierWindow(self.context)
        self.supplier_window.show()
        self.close()

    def goto_medicine(self):
        """Navigate to medicine management"""
        from src.ui.windows.medicine_window import MedicineWindow
        self.medicine_window = MedicineWindow(self.context)
        self.medicine_window.show()
        self.close()

    def goto_stock(self):
        """Navigate to stock management"""
        from src.ui.windows.stock_window import StockWindow
        self.stock_window = StockWindow(self.context)
        self.stock_window.show()
        self.close()

    def goto_customer(self):
        """Navigate to customer management"""
        from src.ui.windows.customer_window import CustomerWindow
        self.customer_window = CustomerWindow(self.context)
        self.customer_window.show()
        self.close()

    def goto_staff(self):
        """Navigate to staff management"""
        from src.ui.windows.staff_window import StaffWindow
        self.staff_window = StaffWindow(self.context)
        self.staff_window.show()
        self.close()

    def goto_invoice(self):
        """Navigate to invoice management"""
        from src.ui.windows.invoice_window import InvoiceWindow
        self.invoice_window = InvoiceWindow(self.context)
        self.invoice_window.show()
        self.close()

    def goto_logs(self):
        """Navigate to activity logs"""
        from src.ui.windows.logs_window import LogsWindow
        self.logs_window = LogsWindow(self.context)
        self.logs_window.show()
        self.close()

    def goto_login(self):
        """Logout and return to login"""
        if self.confirm_action("Are you sure you want to logout?"):
            self.log_action("Đăng xuất hệ thống")

            from src.ui.dialogs.login_dialog import LoginDialog
            self.login_window = LoginDialog(self.context)
            self.login_window.show()
            self.close()

    def show_report_dialog(self):
        """Show report export dialog"""
        from src.ui.dialogs.report_dialog import ReportDialog
        ReportDialog(self.context, self).exec()

    def show_create_invoice(self):
        """Show create invoice dialog"""
        from src.ui.dialogs.create_invoice_dialog import CreateInvoiceDialog
        dialog = CreateInvoiceDialog(self.context, parent=self)
        if dialog.exec():
            # Refresh today's invoice data
            self.load_today_invoice()

    def handle_invoice_detail_click(self, row, col):
        """Handle invoice detail click"""
        from src.ui.dialogs.invoice_information_dialog import InvoiceInformationDialog
        invoice_id = self.invoice_daily.item(row, 0).text()
        dialog = InvoiceInformationDialog(self.context, invoice_id, self)
        dialog.exec()
