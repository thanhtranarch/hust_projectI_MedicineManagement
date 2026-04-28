from PyQt6.QtWidgets import QMainWindow, QLabel
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QDateTime, QTimer

from utils.helpers import load_ui_file
from constants import ICON_PATH


class MainWindow(QMainWindow):
    def __init__(self, context):
        super().__init__()
        self.context = context
        load_ui_file(self, 'main.ui')
        self.setWindowTitle("MediManager")
        self.setWindowIcon(QIcon(ICON_PATH))
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: gray; font-size: 11px;")
        self.statusBar().addPermanentWidget(self.status_label)

        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_status_info)
        self.status_timer.start(1000)
        self.update_status_info()

        self.actionSupplier.triggered.connect(self.goto_supplier)
        self.actionMedicine.triggered.connect(self.goto_medicine)
        self.actionStock.triggered.connect(self.goto_stock)
        self.actionCustomer.triggered.connect(self.goto_customer)
        self.actionStaff.triggered.connect(self.goto_staff)
        self.actionInvoice.triggered.connect(self.goto_invoice)
        self.actionLogs.triggered.connect(self.goto_logs)
        self.actionLog_out.triggered.connect(self.goto_login)

        self.export_report.clicked.connect(self.show_report_dialog)
        self.invoice_create.clicked.connect(self.show_create_invoice)

        self.load_stock_overview()
        self.load_outdate_warning()
        self.load_today_invoice()

    def update_status_info(self):
        now = QDateTime.currentDateTime().toString("HH:mm:ss - dd/MM/yyyy")
        status = f"👤 {self.context.staff_id}   | 🕒 {now}   | ✅ Database Connected"
        self.status_label.setText(status)

    def show_report_dialog(self):
        from screens.report_dialog import ReportDialog
        dialog = ReportDialog(self.context)
        dialog.exec()

    def show_create_invoice(self):
        from screens.invoice_screen import CreateInvoiceDialog
        dialog = CreateInvoiceDialog(self.context)
        dialog.exec()

    def load_stock_overview(self):
        db = self.context.db_manager
        query = "SELECT medicine_id, medicine_name, unit, stock_quantity, batch_number, sale_price FROM medicine"
        db.execute(query)
        results = db.fetchall()

        self.stock_medicine.setRowCount(len(results))
        for row, data in enumerate(results):
            for col, value in enumerate(data):
                item = self._create_centered_item(value)
                self.stock_medicine.setItem(row, col, item)
        self.stock_medicine.setColumnWidth(1, 200)
        self.stock_medicine.setColumnWidth(4, 200)

    def load_outdate_warning(self):
        db = self.context.db_manager
        query = """
            SELECT medicine_id, medicine_name, stock_quantity, unit, batch_number, expiration_date,
                   DATEDIFF(expiration_date, NOW()) AS days_left,
                   CASE
                       WHEN DATEDIFF(expiration_date, NOW()) <= 30 THEN '❗'
                       WHEN DATEDIFF(expiration_date, NOW()) <= 60 THEN '⚠'
                   END AS status
            FROM medicine
            WHERE DATEDIFF(expiration_date, NOW()) <= 60
            ORDER BY expiration_date ASC
        """
        db.execute(query)
        results = db.fetchall()

        self.outdate_medicine.setRowCount(len(results))
        for row, data in enumerate(results):
            for col, value in enumerate(data):
                item = self._create_centered_item(value)
                self.outdate_medicine.setItem(row, col, item)
        self.outdate_medicine.setColumnWidth(1, 200)
        self.outdate_medicine.setColumnWidth(5, 150)
        self.outdate_medicine.setColumnWidth(7, 50)

    def load_today_invoice(self):
        db = self.context.db_manager
        query = """
            SELECT invoice_id, invoice_date, customer_id, total_amount, staff_id, payment_status
            FROM invoice WHERE DATE(invoice_date) = CURDATE()
        """
        db.execute(query)
        results = db.fetchall()

        column_labels = ["Mã HĐ", "Ngày lập", "Khách hàng", "Tổng tiền", "Nhân viên", "Trạng thái", "Chi tiết"]
        self.invoice_daily.setRowCount(len(results))
        self.invoice_daily.setColumnCount(len(column_labels))
        self.invoice_daily.setHorizontalHeaderLabels(column_labels)

        for row, data in enumerate(results):
            for col, value in enumerate(data):
                item = self._create_centered_item(value)
                self.invoice_daily.setItem(row, col, item)
            detail_item = QTableWidgetItem("View Details")
            font = QFont()
            font.setUnderline(True)
            detail_item.setFont(font)
            detail_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            detail_item.setData(Qt.ItemDataRole.UserRole, data[0])
            detail_item.setToolTip("Click để xem chi tiết hóa đơn")
            self.invoice_daily.setItem(row, len(data), detail_item)

        self.invoice_daily.cellClicked.connect(self.handle_invoice_detail_click)

    def handle_invoice_detail_click(self, row, column):
        if column == self.invoice_daily.columnCount() - 1:
            item = self.invoice_daily.item(row, column)
            if item:
                invoice_id = item.data(Qt.ItemDataRole.UserRole)
                if invoice_id:
                    from screens.invoice_screen import InvoiceDetailDialog
                    dialog = InvoiceDetailDialog(self.context, invoice_id)
                    dialog.exec()

    def _create_centered_item(self, value):
        item = QTableWidgetItem(str(value))
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item

    def goto_supplier(self):
        from screens.supplier_screen import SupplierWindow
        self._open_screen(SupplierWindow)

    def goto_medicine(self):
        from screens.medicine_screen import MedicineWindow
        self._open_screen(MedicineWindow)

    def goto_stock(self):
        from screens.stock_screen import StockWindow
        self._open_screen(StockWindow)

    def goto_customer(self):
        from screens.customer_screen import CustomerWindow
        self._open_screen(CustomerWindow)

    def goto_staff(self):
        from screens.staff_screen import StaffWindow
        self._open_screen(StaffWindow)

    def goto_invoice(self):
        from screens.invoice_screen import InvoiceWindow
        self._open_screen(InvoiceWindow)

    def goto_logs(self):
        from screens.logs_screen import LogsWindow
        self._open_screen(LogsWindow)

    def goto_login(self):
        from screens.auth_screen import AuthDialog
        self.auth_window = AuthDialog(self.context)
        self.auth_window.show()
        self.close()

    def _open_screen(self, screen_class):
        self.new_window = screen_class(self.context)
        self.new_window.show()
        self.close()
