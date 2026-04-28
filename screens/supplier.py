from PyQt6.QtWidgets import QMainWindow, QLabel, QDialog, QDialogButtonBox, QVBoxLayout, QComboBox,
    QPushButton, QTableWidgetItem, QMessageBox, QLineEdit, QTextEdit, QToolButton
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt
import os

from utils.helpers import load_ui_file
from constants import ICON_PATH


class SupplierWindow(QMainWindow):
    def __init__(self, context):
        super().__init__()
        self.context = context
        load_ui_file(self, 'supplier.ui')
        self.setWindowTitle("Supplier Management")
        self.setWindowIcon(QIcon(ICON_PATH))

        self.back_button.clicked.connect(self.goto_main)
        self.search_input.textChanged.connect(self.search_supplier)
        self.tableWidget.setSortingEnabled(True)
        self.tableWidget.cellClicked.connect(self.handle_cell_click)

        self.load_supplier_data()

    def load_supplier_data(self):
        try:
            db = self.context.db
            query = "SELECT supplier_id, supplier_name, created_at, updated_at FROM supplier"
            db.execute(query)
            results = db.fetchall()

            self.tableWidget.setRowCount(len(results))
            self.tableWidget.setColumnCount(5)
            self.tableWidget.setColumnHidden(0, True)
            self.tableWidget.setColumnWidth(1, 300)
            self.tableWidget.setColumnWidth(2, 150)
            self.tableWidget.setColumnWidth(3, 150)
            self.tableWidget.setColumnWidth(4, 200)

            for row_idx, row_data in enumerate(results):
                supplier_id = row_data[0]
                for col_idx in range(5):
                    if col_idx < len(row_data):
                        item = QTableWidgetItem(str(row_data[col_idx]))
                        if col_idx == 1:
                            font = QFont()
                            font.setBold(True)
                            font.setUnderline(True)
                            item.setFont(font)
                            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                            item.setToolTip("Click để xem chi tiết nhà cung cấp")
                            item.setData(Qt.ItemDataRole.UserRole, supplier_id)
                        self.tableWidget.setItem(row_idx, col_idx, item)
                    else:
                        detail_item = QTableWidgetItem("View Details")
                        font = QFont()
                        font.setUnderline(True)
                        detail_item.setFont(font)
                        detail_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        detail_item.setData(Qt.ItemDataRole.UserRole, supplier_id)
                        self.tableWidget.setItem(row_idx, col_idx, detail_item)
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể tải nhà cung cấp: {e}")

    def search_supplier(self):
        keyword = self.search_input.text().strip().lower()
        for row in range(self.tableWidget.rowCount()):
            name_item = self.tableWidget.item(row, 1)
            match = keyword in name_item.text().lower() if name_item else False
            self.tableWidget.setRowHidden(row, not match)

    def handle_cell_click(self, row, column):
        if column == 1 or column == 4:
            item = self.tableWidget.item(row, column)
            if item:
                supplier_id = item.data(Qt.ItemDataRole.UserRole)
                if supplier_id:
                    dialog = SupplierDetailDialog(self.context, supplier_id)
                    dialog.exec()

    def goto_main(self):
        from screens.main_window import MainWindow
        self.main_window = MainWindow(self.context)
        self.main_window.show()
        self.close()


class SupplierDetailDialog(QDialog):
    def __init__(self, context, supplier_id):
        super().__init__()
        self.context = context
        self.supplier_id_value = supplier_id
        self.edit_mode = False
        load_ui_file(self, 'supplier_information.ui')

        self.setWindowTitle("Supplier Detail")
        self.setWindowIcon(QIcon(ICON_PATH))

        self.pushButton.clicked.connect(self.toggle_edit_mode)
        self.load_supplier_data()

    def load_supplier_data(self):
        try:
            db = self.context.db
            query = """
                SELECT supplier_id, supplier_name, supplier_address, contact_name,
                       contact_phone, contact_email, payment_terms
                FROM supplier WHERE supplier_id = %s
            """
            db.execute(query, (self.supplier_id_value,))
            result = db.fetchone()

            if result:
                self.supplier_id.setText(str(result[0]))
                self.supplier_name.setText(result[1] or "")
                self.supplier_address.setPlainText(result[2] or "")
                self.contact_name.setText(result[3] or "")
                self.contact_phone.setText(result[4] or "")
                self.contact_email.setText(result[5] or "")
                self.comboBox_payment_terms.setCurrentText(result[6] or "")
                self.set_fields_editable(False)
            else:
                QMessageBox.warning(self, "Thông báo", "Không tìm thấy nhà cung cấp.")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải dữ liệu: {e}")

    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode
        self.set_fields_editable(self.edit_mode)
        self.pushButton.setText("💾 Save" if self.edit_mode else "Edit...")

        if self.edit_mode:
            self.original_data = {
                "name": self.supplier_name.text(),
                "address": self.supplier_address.toPlainText(),
                "contact": self.contact_name.text(),
                "phone": self.contact_phone.text(),
                "email": self.contact_email.text(),
                "payment": self.comboBox_payment_terms.currentText()
            }
            self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel)
            cancel_btn = self.buttonBox.button(QDialogButtonBox.StandardButton.Cancel)
            if cancel_btn:
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
            db = self.context.db
            query = """
                UPDATE supplier SET
                    supplier_name = %s,
                    supplier_address = %s,
                    contact_name = %s,
                    contact_phone = %s,
                    contact_email = %s,
                    payment_terms = %s
                WHERE supplier_id = %s
            """
            values = (
                self.supplier_name.text(),
                self.supplier_address.toPlainText(),
                self.contact_name.text(),
                self.contact_phone.text(),
                self.contact_email.text(),
                self.comboBox_payment_terms.currentText().strip() or "COD",
                self.supplier_id.text()
            )
            db.execute(query, values)
            db.commit()
            db.log_action(self.context.staff_id, f"Cập nhật nhà cung cấp: {self.supplier_id.text()}")
            QMessageBox.information(self, "Thành công", "Đã lưu thông tin nhà cung cấp.")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể lưu: {e}")

    def cancel_edit(self):
        for field, value in self.original_data.items():
            if field == "address":
                self.supplier_address.setPlainText(value)
            elif field == "payment":
                self.comboBox_payment_terms.setCurrentText(value)
            else:
                getattr(self, f"supplier_{field}").setText(value)

        self.set_fields_editable(False)
        self.edit_mode = False
        self.pushButton.setText("Edit...")
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Ok)
        QMessageBox.information(self, "Đã hủy", "Thay đổi đã được hủy.")
