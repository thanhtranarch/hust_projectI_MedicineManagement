from PyQt6 import QtCore, QtWidgets, QtGui, uic
from PyQt6.QtWidgets import *
from PyQt6.uic import loadUi
from PyQt6.QtGui import QIcon, QFont, QBrush, QColor
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import *
from datetime import datetime
from DBManager import DBManager
import sys
import MySQLdb as mysql_db
import os
import darkdetect
import bcrypt 
from export_reports import export_stock_report, export_invoice_report, export_expiry_warning_report

# Connect to DataBase - Done
class AppContext:
    def __init__(self, staff_id = None):
        self.staff_id = staff_id
        self.db_manager = DBManager()
        self.connection = self.db_manager.connect()
    def __del__(self):
        self.db_manager.close()

# Main Window
class Main_w(QMainWindow):  
    def __init__(self, context, staff_id=None):
        super(Main_w, self).__init__()
        ui_path = os.path.join(current_dir, 'ui', 'main.ui')
        print(">>> main.ui path:", ui_path)
        if not os.path.exists(ui_path):
            raise FileNotFoundError(f"Không tìm thấy UI file: {ui_path}")
        uic.loadUi(ui_path, self)
        self.setWindowTitle("MediManager")
        self.setWindowIcon(QtGui.QIcon(icon_path))
        self.context = context
        self.staff_id = staff_id

        # Load UI file
        ui_path = os.path.join(current_dir, 'ui', 'main.ui')
        print(">>> main.ui path:", ui_path)
        if not os.path.exists(ui_path):
            raise FileNotFoundError(f"Không tìm thấy UI file: {ui_path}")
        uic.loadUi(ui_path, self)

        # Setup window properties
        self.setWindowTitle("MediManager")
        self.setWindowIcon(QtGui.QIcon(icon_path))
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # Status bar setup
        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: gray; font-size: 11px;")
        self.statusBar().addPermanentWidget(self.status_label)

        # Timer for status updates
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_status_info)
        self.status_timer.start(1000)  # Update every second
        self.update_status_info()  # Initial update

        # Connect menu actions
        self.actionSupplier.triggered.connect(self.goto_supplier)
        self.actionMedicine.triggered.connect(self.goto_medicine)
        self.actionStock.triggered.connect(self.goto_stock)
        self.actionCustomer.triggered.connect(self.goto_customer)
        self.actionStaff.triggered.connect(self.goto_staff)
        self.actionInvoice.triggered.connect(self.goto_invoice)
        self.actionLog_out.triggered.connect(self.goto_login)
        self.actionLogs.triggered.connect(self.goto_logs)
        self.load_stock_overview()
        self.load_outdate_warning()
        self.load_today_invoice()


        # Button click
        self.export_report.clicked.connect(self.show_report_dialog)
        self.stock_detail.clicked.connect(self.goto_medicine)
        self.warning_detail.clicked.connect(self.goto_medicine)
        self.invoice_detail.clicked.connect(self.goto_invoice)
        self.invoice_create.clicked.connect(self.show_create_invoice)
        self.invoice_daily.cellClicked.connect(self.handle_invoice_detail_click)

        # Sorting
        self.outdate_medicine.setSortingEnabled(True)
        self.stock_medicine.setSortingEnabled(True)
        self.invoice_daily.setSortingEnabled(True)

    def load_stock_overview(self):
        db = self.context.db_manager
        sql = """SELECT medicine_id, medicine_name, unit, stock_quantity, batch_number, sale_price FROM medicine"""
        db.execute(sql)
        results = db.fetchall()
        self.stock_medicine.setRowCount(len(results))
        for row, data in enumerate(results):
            for col, value in enumerate(data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.stock_medicine.setItem(row, col, item)

        self.stock_medicine.setColumnWidth(1, 200)  
        self.stock_medicine.setColumnWidth(4, 200)

    def load_outdate_warning(self):
        db = self.context.db_manager
        sql = """SELECT medicine_id, medicine_name, stock_quantity, unit, batch_number, expiration_date,
                DATEDIFF(expiration_date, NOW()) AS days_left,
                CASE
                  WHEN DATEDIFF(expiration_date, NOW()) <= 30 THEN '❗'
                  WHEN DATEDIFF(expiration_date, NOW()) <= 60 THEN '⚠'
                END AS status
                FROM medicine
                WHERE DATEDIFF(expiration_date, NOW()) <= 60
                ORDER BY expiration_date ASC
                """  
        db.execute(sql)
        results = db.fetchall()
        self.outdate_medicine.setRowCount(len(results))
        for row, data in enumerate(results):
            for col, value in enumerate(data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.outdate_medicine.setItem(row, col, item)
        self.outdate_medicine.setColumnWidth(1,200)
        self.outdate_medicine.setColumnWidth(5,150)
        self.outdate_medicine.setColumnWidth(7,50)
    def load_today_invoice(self):
        db = self.context.db_manager
        sql = """SELECT invoice_id, invoice_date, customer_id, total_amount, staff_id, payment_status
                FROM invoice WHERE DATE(invoice_date) = CURDATE()"""
        db.execute(sql)
        results = db.fetchall()

        column_labels = ["Mã HĐ", "Ngày lập", "Khách hàng", "Tổng tiền", "Nhân viên", "Trạng thái", "Chi tiết"]
        self.invoice_daily.setRowCount(len(results))
        self.invoice_daily.setColumnCount(len(column_labels))
        self.invoice_daily.setHorizontalHeaderLabels(column_labels)

        for row, data in enumerate(results):
            for col, value in enumerate(data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.invoice_daily.setItem(row, col, item)
            # Cột cuối cùng - View Details
            detail_item = QTableWidgetItem("View Details")
            font = QFont()
            font.setUnderline(True)
            detail_item.setFont(font)
            detail_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            detail_item.setData(Qt.ItemDataRole.UserRole, data[0])  # invoice_id
            detail_item.setToolTip("Click để xem chi tiết hóa đơn")
            self.invoice_daily.setItem(row, len(data), detail_item)


    def handle_invoice_detail_click(self, row, column):
        if column == self.invoice_daily.columnCount() - 1:
            item = self.invoice_daily.item(row, column)
            if item:
                invoice_id = item.data(Qt.ItemDataRole.UserRole)
                if invoice_id:
                    self.show_invoice_detail(invoice_id)

    def show_invoice_detail(self, invoice_id):
        print("Mở chi tiết hóa đơn:", invoice_id)
        dialog = InvoiceInformation_w(self.context, invoice_id)
        dialog.exec()


    
    def closeEvent(self, event):
        QApplication.quit()

    def goto_login(self):
        self.login_window = Login_w(self.context)
        self.login_window.show()
        self.hide()

    def goto_supplier(self):
        self.supplier_window = Supplier_w(self.context)
        self.supplier_window.show()
        self.hide()

    def goto_medicine(self):
        self.medicine_window = Medicine_w(self.context)
        self.medicine_window.show()
        self.hide()

    def goto_customer(self):
        self.customer_window = Customer_w(self.context)
        self.customer_window.show()
        self.hide()

    def goto_stock(self):
        self.stock_window = Stock_w(self.context)
        self.stock_window.show()
        self.hide()

    def goto_staff(self):
        self.staff_window = Staff_w(self.context)
        self.staff_window.show()
        self.hide()

    def goto_invoice(self):
        self.invoice_window = Invoice_w(self.context)
        self.invoice_window.show()
        self.hide()

    def goto_logs(self):
        self.logs_window = Logs_w(self.context)
        self.logs_window.show()
        self.hide()

    def show_report_dialog(self):
        dialog = ReportDialog_w(self.context)
        dialog.exec()

    def show_create_invoice(self):
        dialog = CreateInvoiceDialog_w(self.context)
        dialog.exec()

    def show_invoice_detail(self, invoice_id):
        dialog = InvoiceInformation_w(self.context, invoice_id)
        dialog.exec()

    def update_status_info(self):
        now = datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
        status = f"👤 {self.staff_id}   | 🕒 {now}   | ✅ Database Connected"
        self.status_label.setText(status)

# ReportDialog        
class ReportDialog_w(QDialog):
    def __init__(self, context, parent=None):
        super().__init__(parent)
        self.context = context
        self.setWindowTitle("Xuất báo cáo")
        self.setWindowIcon(QtGui.QIcon(icon_path))
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        self.combo = QComboBox()
        self.combo.addItems([
            "Tổng tồn kho",
            "Hóa đơn trong ngày",
            "Thuốc sắp hết hạn"
        ])

        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)

        self.export_btn = QPushButton("Xuất PDF")
        self.export_btn.clicked.connect(self.export_report)

        layout.addWidget(QLabel("Chọn loại báo cáo:"))
        layout.addWidget(self.combo)
        layout.addWidget(QLabel("Chọn ngày (với hóa đơn):"))
        layout.addWidget(self.date_edit)
        layout.addWidget(self.export_btn)
        self.setLayout(layout)

    def export_report(self):
        report_type = self.combo.currentText()
        selected_date = self.date_edit.date().toString("yyyy-MM-dd")

        # Gợi ý tên file dựa trên loại báo cáo
        if report_type == "Tổng tồn kho":
            default_name = f"report_stock_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        elif report_type == "Hóa đơn trong ngày":
            default_name = f"report_invoice_{selected_date}.pdf"
        elif report_type == "Thuốc sắp hết hạn":
            default_name = f"report_expiring_meds_{datetime.now().strftime('%Y%m%d')}.pdf"
        else:
            default_name = "report.pdf"

        filepath, _ = QFileDialog.getSaveFileName(self, "Chọn vị trí lưu báo cáo", default_name, "PDF Files (*.pdf)")
        if not filepath:
            return

        try:
            # Import các hàm export bên ngoài, hoặc import ở đầu file chính
            from export_reports import (
                export_stock_report, export_invoice_report, export_expiry_warning_report
            )

            if report_type == "Tổng tồn kho":
                file_path = export_stock_report(self.context, filepath)
                log_content = f"Xuất báo cáo tồn kho: {file_path}"
            elif report_type == "Hóa đơn trong ngày":
                file_path = export_invoice_report(self.context, selected_date, filepath)
                log_content = f"Xuất báo cáo hóa đơn ngày {selected_date}: {file_path}"
            elif report_type == "Thuốc sắp hết hạn":
                file_path = export_expiry_warning_report(self.context, filepath)
                log_content = f"Xuất báo cáo thuốc sắp hết hạn: {file_path}"
            self.context.db_manager.log_action(self.context.staff_id, log_content)
            QMessageBox.information(self, "Thành công", f"Đã xuất file:\n{file_path}")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể xuất báo cáo: {e}")

# Supplier Window
class Supplier_w(QMainWindow):
    def __init__(self, context):
        super(Supplier_w, self).__init__()
        self.context = context
        # Load UI file
        ui_path = os.path.join(current_dir, 'ui', 'supplier.ui')
        print(">>> supplier.ui path:", ui_path)
        if not os.path.exists(ui_path):
            raise FileNotFoundError(f"Không tìm thấy UI file: {ui_path}")
        uic.loadUi(ui_path, self)

        # Setup window properties
        self.setWindowTitle("Supplier Management")
        self.setWindowIcon(QtGui.QIcon(icon_path))

        # Initialize UI components and data
        self.load_supplier_data()
        self.back_button.clicked.connect(self.goto_main)
        self.tableWidget.setSortingEnabled(True)
        self.search_input.textChanged.connect(self.search_supplier)

    def load_supplier_data(self):
        try:
            db = self.context.db_manager
            sql = """SELECT supplier_id, supplier_name, created_at, updated_at FROM supplier"""
            db.execute(sql)
            results = db.fetchall()

            # Configure table
            self.tableWidget.setRowCount(len(results))
            self.tableWidget.setColumnCount(len(db.execute(sql).description)+1)
            self.tableWidget.setColumnHidden(0, True)
            self.tableWidget.setColumnWidth(1, 300)  
            self.tableWidget.setColumnWidth(2, 150) 
            self.tableWidget.setColumnWidth(3, 150) 
            self.tableWidget.setColumnWidth(4, 200) 
            self.tableWidget.cellClicked.connect(self.handle_cell_click)

            column_count = self.tableWidget.columnCount()

            # Populate table data
            for row_idx, row_data in enumerate(results):
                supplier_id = row_data[0]  # Store for UserRole

                for col_idx in range(column_count):
                    if col_idx < len(row_data):
                        value = row_data[col_idx]
                        item = QTableWidgetItem(str(value))

                        # Format supplier name column
                        if col_idx == 1:
                            font = QFont()
                            font.setBold(True)
                            font.setUnderline(True)
                            item.setFont(font)
                            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                            item.setToolTip("Click để xem chi tiết nhà cung cấp")
                            item.setData(Qt.ItemDataRole.UserRole, supplier_id)
                        elif col_idx == 0:
                            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                        self.tableWidget.setItem(row_idx, col_idx, item)
                    else:
                        # Add "View Details" column
                        detail_item = QTableWidgetItem("View Details")
                        font = QFont()
                        font.setUnderline(True)
                        detail_item.setFont(font)
                        detail_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        detail_item.setData(Qt.ItemDataRole.UserRole, supplier_id)
                        detail_item.setToolTip("Click để xem chi tiết nhà cung cấp")
                        self.tableWidget.setItem(row_idx, col_idx, detail_item)
        except Exception as e:
            print("Lỗi khi tải dữ liệu:", e)

    def search_supplier(self):
        keyword = self.search_input.text().strip().lower()
        for row in range(self.tableWidget.rowCount()):
            name_item = self.tableWidget.item(row, 1)  # Supplier name column
            if name_item:
                name_text = name_item.text().lower()
                match = keyword in name_text
                self.tableWidget.setRowHidden(row, not match)

    def show_supplier_detail(self, supplier_id):
        detail_dialog = SupplierInformation_w(self.context, supplier_id)
        detail_dialog.exec()
    
    def handle_cell_click(self, row, column):
        if column == 1 or column == 4:
            item = self.tableWidget.item(row, column)
            if item is None:
                print("Item not found")
                return
            supplier_id = item.data(Qt.ItemDataRole.UserRole)
            if supplier_id:
                print(f"Opening details for supplier ID: {supplier_id}")
                self.show_supplier_detail(supplier_id)

    def goto_main(self):
        self.main_window = Main_w(self.context)
        self.main_window.show()
        self.hide()

class SupplierInformation_w(QDialog):
    def __init__(self, context, supplier_id):
        super(SupplierInformation_w, self).__init__()
        self.context = context
        self.supplier_id_value = supplier_id

        # Load UI
        ui_path = os.path.join(current_dir, 'ui', 'supplier_information.ui')
        print(">>> supplier_information.ui' path:", ui_path)
        if not os.path.exists(ui_path):
            raise FileNotFoundError(f"Không tìm thấy UI file: {ui_path}")
        uic.loadUi(ui_path, self)

        # Setup window and components
        self.setWindowTitle("Supplier Management")
        self.setWindowIcon(QtGui.QIcon(icon_path))
        self.edit_mode = False
        self.pushButton.clicked.connect(self.toggle_edit_mode)
        self.load_supplier_data(self.supplier_id_value)
        
    def load_supplier_data(self, supplier_id_value):
        try:
            db = self.context.db_manager
            sql = """SELECT supplier_id, supplier_name, supplier_address,
                            contact_name, contact_phone, contact_email, payment_terms 
                        FROM supplier WHERE supplier_id = %s"""
            db.execute(sql, (supplier_id_value,))
            result = db.fetchone()

            if result:
                # Populate form fields
                self.supplier_id.setText(str(result[0]))
                self.supplier_id.setReadOnly(True)
                self.supplier_name.setText(result[1] if result[1] else "")
                self.supplier_name.setReadOnly(True)
                self.supplier_address.setPlainText(result[2] if result[2] else "")
                self.supplier_address.setReadOnly(True)
                self.contact_name.setText(result[3] if result[3] else "")
                self.contact_name.setReadOnly(True)
                self.contact_phone.setText(result[4] if result[4] else "")
                self.contact_phone.setReadOnly(True)
                self.contact_email.setText(result[5] if result[5] else "")
                self.contact_email.setReadOnly(True)
                if result[6]:
                    self.comboBox_payment_terms.setCurrentText(result[6])
                    self.comboBox_payment_terms.setEnabled(False)
            else:
                QMessageBox.warning(self, "Thông báo", "Không tìm thấy thông tin nhà cung cấp.")
        except Exception as e:
            print("Lỗi khi tải dữ liệu chi tiết:", e)

    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode

        # Toggle form field editability
        self.supplier_name.setReadOnly(not self.edit_mode)
        self.supplier_address.setReadOnly(not self.edit_mode)
        self.contact_name.setReadOnly(not self.edit_mode)
        self.contact_phone.setReadOnly(not self.edit_mode)
        self.contact_email.setReadOnly(not self.edit_mode)
        self.comboBox_payment_terms.setEnabled(self.edit_mode)
        self.pushButton.setText("💾 Save" if self.edit_mode else "Edit...")

        if self.edit_mode:
            self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel)
            # Store original data for cancel operation
            self.original_data = {
                "name": self.supplier_name.text(),
                "address": self.supplier_address.toPlainText(),
                "contact": self.contact_name.text(),
                "phone": self.contact_phone.text(),
                "email": self.contact_email.text(),
                "payment": self.comboBox_payment_terms.currentText()
                }
            cancel_btn = self.buttonBox.button(QDialogButtonBox.StandardButton.Cancel)
            if cancel_btn:
                try:
                    cancel_btn.clicked.disconnect()
                except:
                    pass
                cancel_btn.clicked.connect(self.cancel_edit)
        else:
            self.save_supplier_data()
            self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Ok)

    def set_fields_editable(self, editable):
        self.supplier_id.setReadOnly(True)
        self.supplier_name.setReadOnly(not editable)
        self.supplier_address.setReadOnly(not editable)
        self.contact_name.setReadOnly(not editable)
        self.contact_phone.setReadOnly(not editable)
        self.contact_email.setReadOnly(not editable)
        self.comboBox_payment_terms.setEnabled(editable)

    def save_supplier_data(self):
        try:
            db = self.context.db_manager
            # Default to COD if payment terms empty
            payment = self.comboBox_payment_terms.currentText().strip() or "COD"
            sql = """UPDATE supplier SET
                    supplier_name = %s,
                    supplier_address = %s,
                    contact_name = %s,
                    contact_phone = %s,
                    contact_email = %s,
                    payment_terms = %s
                     WHERE supplier_id = %s"""
            values = (
                self.supplier_name.text(),
                self.supplier_address.toPlainText(),
                self.contact_name.text(),
                self.contact_phone.text(),
                self.contact_email.text(),
                payment,
                self.supplier_id.text()
            )

            db.execute(sql, values)
            db.commit()
            QMessageBox.information(self, "Thành công", "Đã lưu thông tin nhà cung cấp.")
            self.context.db_manager.log_action(self.context.staff_id, f"Cập nhật nhà cung cấp: {self.supplier_id.text()}")

        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể lưu: {e}")

    def cancel_edit(self):
        if self.edit_mode:
            # Restore original data
            self.supplier_name.setText(self.original_data["name"])
            self.supplier_address.setPlainText(self.original_data["address"])
            self.contact_name.setText(self.original_data["contact"])
            self.contact_phone.setText(self.original_data["phone"])
            self.contact_email.setText(self.original_data["email"])
           
            idx = self.comboBox_payment_terms.findText(self.original_data["payment"])
            if idx >= 0:
                self.comboBox_payment_terms.setCurrentIndex(idx)

            # Return to view mode
            self.edit_mode = False
            self.set_fields_editable(False)
            self.pushButton.setText("Edit...")
            self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Ok)
            QMessageBox.information(self, "Hủy chỉnh sửa", "Thay đổi đã được hủy.")
            self.context.db_manager.log_action(self.context.staff_id, f"Hủy chỉnh sửa nhà cung cấp: {self.supplier_id.text()}")


