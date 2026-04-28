from PyQt6.QtWidgets import QMainWindow, QDialog, QMessageBox, QPushButton, QTableWidgetItem,
    QDialogButtonBox, QVBoxLayout, QComboBox, QLabel, QSpinBox, QDoubleSpinBox, QDateEdit
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt, pyqtSignal, QDate
import os

from utils.helpers import load_ui_file
from constants import ICON_PATH


class MedicineWindow(QMainWindow):
    def __init__(self, context):
        super().__init__()
        self.context = context
        load_ui_file(self, 'medicine.ui')
        self.setWindowTitle("Medicine Management")
        self.setWindowIcon(QIcon(ICON_PATH))

        self.back_button.clicked.connect(self.goto_main)
        self.search_input.textChanged.connect(self.search_medicine)
        self.tableWidget.cellClicked.connect(self.handle_cell_click)
        self.tableWidget.setSortingEnabled(True)

        self.load_medicine_data()

    def load_medicine_data(self):
        try:
            query = """
                SELECT m.medicine_id, m.medicine_name, c.category_name, m.created_at, m.updated_at
                FROM medicine m
                JOIN category c ON m.category_id = c.category_id
            """
            db = self.context.db
            db.execute(query)
            results = db.fetchall()

            self.tableWidget.setRowCount(len(results))
            self.tableWidget.setColumnCount(6)
            self.tableWidget.setHorizontalHeaderLabels(["ID", "Name", "Category", "Created At", "Updated At", "Details"])
            self.tableWidget.setColumnWidth(1, 200)
            self.tableWidget.setColumnWidth(2, 150)
            self.tableWidget.setColumnWidth(3, 150)

            for row_idx, row_data in enumerate(results):
                medicine_id = row_data[0]
                for col_idx in range(6):
                    if col_idx < len(row_data):
                        item = QTableWidgetItem(str(row_data[col_idx]))
                        if col_idx == 1:
                            font = QFont()
                            font.setUnderline(True)
                            item.setFont(font)
                            item.setToolTip("Click để xem chi tiết thuốc")
                            item.setData(Qt.ItemDataRole.UserRole, medicine_id)
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        self.tableWidget.setItem(row_idx, col_idx, item)
                    else:
                        detail_item = QTableWidgetItem("View Details")
                        font = QFont()
                        font.setUnderline(True)
                        detail_item.setFont(font)
                        detail_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        detail_item.setData(Qt.ItemDataRole.UserRole, medicine_id)
                        self.tableWidget.setItem(row_idx, col_idx, detail_item)
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể tải danh sách thuốc: {e}")

    def handle_cell_click(self, row, column):
        if column == 1 or column == 5:
            item = self.tableWidget.item(row, column)
            if item:
                medicine_id = item.data(Qt.ItemDataRole.UserRole)
                if medicine_id:
                    dialog = MedicineDetailDialog(self.context, medicine_id)
                    dialog.data_updated.connect(self.load_medicine_data)
                    dialog.exec()

    def search_medicine(self):
        keyword = self.search_input.text().strip().lower()
        for row in range(self.tableWidget.rowCount()):
            name_item = self.tableWidget.item(row, 1)
            match = keyword in name_item.text().lower() if name_item else False
            self.tableWidget.setRowHidden(row, not match)

    def goto_main(self):
        from screens.main_window import MainWindow
        self.main_window = MainWindow(self.context)
        self.main_window.show()
        self.close()


