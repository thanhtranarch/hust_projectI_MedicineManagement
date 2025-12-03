"""
Main application window - Dashboard and navigation hub
"""

from PyQt6.QtWidgets import QLabel, QTableWidgetItem, QMessageBox
from PyQt6.QtCore import QTimer, Qt
from datetime import datetime

from src.ui.base import BaseWindow
from src.services import ReportService


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

    def load_stock_overview(self):
        """Load stock overview table"""
        try:
            sql = """
                SELECT medicine_id, medicine_name, unit, stock_quantity, batch_number, sale_price
                FROM medicine
                ORDER BY medicine_name
            """
            self.db.execute(sql)
            results = self.db.fetchall()

            self.stock_medicine.setRowCount(len(results))
            for row, data in enumerate(results):
                for col, value in enumerate(data):
                    item = QTableWidgetItem(str(value or ''))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.stock_medicine.setItem(row, col, item)

        except Exception as e:
            self.show_error(f"Error loading stock overview: {e}")

    def load_outdate_warning(self):
        """Load expiring medicines warning table"""
        try:
            sql = """
                SELECT medicine_name, stock_quantity, unit, batch_number, expiration_date,
                       (expiration_date::date - CURRENT_DATE) AS days_left
                FROM medicine
                WHERE (expiration_date::date - CURRENT_DATE) <= 60
                  AND (expiration_date::date - CURRENT_DATE) >= 0
                ORDER BY expiration_date ASC
            """
            self.db.execute(sql)
            results = self.db.fetchall()

            self.outdate_medicine.setRowCount(len(results))
            for row, data in enumerate(results):
                for col, value in enumerate(data):
                    item = QTableWidgetItem(str(value or ''))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.outdate_medicine.setItem(row, col, item)

        except Exception as e:
            self.show_error(f"Error loading expiry warnings: {e}")

    def load_today_invoice(self):
        """Load today's invoices"""
        try:
            sql = """
                SELECT invoice_id, invoice_date, customer_id, total_amount, staff_id, payment_status
                FROM invoice
                WHERE DATE(invoice_date) = CURRENT_DATE
                ORDER BY invoice_date DESC
            """
            self.db.execute(sql)
            results = self.db.fetchall()

            self.invoice_daily.setRowCount(len(results))
            for row, data in enumerate(results):
                for col, value in enumerate(data):
                    item = QTableWidgetItem(str(value or ''))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.invoice_daily.setItem(row, col, item)

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
        # TODO: Complete MedicineWindow refactoring
        self.show_warning("Medicine management - Refactoring in progress...")

    def goto_stock(self):
        """Navigate to stock management"""
        # TODO: Complete StockWindow refactoring
        self.show_warning("Stock management - Refactoring in progress...")

    def goto_customer(self):
        """Navigate to customer management"""
        # TODO: Complete CustomerWindow refactoring
        self.show_warning("Customer management - Refactoring in progress...")

    def goto_staff(self):
        """Navigate to staff management"""
        # TODO: Complete StaffWindow refactoring
        self.show_warning("Staff management - Refactoring in progress...")

    def goto_invoice(self):
        """Navigate to invoice management"""
        # TODO: Complete InvoiceWindow refactoring
        self.show_warning("Invoice management - Refactoring in progress...")

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
        dialog = ReportDialog(self.context, self)

        # Show quick menu for report type
        from PyQt6.QtWidgets import QMenu
        menu = QMenu(self)
        menu.addAction("Stock Report", dialog.export_stock_report)
        menu.addAction("Invoice Report (Today)", dialog.export_invoice_report)
        menu.addAction("Expiry Warning", dialog.export_expiry_report)
        menu.exec(self.export_report.mapToGlobal(self.export_report.rect().bottomLeft()))

    def show_create_invoice(self):
        """Show create invoice dialog"""
        # TODO: Import and show CreateInvoiceDialog
        self.show_warning("Create invoice - Coming soon!")

    def handle_invoice_detail_click(self, row, col):
        """Handle invoice detail click"""
        # TODO: Show invoice details
        invoice_id = self.invoice_daily.item(row, 0).text()
        self.show_warning(f"Invoice details for ID: {invoice_id} - Coming soon!")