# Customer Window
class Customer_w(QMainWindow):
    def __init__(self, context):
        super(Customer_w, self).__init__()
        self.context = context
        ui_path = os.path.join(current_dir, 'ui', 'customer.ui')
        if not os.path.exists(ui_path):
            raise FileNotFoundError(f"Không tìm thấy UI file: {ui_path}")
        uic.loadUi(ui_path, self)

        self.setWindowTitle("Customer Management")
        self.setWindowIcon(QtGui.QIcon(icon_path))
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.back_button.clicked.connect(self.goto_main)
        self.tableWidget.cellClicked.connect(self.handle_cell_click)
        self.search_input.textChanged.connect(self.search_customer)
        self.tableWidget.setSortingEnabled(True)

        self.load_customer_data()

    def load_customer_data(self):
        try:
            db = self.context.db_manager
            sql = "SELECT customer_id, customer_name, customer_phone, customer_email FROM customer"
            db.execute(sql)
            results = db.fetchall()

            self.tableWidget.setRowCount(len(results))
            self.tableWidget.setColumnCount(5)
            self.tableWidget.setHorizontalHeaderLabels(["ID", "Name", "Phone", "Email", "Details"])
            self.tableWidget.setColumnHidden(0, True)

            for row_idx, row_data in enumerate(results):
                customer_id = row_data[0]
                # Các cột thông tin
                for col_idx in range(4):
                    item = QTableWidgetItem(str(row_data[col_idx]))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    # Cột Name (có thể click)
                    if col_idx == 1:
                        font = QFont()
                        font.setBold(True)
                        font.setUnderline(True)
                        item.setFont(font)
                        item.setData(Qt.ItemDataRole.UserRole, customer_id)
                        item.setToolTip("Click để xem chi tiết khách hàng")
                    self.tableWidget.setItem(row_idx, col_idx, item)
                # Cột Details cuối cùng
                detail_item = QTableWidgetItem("View Details")
                font = QFont()
                font.setUnderline(True)
                detail_item.setFont(font)
                detail_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                detail_item.setData(Qt.ItemDataRole.UserRole, customer_id)
                detail_item.setToolTip("Click để xem chi tiết khách hàng")
                self.tableWidget.setItem(row_idx, 4, detail_item)
        except Exception as e:
            print("Lỗi khi tải dữ liệu khách hàng:", e)

    def search_customer(self):
        keyword = self.search_input.text().strip().lower()
        for row in range(self.tableWidget.rowCount()):
            name_item = self.tableWidget.item(row, 1)
            if name_item:
                name_text = name_item.text().lower()
                match = keyword in name_text
                self.tableWidget.setRowHidden(row, not match)

    def handle_cell_click(self, row, column):
        # Cột Name (1) hoặc cột Details (4)
        if column == 1 or column == 4:
            item = self.tableWidget.item(row, column)
            if item is None:
                return
            customer_id = item.data(Qt.ItemDataRole.UserRole)
            if customer_id:
                self.show_customer_detail(customer_id)

    def show_customer_detail(self, customer_id):
        dialog = CustomerInformation_w(self.context, customer_id)
        dialog.exec()

    def goto_main(self):
        self.main_window = Main_w(self.context)
        self.main_window.show()
        self.hide()



