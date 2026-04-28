from PyQt6.QtWidgets import QMainWindow, QDialog, QTableWidgetItem, QMessageBox, QPushButton, QLineEdit, QDialogButtonBox
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt

from utils.helpers import load_ui_file
from constants import ICON_PATH


class CustomerWindow(QMainWindow):
    def __init__(self, context):
        super().__init__()
        self.context = context
        load_ui_file(self, 'customer.ui')
        self.setWindowTitle("Customer Management")
        self.setWindowIcon(QIcon(ICON_PATH))
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.back_button.clicked.connect(self.goto_main)
        self.search_input.textChanged.connect(self.search_customer)
        self.tableWidget.cellClicked.connect(self.handle_cell_click)
        self.tableWidget.setSortingEnabled(True)

        self.load_customer_data()

    def load_customer_data(self):
        try:
            db = self.context.db
            query = "SELECT customer_id, customer_name, customer_phone, customer_email FROM customer"
            db.execute(query)
            results = db.fetchall()

            self.tableWidget.setRowCount(len(results))
            self.tableWidget.setColumnCount(5)
            self.tableWidget.setHorizontalHeaderLabels(["ID", "Name", "Phone", "Email", "Details"])
            self.tableWidget.setColumnHidden(0, True)

            for row_idx, row_data in enumerate(results):
                customer_id = row_data[0]
                for col_idx in range(4):
                    item = QTableWidgetItem(str(row_data[col_idx]))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    if col_idx == 1:
                        font = QFont()
                        font.setBold(True)
                        font.setUnderline(True)
                        item.setFont(font)
                        item.setData(Qt.ItemDataRole.UserRole, customer_id)
                        item.setToolTip("Click để xem chi tiết khách hàng")
                    self.tableWidget.setItem(row_idx, col_idx, item)

                detail_item = QTableWidgetItem("View Details")
                font = QFont()
                font.setUnderline(True)
                detail_item.setFont(font)
                detail_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                detail_item.setData(Qt.ItemDataRole.UserRole, customer_id)
                detail_item.setToolTip("Click để xem chi tiết khách hàng")
                self.tableWidget.setItem(row_idx, 4, detail_item)
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể tải dữ liệu khách hàng: {e}")

    def search_customer(self):
        keyword = self.search_input.text().strip().lower()
        for row in range(self.tableWidget.rowCount()):
            name_item = self.tableWidget.item(row, 1)
            match = keyword in name_item.text().lower() if name_item else False
            self.tableWidget.setRowHidden(row, not match)

    def handle_cell_click(self, row, column):
        if column == 1 or column == 4:
            item = self.tableWidget.item(row, column)
            if item:
                customer_id = item.data(Qt.ItemDataRole.UserRole)
                dialog = CustomerDetailDialog(self.context, customer_id)
                dialog.exec()

    def goto_main(self):
        from screens.main_window import MainWindow
        self.main_window = MainWindow(self.context)
        self.main_window.show()
        self.close()


class CustomerDetailDialog(QDialog):
    def __init__(self, context, customer_id):
        super().__init__()
        self.context = context
        self.customer_id_value = customer_id
        self.edit_mode = False

        load_ui_file(self, 'customer_information.ui')
        self.setWindowTitle("Customer Information")
        self.setWindowIcon(QIcon(ICON_PATH))

        self.edit_button = QPushButton("Edit...", self)
        self.edit_button.setGeometry(80, 445, 80, 28)
        self.edit_button.clicked.connect(self.toggle_edit_mode)

        self.set_fields_editable(False)
        self.load_customer_data()

    def load_customer_data(self):
        try:
            db = self.context.db
            db.execute("SELECT customer_id, customer_name, customer_phone, customer_email FROM customer WHERE customer_id = %s", (self.customer_id_value,))
            result = db.fetchone()

            if result:
                self.customer_id.setText(str(result[0]))
                self.customer_name.setText(result[1])
                self.customer_phone.setText(result[2])
                self.customer_email.setText(result[3])
            else:
                QMessageBox.warning(self, "Thông báo", "Không tìm thấy khách hàng.")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể tải dữ liệu: {e}")

    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode
        self.set_fields_editable(self.edit_mode)
        self.edit_button.setText("💾 Save" if self.edit_mode else "Edit...")

        if self.edit_mode:
            self.original_data = {
                "name": self.customer_name.text(),
                "phone": self.customer_phone.text(),
                "email": self.customer_email.text()
            }
            self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel)
            cancel_btn = self.buttonBox.button(QDialogButtonBox.StandardButton.Cancel)
            if cancel_btn:
                cancel_btn.clicked.connect(self.cancel_edit)
        else:
            self.save_customer_data()
            self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Ok)

    def save_customer_data(self):
        try:
            db = self.context.db
            query = """
                UPDATE customer SET
                    customer_name = %s,
                    customer_phone = %s,
                    customer_email = %s
                WHERE customer_id = %s
            """
            values = (
                self.customer_name.text(),
                self.customer_phone.text(),
                self.customer_email.text(),
                self.customer_id.text()
            )
            db.execute(query, values)
            db.commit()
            db.log_action(self.context.staff_id, f"Cập nhật khách hàng: {self.customer_id.text()}")
            QMessageBox.information(self, "Thành công", "Đã cập nhật thông tin khách hàng.")
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