class MedicineDetailDialog(QDialog):
    data_updated = pyqtSignal()

    def __init__(self, context, medicine_id):
        super().__init__()
        self.context = context
        self.medicine_id = medicine_id
        self.edit_mode = False

        load_ui_file(self, 'medicine_information.ui')
        self.setWindowTitle("Medicine Detail")
        self.setWindowIcon(QIcon(ICON_PATH))

        self.pushButton.clicked.connect(self.toggle_edit_mode)
        self.deleteButton.clicked.connect(self.confirm_delete)
        self.deleteButton.setEnabled(False)

        self.load_medicine_data()

    def load_medicine_data(self):
        try:
            db = self.context.db
            query = """
                SELECT m.medicine_id, m.medicine_name, m.generic_name, c.category_name, s.supplier_name,
                       m.batch_number, m.expiration_date, m.stock_quantity, m.unit_price, m.sale_price
                FROM medicine m
                JOIN category c ON m.category_id = c.category_id
                JOIN supplier s ON m.supplier_id = s.supplier_id
                WHERE m.medicine_id = %s
            """
            db.execute(query, (self.medicine_id,))
            result = db.fetchone()

            if result:
                self.medicine_id_field.setText(str(result[0]))
                self.medicine_name.setText(result[1])
                self.generic_name.setText(result[2])
                self.category_name.setText(result[3])
                self.supplier_name.setText(result[4])
                self.batch_number.setText(result[5])
                self.expiration_date.setDate(result[6].date())
                self.stock_quantity.setValue(result[7])
                self.unit_price.setValue(float(result[8]))
                self.sale_price.setValue(float(result[9]))
                self.set_fields_editable(False)
            else:
                QMessageBox.warning(self, "Lỗi", "Không tìm thấy thuốc.")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải dữ liệu: {e}")

    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode
        self.set_fields_editable(self.edit_mode)
        self.pushButton.setText("💾 Save" if self.edit_mode else "Edit...")
        self.deleteButton.setEnabled(self.edit_mode)

        if self.edit_mode:
            self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel)
            self.original_data = {
                "name": self.medicine_name.text(),
                "generic": self.generic_name.text(),
                "batch": self.batch_number.text(),
                "exp_date": self.expiration_date.date(),
                "quantity": self.stock_quantity.value(),
                "unit_price": self.unit_price.value(),
                "sale_price": self.sale_price.value()
            }
            cancel_btn = self.buttonBox.button(QDialogButtonBox.StandardButton.Cancel)
            if cancel_btn:
                cancel_btn.clicked.connect(self.cancel_edit)
        else:
            self.save_medicine_data()
            self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Ok)

    def set_fields_editable(self, editable):
        self.medicine_name.setReadOnly(not editable)
        self.generic_name.setReadOnly(not editable)
        self.batch_number.setReadOnly(not editable)
        self.expiration_date.setEnabled(editable)
        self.stock_quantity.setEnabled(editable)
        self.unit_price.setEnabled(editable)
        self.sale_price.setEnabled(editable)

    def save_medicine_data(self):
        try:
            db = self.context.db
            query = """
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
                self.medicine_id_field.text()
            )
            db.execute(query, values)
            db.commit()
            db.log_action(self.context.staff_id, f"Cập nhật thuốc: {self.medicine_id_field.text()}")
            self.data_updated.emit()
            QMessageBox.information(self, "Thành công", "Đã lưu thông tin thuốc.")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể lưu: {e}")

    def cancel_edit(self):
        self.medicine_name.setText(self.original_data["name"])
        self.generic_name.setText(self.original_data["generic"])
        self.batch_number.setText(self.original_data["batch"])
        self.expiration_date.setDate(self.original_data["exp_date"])
        self.stock_quantity.setValue(self.original_data["quantity"])
        self.unit_price.setValue(self.original_data["unit_price"])
        self.sale_price.setValue(self.original_data["sale_price"])

        self.set_fields_editable(False)
        self.edit_mode = False
        self.pushButton.setText("Edit...")
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Ok)
        QMessageBox.information(self, "Đã hủy", "Chỉnh sửa đã được hủy.")

    def confirm_delete(self):
        reply = QMessageBox.question(
            self, "Xác nhận xóa", "Bạn có chắc chắn muốn xóa thuốc này?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.delete_medicine()

    def delete_medicine(self):
        try:
            db = self.context.db
            db.execute("DELETE FROM medicine WHERE medicine_id = %s", (self.medicine_id_field.text(),))
            db.commit()
            db.log_action(self.context.staff_id, f"Xóa thuốc: {self.medicine_id_field.text()}")
            QMessageBox.information(self, "Đã xóa", "Đã xóa thuốc khỏi hệ thống.")
            self.data_updated.emit()
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể xóa thuốc: {e}")