class CustomerInformation_w(QDialog):
    def __init__(self, context, customer_id):
        super(CustomerInformation_w, self).__init__()
        self.context = context
        self.customer_id_value = customer_id

        # Load UI từ file .ui mới (PySide6/PyQt6 đều dùng được nếu đã sinh đúng class)
        ui_path = os.path.join(current_dir, 'ui', 'customer_information.ui')
        uic.loadUi(ui_path, self)

        self.setWindowTitle("Customer Information")
        self.setWindowIcon(QtGui.QIcon(icon_path))

        self.edit_mode = False
        # Button "Edit..." sẽ được add động vì UI không có sẵn
        self.edit_button = QPushButton("Edit...", self)
        self.edit_button.setGeometry(80, 445, 80, 28)
        self.edit_button.clicked.connect(self.toggle_edit_mode)
        self.edit_button.show()

        self.load_customer_data(self.customer_id_value)
        # Default: readonly
        self.set_fields_editable(False)

    def load_customer_data(self, customer_id):
        try:
            db = self.context.db_manager
            sql = """SELECT customer_id, customer_name, customer_phone, customer_email FROM customer WHERE customer_id = %s"""
            db.execute(sql, (customer_id,))
            result = db.fetchone()

            if result:
                self.customer_id.setText(str(result[0]))
                self.customer_name.setText(result[1])
                self.customer_phone.setText(result[2])
                self.customer_email.setText(result[3])
                self.set_fields_editable(False)
            else:
                QMessageBox.warning(self, "Thông báo", "Không tìm thấy khách hàng.")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể tải dữ liệu: {e}")

    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode
        self.set_fields_editable(self.edit_mode)
        self.edit_button.setText("💾 Save" if self.edit_mode else "Edit...")

        if self.edit_mode:
            # Lưu dữ liệu gốc để có thể Cancel
            self.original_data = {
                "name": self.customer_name.text(),
                "phone": self.customer_phone.text(),
                "email": self.customer_email.text()
            }
            self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel)
            cancel_btn = self.buttonBox.button(QDialogButtonBox.StandardButton.Cancel)
            if cancel_btn:
                try:
                    cancel_btn.clicked.disconnect()
                except:
                    pass
                cancel_btn.clicked.connect(self.cancel_edit)
        else:
            self.save_customer_data()
            self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Ok)

    def save_customer_data(self):
        try:
            sql = """UPDATE customer SET customer_name = %s, customer_phone = %s, customer_email = %s WHERE customer_id = %s"""
            values = (
                self.customer_name.text(),
                self.customer_phone.text(),
                self.customer_email.text(),
                self.customer_id.text()
            )
            self.context.db_manager.execute(sql, values)
            self.context.db_manager.commit()
            QMessageBox.information(self, "Thành công", "Đã cập nhật khách hàng.")
            self.context.db_manager.log_action(self.context.staff_id, f"Cập nhật khách hàng: {self.customer_id.text()}")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể cập nhật: {e}")

    def cancel_edit(self):
        self.customer_name.setText(self.original_data["name"])
        self.customer_phone.setText(self.original_data["phone"])
        self.customer_email.setText(self.original_data["email"])
        self.set_fields_editable(False)
        self.edit_mode = False
        self.edit_button.setText("Edit...")
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Ok)
        QMessageBox.information(self, "Đã hủy", "Chỉnh sửa đã được hủy.")

    def set_fields_editable(self, editable):
        self.customer_id.setReadOnly(True)
        self.customer_name.setReadOnly(not editable)
        self.customer_phone.setReadOnly(not editable)
        self.customer_email.setReadOnly(not editable)


# Staff Window - Done
class Staff_w(QMainWindow):
    def __init__(self, context):
        super(Staff_w, self).__init__()
        self.context = context
        ui_path = os.path.join(current_dir, 'ui', 'staff.ui')
        print(">>> staff.ui path:", ui_path)
        if not os.path.exists(ui_path):
            raise FileNotFoundError(f"Không tìm thấy UI file: {ui_path}")
        uic.loadUi(ui_path, self)
        self.setWindowTitle("Staff Management")
        self.setWindowIcon(QtGui.QIcon(icon_path))
        self.load_staff_data()
        self.back_button.clicked.connect(self.goto_main)
        self.tableWidget.setSortingEnabled(True)
        self.search_input.textChanged.connect(self.search_staff)

    def load_staff_data(self):
        try:
            db = self.context.db_manager
            sql= """SELECT staff_id, staff_name, staff_position, created_at, updated_at FROM staff"""
            db.execute(sql)
            results = db.fetchall()

            # Cập nhật TableWidget
            self.tableWidget.setRowCount(len(results))
            self.tableWidget.setColumnCount(len(db.execute(sql).description)+1)
            # self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
            self.tableWidget.setColumnWidth(0, 50)  
            self.tableWidget.setColumnWidth(1, 200)  
            self.tableWidget.setColumnWidth(2, 100) 
            self.tableWidget.setColumnWidth(3, 150) 
            self.tableWidget.setColumnWidth(4, 150) 
            self.tableWidget.setColumnWidth(5, 200) 
            self.tableWidget.cellClicked.connect(self.handle_cell_click)

            column_count = self.tableWidget.columnCount()

            for row_idx, row_data in enumerate(results):
                staff_id = row_data[0]  # Giữ lại để dùng UserRole

                for col_idx in range(column_count):
                    if col_idx < len(row_data):
                        value = row_data[col_idx]
                        item = QTableWidgetItem(str(value))

                        # Staff Name (hiển thị với underline)
                        if col_idx == 1 or col_idx == 2:
                            font = QFont()
                            item.setFont(font)
                            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                            item.setToolTip("Click để xem chi tiết nhân viên")
                            item.setData(Qt.ItemDataRole.UserRole, staff_id)

                        elif col_idx == 0:
                            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                        self.tableWidget.setItem(row_idx, col_idx, item)

                    else:
                        # Cột "View Details"
                        detail_item = QTableWidgetItem("View Details")
                        font = QFont()
                        font.setUnderline(True)
                        detail_item.setFont(font)
                        detail_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        detail_item.setData(Qt.ItemDataRole.UserRole, staff_id)
                        detail_item.setToolTip("Click để xem chi tiết nhân viên")
                        self.tableWidget.setItem(row_idx, col_idx, detail_item)
        except Exception as e:
            print("Lỗi khi tải dữ liệu:", e)
    
    def show_staff_detail(self, staff_id):
        detail_dialog = StaffInformation_w(self.context, staff_id)
        detail_dialog.exec()

    def search_staff(self):
        keyword = self.search_input.text().strip().lower()
        for row in range(self.tableWidget.rowCount()):
            name_item = self.tableWidget.item(row, 2)  # Staff name column
            if name_item:
                name_text = name_item.text().lower()
                match = keyword in name_text
                self.tableWidget.setRowHidden(row, not match)

    def handle_cell_click(self, row, column):
        if column == 1 or column == 5:
            item = self.tableWidget.item(row, column)
            if item is None:
                print("Item not found")
                return
            staff_id = item.data(Qt.ItemDataRole.UserRole)
            if staff_id:
                print(f"Opening details for staff ID: {staff_id}")
                self.show_staff_detail(staff_id)
    def goto_main(self):
        self.main_window = Main_w(self.context)
        self.main_window.show()
        self.hide()

class StaffInformation_w(QDialog):
    def __init__(self, context, staff_id):
        super(StaffInformation_w, self).__init__()
        self.context = context
        self.staff_id_value = staff_id
        ui_path = os.path.join(current_dir, 'ui', 'staff_information.ui')
        print(">>> staff_information.ui' path:", ui_path)
        if not os.path.exists(ui_path):
            raise FileNotFoundError(f"Không tìm thấy UI file: {ui_path}")
        uic.loadUi(ui_path, self)
        self.setWindowTitle("Staff Management")
        self.setWindowIcon(QtGui.QIcon(icon_path))
        self.load_staff_data(self.staff_id_value)
        

    def load_staff_data(self, staff_id_value):
        try:
            db = self.context.db_manager
            sql = """SELECT staff_name, staff_id, staff_position,
                            staff_phone, staff_email, staff_salary, hire_date FROM staff WHERE staff_id = %s"""
            db.execute(sql, (staff_id_value,))
            result = db.fetchone()
            # print(f"Query result: {result}")

            # Đổi lại các trường
            self.staff_id.setText(str(result[1]))
            self.staff_name.setText(result[0] if result[0] else "")
            self.staff_position.setText(result[2] if result[2] else "")
            self.staff_phone.setText(result[3] if result[3] else "")
            self.staff_email.setText(result[4] if result[4] else "")
            self.staff_salary.setText(str(result[5]) if result[5] else "")
            self.hire_date.setText(str(result[6]) if result[6] else "")
            self.hire_date.setReadOnly(True)
            self.staff_email.setText(result[4] if result[4] else "")
            self.staff_email.setReadOnly(True)
            self.staff_salary.setText(str(result[5]) if result[5] else "")
            self.staff_salary.setReadOnly(True)
            self.hire_date.setText(str(result[6]) if result[6] else "")
            self.hire_date.setReadOnly(True)
        except Exception as e:
            print("Lỗi khi tải dữ liệu:", e)

# Medicine Window - Done
class Medicine_w(QMainWindow):
    """Main window for medicine management."""
    def __init__(self, context):
        super(Medicine_w, self).__init__()
        self.context = context

        # Load UI
        ui_path = os.path.join(current_dir, 'ui', 'medicine.ui')
        print(f">>> medicine.ui path: {ui_path}")
        if not os.path.exists(ui_path):
            raise FileNotFoundError(f"Không tìm thấy UI file: {ui_path}")
        uic.loadUi(ui_path, self)

        # Set window properties
        self.setWindowTitle("Medicine Management")
        self.setWindowIcon(QIcon(icon_path))
        self.back_button.clicked.connect(self.goto_main)

        # Connect signals
        self.tableWidget.cellClicked.connect(self.handle_cell_click)
        self.tableWidget.setSortingEnabled(True)
        self.search_input.textChanged.connect(self.search_supplier)

        # Load initial data
        self.load_medicine_data()

    def load_medicine_data(self):
        """Load and display medicine data in the table."""
        try:
            sql = """
                SELECT m.medicine_id, m.medicine_name, c.category_name, m.created_at, m.updated_at
                FROM medicine m
                JOIN category c ON m.category_id = c.category_id
            """
            cursor = self.context.db_manager.execute(sql)
            results = cursor.fetchall()

            if not results:
                print("No medicine data found")
                return

            # Setup table
            self.tableWidget.setRowCount(len(results))
            column_count = len(cursor.description) + 1  # +1 for "View Details" column
            self.tableWidget.setColumnCount(column_count)

            self.tableWidget.setHorizontalHeaderLabels([
                "ID", "Name", "Category", "Created At", "Updated At", "Details"
            ])

            # Set column widths
            self.tableWidget.setColumnWidth(0, 50)
            self.tableWidget.setColumnWidth(1, 200)
            self.tableWidget.setColumnWidth(2, 150)
            self.tableWidget.setColumnWidth(3, 150)
            self.tableWidget.setColumnWidth(4, 150)
            self.tableWidget.setColumnWidth(5, 150)

            # Populate table
            for row_idx, row_data in enumerate(results):
                medicine_id = row_data[0]

                for col_idx in range(column_count):
                    if col_idx < len(row_data):
                        value = row_data[col_idx]
                        item = QTableWidgetItem()

                        if col_idx == 0:
                            item.setData(Qt.ItemDataRole.DisplayRole, int(value))
                            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        else:
                            item.setText(str(value))
                            if col_idx in [1, 2]:  # Name, Category
                                font = QFont()
                                item.setFont(font)
                                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                                item.setToolTip("Click để xem chi tiết thuốc")
                                item.setData(Qt.ItemDataRole.UserRole, medicine_id)

                        self.tableWidget.setItem(row_idx, col_idx, item)
                    else:
                        # "View Details" column
                        detail_item = QTableWidgetItem("View Details")
                        font = QFont()
                        font.setUnderline(True)
                        detail_item.setFont(font)
                        detail_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        detail_item.setData(Qt.ItemDataRole.UserRole, medicine_id)
                        detail_item.setToolTip("Click để xem chi tiết thuốc")
                        self.tableWidget.setItem(row_idx, col_idx, detail_item)

            # ✅ Enable sorting after all data is loaded
            self.tableWidget.setSortingEnabled(True)

        except Exception as e:
            print(f"Lỗi khi tải dữ liệu thuốc: {e}")
    def search_supplier(self):
        keyword = self.search_input.text().strip().lower()

        for row in range(self.tableWidget.rowCount()):
            name_item = self.tableWidget.item(row, 1)  # Cột tên nhà cung cấp
            if name_item:
                name_text = name_item.text().lower()
                match = keyword in name_text
                self.tableWidget.setRowHidden(row, not match)


    def show_medicine_detail(self, medicine_id):
        """Open medicine detail dialog."""
        detail_dialog = MedicineInformation_w(self.context, medicine_id)
        detail_dialog.data_updated.connect(self.load_medicine_data)
        detail_dialog.exec()

    def handle_cell_click(self, row, column):
        """Handle click events on table cells."""
        # Open details when clicking on name or "View Details" column
        if column == 1 or column == 5:
            item = self.tableWidget.item(row, column)
            if item is None:
                print("Item not found")
                return

            medicine_id = item.data(Qt.ItemDataRole.UserRole)
            if medicine_id:
                print(f"Opening details for medicine ID: {medicine_id}")
                self.show_medicine_detail(medicine_id)

    def goto_main(self):
        self.main_window = Main_w(self.context)
        self.main_window.show()
        self.hide()

class MedicineInformation_w(QDialog):
    data_updated = pyqtSignal()
    """Dialog window to display detailed information about a medicine."""
    def __init__(self, context, medicine_id):
        super(MedicineInformation_w, self).__init__()
        self.context = context
        self.medicine_id_value = medicine_id

        # Load UI
        ui_path = os.path.join(current_dir, 'ui', 'medicine_information.ui')
        print(f">>> medicine_information.ui path: {ui_path}")
        if not os.path.exists(ui_path):
            raise FileNotFoundError(f"Không tìm thấy UI file: {ui_path}")
        uic.loadUi(ui_path, self)

        # Set window properties
        self.setWindowTitle("Medicine Information")
        self.setWindowIcon(QIcon(icon_path))
        self.edit_mode = False
        self.deleteButton.clicked.connect(self.confirm_delete_medicine)
        self.pushButton.clicked.connect(self.toggle_edit_mode)
        self.deleteButton.setEnabled(False)
        # Load data
        self.load_medicine_data(self.medicine_id_value)


    def load_medicine_data(self, medicine_id_value):
        try:
            db = self.context.db_manager
            sql = """
                SELECT m.medicine_id, m.medicine_name, m.generic_name, c.category_name, s.supplier_name,
                    m.batch_number, m.expiration_date, m.stock_quantity, m.unit_price, m.sale_price
                FROM medicine m
                JOIN category c ON m.category_id = c.category_id
                JOIN supplier s ON m.supplier_id = s.supplier_id
                WHERE m.medicine_id = %s
            """
            db.execute(sql, (medicine_id_value,))
            result = db.fetchone()

            if result:
                self.medicine_id.setText(str(result[0]))
                self.medicine_id.setReadOnly(True)
                self.medicine_name.setText(result[1])
                self.medicine_name.setReadOnly(True)
                self.generic_name.setText(result[2])
                self.generic_name.setReadOnly(True)
                self.category_name.setText(result[3])
                self.category_name.setReadOnly(True)
                self.supplier_name.setText(result[4])
                self.supplier_name.setReadOnly(True)
                self.batch_number.setText(result[5])
                self.batch_number.setReadOnly(True)

                if result[6]:  # expiration_date
                    self.expiration_date.setDate(result[6].date())
                    # self.expiration_date.setReadOnly(True)
                    self.expiration_date.setReadOnly(True)

                self.stock_quantity.setValue(result[7])
                self.stock_quantity.setEnabled(False)
                self.unit_price.setValue(float(result[8]))
                self.unit_price.setEnabled(False)
                self.sale_price.setValue(float(result[9]))
                self.sale_price.setEnabled(False)
            else:
                QMessageBox.warning(self, "Thông báo", "Không tìm thấy thông tin thuốc.")

        except Exception as e:
            print(f"Lỗi khi tải dữ liệu thuốc: {e}")
            QMessageBox.warning(self, "Lỗi", f"Không thể tải thông tin thuốc: {e}")
    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode

        self.set_fields_editable(self.edit_mode)
        self.pushButton.setText("💾 Save" if self.edit_mode else "Edit...")
        self.deleteButton.setEnabled(self.edit_mode)


        if self.edit_mode:
            self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel)

            # ✅ Lưu dữ liệu ban đầu
            self.original_data = {
                "name": self.medicine_name.text(),
                "generic": self.generic_name.text(),
                "category": self.category_name.text(),
                "supplier": self.supplier_name.text(),
                "batch": self.batch_number.text(),
                "exp_date": self.expiration_date.date(),
                "quantity": self.stock_quantity.value(),
                "unit_price": self.unit_price.value(),
                "sale_price": self.sale_price.value()
            }

            cancel_btn = self.buttonBox.button(QDialogButtonBox.StandardButton.Cancel)
            if cancel_btn:
                try:
                    cancel_btn.clicked.disconnect()
                except:
                    pass
                cancel_btn.clicked.connect(self.cancel_edit)
        else:
            self.save_medicine_data()
            self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Close)


    def set_fields_editable(self, editable):
        self.medicine_name.setReadOnly(not editable)
        self.generic_name.setReadOnly(not editable)
        self.category_name.setReadOnly(True)   
        self.supplier_name.setReadOnly(True)
        self.batch_number.setReadOnly(not editable)

        self.expiration_date.setEnabled(editable)
        self.stock_quantity.setEnabled(editable)
        self.unit_price.setEnabled(editable)
        self.sale_price.setEnabled(editable)


    def save_medicine_data(self):
        try:
            db = self.context.db_manager

            sql = """
                UPDATE medicine SET
                    medicine_name = %s,
                    generic_name = %s,
                    batch_number = %s,
                    expiration_date = %s,
                    stock_quantity = %s,
                    unit_price = %s,
                    sale_price = %s
                WHERE medicine_id = %s
            """
            values = (
                self.medicine_name.text(),
                self.generic_name.text(),
                self.batch_number.text(),
                self.expiration_date.date().toString("yyyy-MM-dd"),
                self.stock_quantity.value(),
                self.unit_price.value(),
                self.sale_price.value(),
                self.medicine_id.text()
            )

            db.execute(sql, values)
            db.commit()
            QMessageBox.information(self, "Thành công", "Đã lưu thông tin thuốc.")
            self.context.db_manager.log_action(self.context.staff_id, f"Cập nhật thuốc: {self.medicine_id.text()}")

        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể lưu: {e}")


    def cancel_edit(self):
        if self.edit_mode:
            self.medicine_name.setText(self.original_data["name"])
            self.generic_name.setText(self.original_data["generic"])
            self.category_name.setText(self.original_data["category"])
            self.supplier_name.setText(self.original_data["supplier"])
            self.batch_number.setText(self.original_data["batch"])
            self.expiration_date.setDate(self.original_data["exp_date"])
            self.stock_quantity.setValue(self.original_data["quantity"])
            self.unit_price.setValue(self.original_data["unit_price"])
            self.sale_price.setValue(self.original_data["sale_price"])

            self.set_fields_editable(False)
            self.edit_mode = False
            self.pushButton.setText("Edit...")
            self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Close)
            QMessageBox.information(self, "Hủy chỉnh sửa", "Thay đổi đã được hủy.")

    def confirm_delete_medicine(self):
        reply = QMessageBox.question(self,"Xác nhận xóa",
        "Bạn có chắc chắn muốn xóa thuốc này?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.delete_medicine()
            self.context.db_manager.log_action(self.context.staff_id, f"Xóa thuốc: {self.medicine_id.text()}")


    def delete_medicine(self):
        try:
            db = self.context.db_manager
            sql = "DELETE FROM medicine WHERE medicine_id = %s"
            db.execute(sql, (self.medicine_id.text(),))
            db.commit()
            QMessageBox.information(self, "Thành công", "Đã xóa thuốc khỏi hệ thống.")
            self.data_updated.emit()  # Phát tín hiệu
            self.accept()             # Đóng dialog  # Đóng dialog sau khi xóa thành công
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể xóa thuốc: {e}")



class MedicineInformationAdd_w(QDialog):
    def __init__(self, context, parent=None):
        super().__init__(parent)
        self.context = context
        ui_path = os.path.join(current_dir, 'ui', 'medicine_information_add.ui')
        uic.loadUi(ui_path, self)
        self.setWindowTitle("Thêm thuốc mới")
        self.setWindowIcon(QtGui.QIcon(icon_path))
        self.init_category_combo()
        # Kết nối nút Save/Cancel
        self.buttonBox.button(QDialogButtonBox.StandardButton.Save).clicked.connect(self.save_medicine)
        self.buttonBox.button(QDialogButtonBox.StandardButton.Cancel).clicked.connect(self.reject)


    def init_category_combo(self):
        db = self.context.db_manager
        sql = "SELECT DISTINCT category_name FROM category"
        db.execute(sql)
        results = db.fetchall()
        self.comboBox.clear()
        for row in results:
            self.comboBox.addItem(row[0])

    def save_medicine(self):
        try:
            name = self.medicine_name.text().strip()
            gen_name = self.generic_name.text().strip()
            category = self.comboBox.currentText().strip()
            if not name:
                QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập tên thuốc.")
                return
            # Lấy category_id từ tên (nếu dùng id)
            db = self.context.db_manager
            sql = "SELECT category_id FROM category WHERE category_name=%s"
            db.execute(sql, (category,))
            result = db.fetchone()
            category_id = result[0] if result else None

            sql_insert = """
                INSERT INTO medicine (medicine_name, generic_name, category_id)
                VALUES (%s, %s, %s)
            """
            db.execute(sql_insert, (name, gen_name, category_id))
            db.commit()
            QMessageBox.information(self, "Thành công", "Đã thêm thuốc mới.")
            self.accept()
        except Exception as e:
            db.rollback()
            QMessageBox.warning(self, "Lỗi", f"Không thể thêm thuốc: {e}")




# Invoice Window
class Invoice_w(QMainWindow):
    def __init__(self, context):
        super(Invoice_w, self).__init__()
        self.context = context
        ui_path = os.path.join(current_dir, 'ui', 'invoice.ui')
        uic.loadUi(ui_path, self)
        self.setWindowTitle("Invoice Management")
        self.setWindowIcon(QtGui.QIcon(icon_path))
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.load_invoice_data()
        self.tableWidget.cellClicked.connect(self.handle_cell_click)
        self.back_button.clicked.connect(self.goto_main)
    def load_invoice_data(self):
        try:
            db = self.context.db_manager
            sql = "SELECT invoice_id, customer_id, total_amount, created_at FROM invoice"
            db.execute(sql)
            results = db.fetchall()
            self.tableWidget.setRowCount(len(results))
            self.tableWidget.setColumnCount(4)
            self.tableWidget.setHorizontalHeaderLabels(["Invoice ID", "Customer ID", "Total", "Created At"])

            for row_idx, row_data in enumerate(results):
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tableWidget.setItem(row_idx, col_idx, item)
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể tải hóa đơn: {e}")

    def handle_cell_click(self, row, column):
        invoice_id_item = self.tableWidget.item(row, 0)
        if invoice_id_item:
            invoice_id = invoice_id_item.text()
            self.detail_dialog = InvoiceInformation_w(self.context, invoice_id)
            self.detail_dialog.exec()
    def goto_main(self):
        self.main_window = Main_w(self.context)
        self.main_window.show()
        self.hide()

class InvoiceInformation_w(QDialog):
    def __init__(self, context, invoice_id):
        super().__init__()
        self.context = context
        self.invoice_id_value = invoice_id  # Đặt tên khác hẳn
        ui_path = os.path.join(current_dir, 'ui', 'create_invoice.ui')
        uic.loadUi(ui_path, self)
        self.setWindowTitle("Invoice Detail")
        self.setWindowIcon(QtGui.QIcon(icon_path))

        self.set_view_mode()
        self.load_data()

    def set_view_mode(self):
        self.save_button.setDisabled(True)
        self.cancel_button.setText("Đóng")
        self.add_medicine.setDisabled(True)
        self.add_medicine_2.setDisabled(True)
        self.customer_phone.setReadOnly(True)
        self.staff_name.setReadOnly(True)
        self.invoice_date.setReadOnly(True)
        self.payment_term.setDisabled(True)
        self.buy_list.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.buy_list.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.cancel_button.clicked.connect(self.accept)

    def load_data(self):
        try:
            db = self.context.db_manager
            db.execute(
                "SELECT invoice_id, invoice_date, customer_id, staff_id, total_amount, payment_method_id, payment_status FROM invoice WHERE invoice_id = %s",
                (int(self.invoice_id_value),))
            invoice_info = db.fetchone()
            if not invoice_info:
                QMessageBox.warning(self, "Lỗi", "Không tìm thấy hóa đơn!")
                self.reject()
                return

            self.invoice_id.setText(str(invoice_info[0]))
            self.invoice_date.setDate(invoice_info[1])
            self.staff_name.setText(str(invoice_info[3]))
            self.sum_money.setText(str(invoice_info[4]))
            self.payment_term.setCurrentIndex(self.payment_term.findData(invoice_info[5]))

            db.execute("SELECT customer_name, customer_phone FROM customer WHERE customer_id = %s", (invoice_info[2],))
            cinfo = db.fetchone()
            if cinfo:
                self.customer_phone.setText(cinfo[1])
                self.label_6.setText(f"{cinfo[0]} ({cinfo[1]})")

            # Query thuốc trong hóa đơn, lấy cả medicine_id để đủ cột
            db.execute(
                """SELECT m.medicine_id, m.medicine_name, m.unit, d.sale_price, d.quantity, d.total_price
                FROM invoice_detail d
                JOIN medicine m ON d.medicine_id = m.medicine_id
                WHERE d.invoice_id = %s""", (invoice_info[0],))
            meds = db.fetchall()
            print("DEBUG - meds:", meds)  # Xem có thuốc ko

            self.buy_list.setRowCount(len(meds))
            self.buy_list.setColumnCount(6)
            self.buy_list.setHorizontalHeaderLabels(["Tên thuốc", "Đơn vị", "Giá bán", "Số lượng", "Thành tiền", "ID"])
            self.buy_list.setColumnHidden(5, True)
            for i, med in enumerate(meds):
                self.buy_list.setItem(i, 0, QTableWidgetItem(str(med[1])))  # Tên thuốc
                self.buy_list.setItem(i, 1, QTableWidgetItem(str(med[2])))  # Đơn vị
                self.buy_list.setItem(i, 2, QTableWidgetItem(str(med[3])))  # Giá bán
                self.buy_list.setItem(i, 3, QTableWidgetItem(str(med[4])))  # Số lượng
                self.buy_list.setItem(i, 4, QTableWidgetItem(str(med[5])))  # Thành tiền
                self.buy_list.setItem(i, 5, QTableWidgetItem(str(med[0])))  # ID thuốc (ẩn)

            for i in range(self.buy_list.rowCount()):
                if self.buy_list.columnCount() > 5:
                    self.buy_list.setCellWidget(i, 6, None)

        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Lỗi khi tải thông tin hóa đơn: {e}")

class CreateInvoiceDialog_w(QDialog):
    def __init__(self, context, invoice_id=None, parent=None):
        super().__init__(parent)
        self.context = context
        self.invoice_id = invoice_id  # None khi tạo mới, int khi xem/sửa
        self.customer_id = None
        self.medicine_list = []  # [(medicine_id, medicine_name, unit, sale_price, quantity, total_price)]
        ui_path = os.path.join(os.getcwd(), "ui", "create_invoice.ui")
        uic.loadUi(ui_path, self)

        # Set window properties
        self.setWindowTitle("Invoice")
        self.setWindowIcon(QIcon(icon_path))

        # Tải danh sách phương thức thanh toán (chỉ 3: bank transfer, 4: cash)
        self.load_payment_methods()

        # Kết nối sự kiện
        self.customer_phone.editingFinished.connect(self.lookup_customer)
        self.add_medicine.clicked.connect(self.show_add_medicine_dialog)
        self.add_medicine_2.clicked.connect(self.create_new_customer)
        self.save_button.clicked.connect(self.save_invoice)
        self.cancel_button.clicked.connect(self.reject)
        self.invoice_date.setDate(QDate.currentDate())
        self.invoice_date.setReadOnly(True)
        self.invoice_date.setEnabled(False)
        self.staff_name.setText(str(self.context.staff_id)) 
        self.staff_name.setReadOnly(True)
        self.invoice_id.setText("Tự động") 
        self.invoice_id.setReadOnly(True)
        self.invoice_id.setEnabled(False)

    def load_payment_methods(self):
        db = self.context.db_manager
        sql = "SELECT payment_method_id, payment_name FROM payment_method WHERE payment_method_id IN (3,4)"
        db.execute(sql)
        results = db.fetchall()
        self.payment_term.clear()
        self.payment_methods_map = {}  # Tên => ID
        for pid, name in results:
            self.payment_term.addItem(name, pid)
            self.payment_methods_map[name] = pid

    def lookup_customer(self):
        phone = self.customer_phone.text().strip()
        if not phone:
            self.customer_id = None
            self.label_6.setText("Chưa nhập SĐT khách hàng.")
            self.customer_phone.setStyleSheet("")
            return

        db = self.context.db_manager
        db.execute("SELECT customer_id, customer_name FROM customer WHERE customer_phone = %s", (phone,))
        result = db.fetchone()
        if result:
            self.customer_id = result[0]
            self.label_6.setText(f"{result[1]} ({phone})")
            self.customer_phone.setStyleSheet("background-color: #eaffea;")
        else:
            # Nếu chưa có, hỏi tên và tạo khách mới
            while True:
                name, ok = QInputDialog.getText(self, "Thêm khách hàng", f"Số {phone} chưa có, nhập tên khách hàng:")
                if not ok or not name.strip():
                    self.customer_id = None
                    self.label_6.setText("Chưa nhập tên khách hàng.")
                    self.customer_phone.setStyleSheet("background-color: #ffeaea;")
                    QMessageBox.warning(self, "Lỗi", "Bạn phải nhập tên khách hàng để tạo mới!")
                    break
                try:
                    db.execute("SELECT customer_id FROM customer WHERE customer_phone = %s", (phone,))
                    if db.fetchone():
                        # Đã có khách hàng khác vừa nhập vào (do nhập nhiều lần)
                        db.execute("SELECT customer_id, customer_name FROM customer WHERE customer_phone = %s", (phone,))
                        result = db.fetchone()
                        self.customer_id = result[0]
                        self.label_6.setText(f"{result[1]} ({phone})")
                        self.customer_phone.setStyleSheet("background-color: #eaffea;")
                        break
                    db.execute("INSERT INTO customer (customer_name, customer_phone) VALUES (%s, %s)", (name.strip(), phone))
                    db.commit()
                    db.execute("SELECT customer_id FROM customer WHERE customer_phone = %s", (phone,))
                    self.customer_id = db.fetchone()[0]
                    self.label_6.setText(f"{name.strip()} ({phone})")
                    self.customer_phone.setStyleSheet("background-color: #eaffea;")
                    QMessageBox.information(self, "Thành công", f"Đã thêm khách hàng {name.strip()}")
                    db.log_action(self.context.staff_id, f"Thêm khách hàng mới: {name.strip()} - {phone}")
                    break
                except Exception as e:
                    QMessageBox.warning(self, "Lỗi", f"Không thể thêm khách hàng: {e}")
                    self.customer_id = None
                    self.customer_phone.setStyleSheet("background-color: #ffeaea;")
                    break



    def create_new_customer(self):
        phone = self.customer_phone.text().strip()
        if not phone:
            QMessageBox.warning(self, "Thiếu thông tin", "Bạn phải nhập số điện thoại trước!")
            return

        db = self.context.db_manager
        # Kiểm tra trùng số điện thoại trước
        db.execute("SELECT customer_id FROM customer WHERE customer_phone = %s", (phone,))
        if db.fetchone():
            QMessageBox.warning(self, "Lỗi", "Số điện thoại này đã tồn tại trong hệ thống!")
            return

        name, ok = QInputDialog.getText(self, "Thêm khách hàng", "Nhập tên khách hàng:")
        if ok:
            name = name.strip()
            if not name:
                QMessageBox.warning(self, "Thiếu thông tin", "Bạn phải nhập tên khách hàng!")
                return
            try:
                db.execute("INSERT INTO customer (customer_name, customer_phone) VALUES (%s, %s)", (name, phone))
                db.commit()
                db.execute("SELECT customer_id FROM customer WHERE customer_phone = %s", (phone,))
                self.customer_id = db.fetchone()[0]
                self.label_6.setText(f"{name} ({phone})")
                self.customer_phone.setStyleSheet("background-color: #eaffea;")
                QMessageBox.information(self, "Thành công", f"Đã thêm khách hàng {name}")
                db.log_action(self.context.staff_id, f"Thêm khách hàng mới: {name} - {phone}")
            except Exception as e:
                QMessageBox.warning(self, "Lỗi", f"Không thể thêm khách hàng: {e}")


    def show_add_medicine_dialog(self):
        db = self.context.db_manager
        db.execute("SELECT medicine_id, medicine_name, unit, sale_price, stock_quantity FROM medicine WHERE stock_quantity > 0")
        meds = db.fetchall()
        if not meds:
            QMessageBox.warning(self, "Thông báo", "Không còn thuốc tồn kho để bán.")
            return
        med_names = [f"{row[1]} ({row[2]}) - Giá: {row[3]} - Tồn: {row[4]}" for row in meds]
        idx, ok = QInputDialog.getItem(self, "Chọn thuốc", "Chọn thuốc:", med_names, 0, False)
        if ok and idx:
            med = meds[med_names.index(idx)]
            qty, ok2 = QInputDialog.getInt(self, "Số lượng", f"Nhập số lượng (1 ~ {med[4]}):", 1, 1, med[4])
            if ok2:
                # Kiểm tra trùng, cộng dồn số lượng nếu đã có
                existed = False
                for i, m in enumerate(self.medicine_list):
                    if m[0] == med[0]:
                        # Cộng dồn số lượng, cập nhật giá
                        new_qty = m[4] + qty
                        if new_qty > med[4]:
                            QMessageBox.warning(self, "Lỗi", f"Tổng số lượng vượt tồn kho ({med[4]})")
                            return
                        self.medicine_list[i] = (m[0], m[1], m[2], m[3], new_qty, m[3] * new_qty)
                        existed = True
                        break
                if not existed:
                    self.medicine_list.append((med[0], med[1], med[2], med[3], qty, med[3]*qty))
                self.refresh_medicine_table()
                self.update_total()

    def refresh_medicine_table(self):
        self.buy_list.setRowCount(len(self.medicine_list))
        for i, med in enumerate(self.medicine_list):
            # (medicine_id, medicine_name, unit, sale_price, quantity, total_price)
            self.buy_list.setItem(i, 0, QTableWidgetItem(str(med[1])))  # Tên thuốc
            self.buy_list.setItem(i, 1, QTableWidgetItem(str(med[2])))  # Đơn vị
            self.buy_list.setItem(i, 2, QTableWidgetItem(str(med[3])))  # Giá bán
            self.buy_list.setItem(i, 3, QTableWidgetItem(str(med[4])))  # Số lượng
            self.buy_list.setItem(i, 4, QTableWidgetItem(str(med[5])))  # Thành tiền
            self.buy_list.setItem(i, 5, QTableWidgetItem(str(med[0])))  # ID (ẩn)
            # self.buy_list.setColumnHidden(5, True) 
            # Thêm nút xóa nếu là tạo mới/sửa
            btn = QPushButton("Xóa")
            btn.clicked.connect(lambda _, row=i: self.remove_medicine_row(row))
            self.buy_list.setCellWidget(i, 6, btn)

    def remove_medicine_row(self, row):
        if 0 <= row < len(self.medicine_list):
            del self.medicine_list[row]
            self.refresh_medicine_table()
            self.update_total()

    def update_total(self):
        total = sum(med[5] for med in self.medicine_list)
        self.sum_money.setText(str(total))

    def save_invoice(self):
        # Kiểm tra dữ liệu
        self.setWindowIcon(QIcon(icon_path))
        self.lookup_customer() 
        
        if not self.customer_id:
            
            QMessageBox.warning(self, "Lỗi", "Bạn chưa chọn khách hàng!")
            return
        if not self.medicine_list:
            QMessageBox.warning(self, "Lỗi", "Bạn chưa chọn thuốc!")
            return
        payment_method_id = self.payment_term.currentData()
        invoice_date = self.invoice_date.date().toString("yyyy-MM-dd")
        staff_id = self.context.staff_id
        total = self.sum_money.text()
        db = self.context.db_manager
        # Lưu invoice
        try:
            db.execute(
                "INSERT INTO invoice (invoice_date, customer_id, staff_id, total_amount, payment_method_id, payment_status) VALUES (%s,%s,%s,%s,%s,%s)",
                (invoice_date, self.customer_id, staff_id, total, payment_method_id, "Đã thanh toán")
            )
            db.commit()
            db.execute("SELECT LAST_INSERT_ID()")
            invoice_id = db.fetchone()[0]
            # Lưu từng thuốc
            for med in self.medicine_list:
                db.execute(
                    "INSERT INTO invoice_detail (invoice_id, medicine_id, quantity, sale_price, total_price) VALUES (%s, %s, %s, %s, %s)",
                    (invoice_id, med[0], med[4], med[3], med[5])
                )
                # Trừ tồn kho
                db.execute("UPDATE medicine SET stock_quantity = stock_quantity - %s WHERE medicine_id = %s",
                           (med[4], med[0]))
            db.commit()
            db.log_action(staff_id, f"Tạo hóa đơn: {invoice_id} (Khách: {self.customer_id}, Tổng: {total})")
            QMessageBox.information(self, "Thành công", f"Đã lưu hóa đơn #{invoice_id}")
            self.accept()
        except Exception as e:
            db.rollback()
            QMessageBox.warning(self, "Lỗi", f"Lưu hóa đơn thất bại: {e}")

    def load_invoice_detail(self):
        db = self.context.db_manager
        db.execute(
            "SELECT invoice_id, invoice_date, customer_id, staff_id, total_amount, payment_method_id FROM invoice WHERE invoice_id = %s",
            (self.invoice_id,))
        info = db.fetchone()
        if not info:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy hóa đơn!")
            self.reject()
            return
        self.invoice_id.setText(str(info[0]))
        self.invoice_date.setDate(info[1])
        self.customer_id = info[2]
        self.staff_name.setText(str(info[3]))
        self.sum_money.setText(str(info[4]))
        self.payment_term.setCurrentIndex(self.payment_term.findData(info[5]))
        # Load khách
        db.execute("SELECT customer_name, customer_phone FROM customer WHERE customer_id = %s", (self.customer_id,))
        cinfo = db.fetchone()
        if cinfo:
            self.customer_phone.setText(cinfo[1])
            self.label_6.setText(f"{cinfo[0]} ({cinfo[1]})")
        # Load danh sách thuốc
        db.execute(
            """SELECT m.medicine_id, m.medicine_name, m.unit, d.sale_price, d.quantity, d.total_price
               FROM invoice_detail d JOIN medicine m ON d.medicine_id = m.medicine_id
               WHERE d.invoice_id = %s""", (self.invoice_id,))
        meds = db.fetchall()
        self.medicine_list = [(med[0], med[1], med[2], float(med[3]), int(med[4]), float(med[5])) for med in meds]
        self.refresh_medicine_table()

    def set_view_mode(self):
        self.save_button.setDisabled(True)
        self.cancel_button.setText("Đóng")
        self.add_medicine.setDisabled(True)
        self.add_medicine_2.setDisabled(True)
        self.customer_phone.setReadOnly(True)
        self.staff_name.setReadOnly(True)
        self.invoice_date.setReadOnly(True)
        self.payment_term.setDisabled(True)
        self.buy_list.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.buy_list.setSelectionMode(QTableWidget.SelectionMode.NoSelection)

    def init_new_invoice(self):
        # Reset cho tạo mới
        self.invoice_id.setText("Tự động")
        self.invoice_date.setDate(QDate.currentDate())
        self.staff_name.setText(str(self.context.staff_id))
        self.sum_money.setText("0")
        self.payment_term.setCurrentIndex(0)
        self.buy_list.setRowCount(0)
        self.set_edit_mode()

    def set_edit_mode(self):
        self.save_button.setEnabled(True)
        self.cancel_button.setText("Hủy")
        self.add_medicine.setEnabled(True)
        self.add_medicine_2.setEnabled(True)
        self.customer_phone.setReadOnly(False)
        self.staff_name.setReadOnly(True)
        self.invoice_date.setReadOnly(False)
        self.payment_term.setEnabled(True)
        self.buy_list.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.buy_list.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

# Stock Window
class Stock_w(QMainWindow):
    def __init__(self, context):
        super(Stock_w, self).__init__()
        self.context = context
        ui_path = os.path.join(current_dir, 'ui', 'stock.ui')
        if not os.path.exists(ui_path):
            raise FileNotFoundError(f"Không tìm thấy UI file: {ui_path}")
        uic.loadUi(ui_path, self)
        
        self.setWindowTitle("Stock Management")
        self.setWindowIcon(QtGui.QIcon(icon_path))
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # Setup signals
        self.back_button.clicked.connect(self.goto_main)
        self.tableWidget.cellClicked.connect(self.handle_cell_click)
        self.search_input.textChanged.connect(self.search_stock)
        self.tableWidget.setSortingEnabled(True)

        self.add_stock.clicked.connect(self.show_create_stock)
        self.load_stock_data()

    def load_stock_data(self):
        try:
            db = self.context.db_manager
            sql = """
                SELECT s.stock_id, sd.medicine_id, m.medicine_name, sd.quantity, sd.price, sd.batch_number,
                    sd.expiration_date, sup.supplier_name, s.staff_id, s.created_at
                FROM stock_detail sd
                JOIN stock s ON s.stock_id = sd.stock_id
                JOIN medicine m ON sd.medicine_id = m.medicine_id
                JOIN supplier sup ON s.supplier_id = sup.supplier_id
                ORDER BY s.created_at DESC, s.stock_id DESC
            """
            db.execute(sql)
            results = db.fetchall()
            self.tableWidget.setRowCount(len(results))
            self.tableWidget.setColumnCount(10)
            self.tableWidget.setHorizontalHeaderLabels([
                "Stock ID", "Medicine ID", "Medicine Name", "Quantity", "Price", "Batch", "Exp. Date", "Supplier", "Staff", "Created At"
            ])
            # Ẩn cột Stock ID, Medicine ID nếu muốn
            self.tableWidget.setColumnHidden(0, True)
            self.tableWidget.setColumnHidden(1, True)
            for row_idx, row_data in enumerate(results):
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tableWidget.setItem(row_idx, col_idx, item)
                # Nếu muốn thêm nút Xem chi tiết từng phiếu nhập (stock_id) hoặc thuốc (medicine_id), thêm code ở đây!
        except Exception as e:
            print("Lỗi khi tải dữ liệu stock:", e)


    def search_stock(self):
        keyword = self.search_input.text().strip().lower()
        for row in range(self.tableWidget.rowCount()):
            name_item = self.tableWidget.item(row, 1)
            if name_item:
                name_text = name_item.text().lower()
                match = keyword in name_text
                self.tableWidget.setRowHidden(row, not match)

    def handle_cell_click(self, row, column):
        if column == 1 or column == 6:
            item = self.tableWidget.item(row, column)
            medicine_id = item.data(Qt.ItemDataRole.UserRole)
            if medicine_id:
                self.show_stock_detail(medicine_id)

    def show_stock_detail(self, medicine_id):
        dialog = MedicineInformation_w(self.context, medicine_id)
        dialog.exec()

    def goto_main(self):
        self.main_window = Main_w(self.context)
        self.main_window.show()
        self.hide()
    def show_create_stock(self):
        dialog = CreateStockDialog_w(self.context)
        dialog.exec()


class StockInformation_w(QDialog):
    def __init__(self, context, stock_id):
        super(StockInformation_w, self).__init__()
        self.context = context
        self.stock_id = stock_id
        ui_path = os.path.join(current_dir, 'ui', 'stock_information.ui')
        uic.loadUi(ui_path, self)
        self.setWindowTitle("Stock Detail")
        self.setWindowIcon(QtGui.QIcon(icon_path))

        self.load_data()

    def load_data(self):
        try:
            db = self.context.db_manager
            sql = "SELECT * FROM stock WHERE stock_id = %s"
            db.execute(sql, (self.stock_id,))
            result = db.fetchone()

            if result:
                self.lineEdit_stock_id.setText(str(result[0]))
                self.lineEdit_medicine_id.setText(str(result[1]))
                self.spinBox_quantity.setValue(result[2])
                self.dateEdit_updated.setDate(result[3].date())
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Lỗi khi tải thông tin kho: {e}")

class CreateStockDialog_w(QDialog):
    def __init__(self, context, parent=None):
        super().__init__(parent)
        self.context = context
        ui_path = os.path.join(current_dir, 'ui', 'create_stock.ui')
        uic.loadUi(ui_path, self)
        self.setWindowTitle("Tạo phiếu nhập kho")
        self.setWindowIcon(QtGui.QIcon(icon_path))

        # Thiết lập thông tin mặc định
        self.stock_date.setDate(QDate.currentDate())
        self.staff_name.setText(str(self.context.staff_id))
        self.staff_name.setReadOnly(True)
        self.stock_id.setReadOnly(True)
        self.stock_id.setPlaceholderText("Auto")

        # Load danh mục
        self.load_supplier_list()
        self.load_medicine_name_list()
        self.load_payment_methods()

        # Kết nối sự kiện
        self.save_button.clicked.connect(self.save_stock)
        self.cancel_button.clicked.connect(self.reject)
        self.add_medicine.clicked.connect(self.add_row)
        self.add_new_medicine.clicked.connect(self.open_add_medicine_dialog)

        # Thiết lập bảng nhập thuốc
        self.buy_list.setRowCount(0)
        self.buy_list.setColumnCount(7)
        self.buy_list.setHorizontalHeaderLabels([
            "Tên thuốc", "Giá nhập", "Giá bán", "Số lượng", "Số lô", "Hạn dùng", "Xóa"
        ])
        self.buy_list.cellChanged.connect(self.update_sum_money)

    # ========== LOAD DANH MỤC ==========
    def load_supplier_list(self):
        db = self.context.db_manager
        sql = "SELECT supplier_id, supplier_name FROM supplier"
        db.execute(sql)
        results = db.fetchall()
        self.supplier_map = {}
        self.supplier.clear()
        for supplier_id, supplier_name in results:
            self.supplier.addItem(supplier_name)
            self.supplier_map[supplier_name] = supplier_id

    def load_payment_methods(self):
        db = self.context.db_manager
        sql = "SELECT payment_method_id, payment_name FROM payment_method WHERE payment_name IN ('COD', 'prepayment')"
        db.execute(sql)
        results = db.fetchall()
        self.payment_method_map = {}
        self.payment_term.clear()
        for payment_method_id, payment_name in results:
            self.payment_term.addItem(payment_name)
            self.payment_method_map[payment_name] = payment_method_id

    def load_medicine_name_list(self):
        db = self.context.db_manager
        sql = "SELECT DISTINCT medicine_name FROM medicine"
        db.execute(sql)
        results = db.fetchall()
        self.medicine_names = [row[0] for row in results] if results else []

    # ========== HÀM TẠO/XÓA DÒNG NHẬP THUỐC ==========
    def add_row(self):
        row = self.buy_list.rowCount()
        self.buy_list.insertRow(row)
        # Cột 0: Tên thuốc
        combo = QComboBox()
        combo.setEditable(True)
        combo.addItems(self.medicine_names)
        self.buy_list.setCellWidget(row, 0, combo)
        # Cột 1: Giá nhập
        spin_price = QDoubleSpinBox()
        spin_price.setMinimum(0)
        spin_price.setMaximum(1_000_000_000)
        spin_price.setDecimals(2)
        spin_price.valueChanged.connect(lambda _: self.update_sale_price(row))
        self.buy_list.setCellWidget(row, 1, spin_price)
        # Cột 2: Giá bán (readonly)
        sale_item = QTableWidgetItem("")
        sale_item.setFlags(sale_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.buy_list.setItem(row, 2, sale_item)
        # Cột 3: Số lượng
        spin_quantity = QSpinBox()
        spin_quantity.setMinimum(1)
        spin_quantity.valueChanged.connect(lambda _: self.update_sum_money())
        self.buy_list.setCellWidget(row, 3, spin_quantity)
        # Cột 4: Số lô
        batch_item = QTableWidgetItem("")
        self.buy_list.setItem(row, 4, batch_item)
        # Cột 5: Hạn dùng
        date_exp = QDateEdit()
        date_exp.setCalendarPopup(True)
        date_exp.setDate(QDate.currentDate())
        self.buy_list.setCellWidget(row, 5, date_exp)
        # Cột 6: Xóa dòng
        del_btn = QPushButton("X")
        del_btn.clicked.connect(lambda _, r=row: self.remove_row(r))
        self.buy_list.setCellWidget(row, 6, del_btn)

    def remove_row(self, row):
        self.buy_list.removeRow(row)
        self.update_sum_money()

    def open_add_medicine_dialog(self):
        dialog = MedicineInformationAdd_w(self.context, self)
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            self.load_medicine_name_list()
            # Cập nhật lại combobox cho các dòng đã có
            for row in range(self.buy_list.rowCount()):
                combo = self.buy_list.cellWidget(row, 0)
                if isinstance(combo, QComboBox):
                    current = combo.currentText()
                    combo.clear()
                    combo.addItems(self.medicine_names)
                    idx = combo.findText(current)
                    if idx >= 0:
                        combo.setCurrentIndex(idx)

    # ========== HÀM TÍNH TỔNG TIỀN & TỰ ĐỘNG GIÁ BÁN ==========
    def update_sum_money(self):
        total = 0.0
        for row in range(self.buy_list.rowCount()):
            spin_price = self.buy_list.cellWidget(row, 1)
            spin_quantity = self.buy_list.cellWidget(row, 3)
            if spin_price and spin_quantity:
                total += spin_price.value() * spin_quantity.value()
        self.sum_money.setText(f"{total:,.2f}")

    def update_sale_price(self, row):
        spin_price = self.buy_list.cellWidget(row, 1)
        sale_item = self.buy_list.item(row, 2)
        if spin_price and sale_item:
            price = spin_price.value()
            sale_price = round(price * 1.2, 2)  # Lấy giá bán = giá nhập * 1.2
            sale_item.setText(str(sale_price))
            self.update_sum_money()

    # ========== HÀM XỬ LÝ DB ==========
    def insert_stock(self, supplier_id, staff_id, payment_method_id, stock_date):
        db = self.context.db_manager
        sql = """
            INSERT INTO stock (supplier_id, staff_id, payment_method_id, created_at)
            VALUES (%s, %s, %s, %s)
        """
        db.execute(sql, (supplier_id, staff_id, payment_method_id, stock_date))
        db.commit()
        db.execute("SELECT LAST_INSERT_ID()")
        stock_id = db.fetchone()[0]
        return stock_id

    def insert_or_update_medicine(self, medicine_name, supplier_id, quantity, price, sale_price, batch, exp_date):
        db = self.context.db_manager
        db.execute("SELECT medicine_id FROM medicine WHERE medicine_name=%s AND batch_number=%s", (medicine_name, batch))
        med_exist = db.fetchone()
        if med_exist:
            medicine_id = med_exist[0]
            db.execute(
                "UPDATE medicine SET stock_quantity = stock_quantity + %s, unit_price=%s, sale_price=%s, expiration_date=%s WHERE medicine_id=%s",
                (quantity, price, sale_price, exp_date, medicine_id)
            )
            db.commit()
        else:
            sql = """
                INSERT INTO medicine (medicine_name, supplier_id, stock_quantity, unit_price, sale_price, batch_number, expiration_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            db.execute(sql, (medicine_name, supplier_id, quantity, price, sale_price, batch, exp_date))
            db.commit()
            db.execute("SELECT LAST_INSERT_ID()")
            medicine_id = db.fetchone()[0]
        return medicine_id

    def insert_stock_detail(self, stock_id, medicine_id, quantity, price, batch, exp_date, note=""):
        db = self.context.db_manager
        sql = """
            INSERT INTO stock_detail (stock_id, medicine_id, quantity, price, batch_number, expiration_date, note)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        db.execute(sql, (stock_id, medicine_id, quantity, price, batch, exp_date, note))
        db.commit()

    # ========== HÀM LƯU PHIẾU NHẬP ==========
    def save_stock(self):
        try:
            db = self.context.db_manager
            staff_id = self.context.staff_id
            supplier_name = self.supplier.currentText()
            supplier_id = self.supplier_map.get(supplier_name)
            payment_name = self.payment_term.currentText()
            payment_method_id = self.payment_method_map.get(payment_name)
            stock_date = self.stock_date.date().toString("yyyy-MM-dd")

            if not supplier_id:
                QMessageBox.warning(self, "Lỗi", "Vui lòng chọn nhà cung cấp hợp lệ.")
                return
            if not payment_method_id:
                QMessageBox.warning(self, "Lỗi", "Vui lòng chọn hình thức thanh toán hợp lệ.")
                return

            # 1. Insert stock
            stock_id = self.insert_stock(supplier_id, staff_id, payment_method_id, stock_date)

            # 2. Insert/update medicine và lưu stock_detail
            medicines = []
            for row in range(self.buy_list.rowCount()):
                combo = self.buy_list.cellWidget(row, 0)
                medicine_name = combo.currentText().strip() if combo else ""
                spin_price = self.buy_list.cellWidget(row, 1)
                price = spin_price.value() if spin_price else 0
                sale_item = self.buy_list.item(row, 2)
                sale_price = float(sale_item.text()) if sale_item and sale_item.text() else round(price * 1.2, 2)
                spin_quantity = self.buy_list.cellWidget(row, 3)
                quantity = spin_quantity.value() if spin_quantity else 0
                batch = self.buy_list.item(row, 4).text().strip() if self.buy_list.item(row, 4) else ""
                exp_widget = self.buy_list.cellWidget(row, 5)
                exp_date = exp_widget.date().toString("yyyy-MM-dd") if exp_widget else None

                if not medicine_name or quantity <= 0:
                    continue

                medicine_id = self.insert_or_update_medicine(
                    medicine_name, supplier_id, quantity, price, sale_price, batch, exp_date
                )
                medicines.append((medicine_id, quantity, price, batch, exp_date))

            if not medicines:
                db.execute("DELETE FROM stock WHERE stock_id=%s", (stock_id,))
                db.commit()
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập ít nhất 1 dòng thuốc hợp lệ.")
                return

            for medicine_id, quantity, price, batch, exp_date in medicines:
                self.insert_stock_detail(stock_id, medicine_id, quantity, price, batch, exp_date)

            self.context.db_manager.log_action(staff_id, f"Tạo phiếu nhập kho: {stock_id}")
            QMessageBox.information(self, "Thành công", "Đã lưu phiếu nhập kho và cập nhật danh mục thuốc.")
            self.accept()
        except Exception as e:
            db.rollback()
            QMessageBox.warning(self, "Lỗi", f"Không thể lưu phiếu nhập: {e}")


# Logs Window
class Logs_w(QMainWindow):
    def __init__(self, context):    
        super(Logs_w, self).__init__()
        self.context = context
        ui_path = os.path.join(current_dir, 'ui', 'logs.ui')
        print(">>> logs.ui path:", ui_path)
        if not os.path.exists(ui_path):
            raise FileNotFoundError(f"Không tìm thấy UI file: {ui_path}")
        uic.loadUi(ui_path, self)
        self.setWindowTitle("Logs Management")
        self.setWindowIcon(QtGui.QIcon(icon_path))
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        # Load initial data
        self.load_log_data()

        # Connect signals
        self.tableWidget.setSortingEnabled(True)
        self.search_input.textChanged.connect(self.search_logs)
        self.back_button.clicked.connect(self.goto_main)

    def load_log_data(self):
        try:
            db = self.context.db_manager
            sql = """
                SELECT log_id, staff_id, action, log_time
                FROM activity_log
                ORDER BY log_time DESC
            """
            db.execute(sql)
            results = db.fetchall()

            self.tableWidget.setRowCount(len(results))
            self.tableWidget.setColumnCount(4)
            self.tableWidget.setHorizontalHeaderLabels(["Log ID", "Staff ID", "Action", "Timestamp"])
            self.tableWidget.setSortingEnabled(False)
            
            for row_idx, row_data in enumerate(results):
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tableWidget.setItem(row_idx, col_idx, item)

            self.tableWidget.setSortingEnabled(True)
            self.tableWidget.resizeColumnsToContents()
            self.tableWidget.setColumnWidth(2, 500) 
            self.tableWidget.setColumnWidth(3, 150) 
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể tải log: {e}")
    def search_logs(self):
        keyword = self.search_input.text().strip().lower()

        for row in range(self.tableWidget.rowCount()):
            visible = False
            if col == 3:  
                item = self.tableWidget.item(row, col)
                if item and keyword in item.text().lower():
                    visible = True
                    break
            self.tableWidget.setRowHidden(row, not visible)
    def goto_main(self):
        self.main_window = Main_w(self.context)
        self.main_window.show()
        self.hide()

# Login Window - Done
class Login_w(QDialog):
    def __init__(self, context):
        super(Login_w, self).__init__()
        self.context = context
        ui_path = os.path.join(current_dir, 'ui', 'login.ui')
        if not os.path.exists(ui_path):
            raise FileNotFoundError(f"Không tìm thấy file UI: {ui_path}")
        uic.loadUi(ui_path, self)

        self.setFixedSize(250, 110)
        self.setWindowTitle("MediManager")
        self.setWindowIcon(QtGui.QIcon(icon_path))

        self.register_label.linkActivated.connect(self.goto_register)
        self.login_button.clicked.connect(self.login)
        self.login_button.setDefault(True)

        # Ẩn mật khẩu mặc định
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)

        # Tạo nút 👁
        self.toggle_pw_button = QToolButton(self.login_password)
        self.toggle_pw_button.setIcon(QIcon("icon/eye_closed.png"))  # đặt icon của bạn
        self.toggle_pw_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_pw_button.setStyleSheet("border: none; padding: 0px;")
        self.toggle_pw_button.setFixedSize(20, 20)
        self.toggle_pw_button.move(self.login_password.rect().right() - 24, 0)

        # Gắn click
        self.toggle_pw_button.clicked.connect(self.show_password_temporarily)

        # Tạo QTimer để ẩn sau 1 giây
        self.hide_pw_timer = QTimer(self)
        self.hide_pw_timer.setSingleShot(True)
        self.hide_pw_timer.timeout.connect(self.hide_password)

    def login(self):
        un = self.login_user.text()
        psw = self.login_password.text()
        try:
            db = self.context.db_manager
            sql = 'SELECT staff_id, staff_psw FROM staff WHERE staff_id = %s'
            db.execute(sql, (un,))
            result = db.fetchone()

            if result:
                stored_pw = result[1]

                try:
                    # Nếu là bcrypt → kiểm tra bằng checkpw
                    if bcrypt.checkpw(psw.encode('utf-8'), stored_pw.encode('utf-8')):
                        login_success = True
                    else:
                        login_success = False
                except ValueError:
                    # Nếu không phải bcrypt → so sánh trực tiếp
                    if psw == stored_pw:
                        login_success = True

                        # Tự động mã hóa lại mật khẩu cũ
                        new_hash = bcrypt.hashpw(psw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                        db.execute("UPDATE staff SET staff_psw = %s WHERE staff_id = %s", (new_hash, un))
                        db.commit()
                        print("Đã tự động mã hóa lại mật khẩu cũ cho user:", un)
                    else:
                        login_success = False

                if login_success:
                    QMessageBox.information(self, "Login Success", "Đăng nhập thành công!")
                    self.context.staff_id = result[0]
                    self.main_window = Main_w(self.context, un)
                    self.context.db_manager.log_action(self.context.staff_id, "Đăng nhập hệ thống")
                    self.main_window.show()
                    self.close()
                else:
                    QMessageBox.warning(self, "Login Failed", "Sai tài khoản hoặc mật khẩu.")
        except mysql_db.Error as e:
            QMessageBox.critical(self, "Database Error", f"Lỗi kết nối CSDL: {str(e)}")

    def show_password_temporarily(self):
        self.login_password.setEchoMode(QLineEdit.EchoMode.Normal)
        icon_path = os.path.join(current_dir, "icon", "eye_open.png")
        self.toggle_pw_button.setIcon(QIcon(icon_path))

        # Start timer 1 giây để ẩn lại
        self.hide_pw_timer.start(1000)

    def hide_password(self):
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)
        icon_path = os.path.join(current_dir, "icon", "eye_closed.png")
        self.toggle_pw_button.setIcon(QIcon(icon_path))

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.login()

    def goto_register(self):
        self.register_window = Register_w(self.context)
        self.register_window.show()
        self.close()

# Register Window - Done
class Register_w(QDialog):
    def __init__(self, context):
        super(Register_w, self).__init__()   
        self.context = context
        ui_path = os.path.join(current_dir, 'ui', 'register.ui')
        if not os.path.exists(ui_path):
            raise FileNotFoundError(f"Không tìm thấy file UI: {ui_path}")
        uic.loadUi(ui_path, self)
        self.setFixedSize(250, 220)
        self.setWindowTitle("MediManager")
        self.setWindowIcon(QtGui.QIcon(icon_path))

        self.login_label.linkActivated.connect(self.goto_login)
        self.register_button.clicked.connect(self.register)
        self.register_button.setDefault(True)

    def register(self):
        un = self.staff_id.text()
        psw = self.staff_psw.text()
        name = self.staff_name.text()
        phone = self.staff_phone.text()
        email = self.staff_email.text()

        try:
            db = self.context.db_manager
            create_sql = """CREATE TABLE IF NOT EXISTS staff (
                        staff_id INT PRIMARY KEY,
                        staff_psw VARCHAR(255),
                        staff_name VARCHAR(255),
                        staff_phone VARCHAR(20),
                        staff_email VARCHAR(50),
                        staff_position VARCHAR(100),
                        staff_salary DECIMAL(10, 0),
                        hire_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    )"""
            db.execute(create_sql)
            db.execute("SELECT staff_id FROM staff WHERE staff_id = %s", (un,))
            if db.fetchone():
                QMessageBox.warning(self, "Lỗi", "Mã nhân viên đã tồn tại. Vui lòng chọn mã khác.")
                return

            insert_sql = """INSERT INTO staff (staff_id, staff_psw, staff_name, staff_phone, staff_email)
                           VALUES (%s, %s, %s, %s, %s)"""
            db.execute(insert_sql, (un, psw, name, phone, email))
            db.commit()

            QMessageBox.information(self, "Register Success", "Đăng ký thành công!")
            self.context.db_manager.log_action(self.context.staff_id, f"Thêm nhân viên: {staff_id}")
            self.staff_id.clear()
            self.staff_psw.clear()
            self.staff_name.clear()
            self.staff_phone.clear()
            self.staff_email.clear()
        except mysql_db.Error as e:
            QMessageBox.critical(self, "Database Error", f"Lỗi đăng ký: {str(e)}")

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.register()

    def goto_login(self):
        self.login_window = Login_w(self.context)
        self.login_window.show()
        self.close()

# Program starts here
if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    icon_dir = os.path.join(current_dir, "icon")
    icon_file = "app_icon_dark.png" if darkdetect.isDark() else "app_icon_light.png"
    icon_path = os.path.join(icon_dir, icon_file)
    context = AppContext()
    app = QApplication(sys.argv)
    login_window = Login_w(context)
    login_window.show()
    sys.exit(app.exec())