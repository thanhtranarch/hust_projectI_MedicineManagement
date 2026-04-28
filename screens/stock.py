from PyQt6.QtWidgets import QMainWindow, QDialog, QMessageBox, QPushButton, QTableWidgetItem,
    QDialogButtonBox, QVBoxLayout, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox, QLabel
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt, QDate
import os

from utils.helpers import load_ui_file
from constants import ICON_PATH


class StockWindow(QMainWindow):
    def __init__(self, context):
        super().__init__()
        self.context = context
        load_ui_file(self, 'stock.ui')
        self.setWindowTitle("Stock Management")
        self.setWindowIcon(QIcon(ICON_PATH))

        self.back_button.clicked.connect(self.goto_main)
        self.search_input.textChanged.connect(self.search_stock)
        self.tableWidget.cellClicked.connect(self.handle_cell_click)
        self.add_stock.clicked.connect(self.show_create_stock)
        self.tableWidget.setSortingEnabled(True)

        self.load_stock_data()

    def load_stock_data(self):
        try:
            query = """
                SELECT s.stock_id, sd.medicine_id, m.medicine_name, sd.quantity, sd.price,
                       sd.batch_number, sd.expiration_date, sup.supplier_name,
                       s.staff_id, s.created_at
                FROM stock_detail sd
                JOIN stock s ON s.stock_id = sd.stock_id
                JOIN medicine m ON sd.medicine_id = m.medicine_id
                JOIN supplier sup ON s.supplier_id = sup.supplier_id
                ORDER BY s.created_at DESC, s.stock_id DESC
            """
            db = self.context.db
            db.execute(query)
            results = db.fetchall()

            self.tableWidget.setRowCount(len(results))
            self.tableWidget.setColumnCount(10)
            self.tableWidget.setHorizontalHeaderLabels([
                "Stock ID", "Medicine ID", "Medicine Name", "Quantity", "Price",
                "Batch", "Exp. Date", "Supplier", "Staff", "Created At"
            ])
            self.tableWidget.setColumnHidden(0, True)
            self.tableWidget.setColumnHidden(1, True)

            for row_idx, row_data in enumerate(results):
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tableWidget.setItem(row_idx, col_idx, item)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải dữ liệu kho: {e}")

    def search_stock(self):
        keyword = self.search_input.text().strip().lower()
        for row in range(self.tableWidget.rowCount()):
            name_item = self.tableWidget.item(row, 2)
            match = keyword in name_item.text().lower() if name_item else False
            self.tableWidget.setRowHidden(row, not match)

    def handle_cell_click(self, row, column):
        if column == 1 or column == 2:
            item = self.tableWidget.item(row, column)
            medicine_id = self.tableWidget.item(row, 1).text() if item else None
            if medicine_id:
                dialog = StockMedicineDialog(self.context, medicine_id)
                dialog.exec()

    def show_create_stock(self):
        dialog = CreateStockDialog(self.context)
        dialog.exec()

    def goto_main(self):
        from screens.main_window import MainWindow
        self.main_window = MainWindow(self.context)
        self.main_window.show()
        self.close()


class StockMedicineDialog(QDialog):
    def __init__(self, context, medicine_id):
        super().__init__()
        self.context = context
        self.medicine_id = medicine_id
        load_ui_file(self, 'medicine_information.ui')
        self.setWindowTitle("Medicine Information")
        self.setWindowIcon(QIcon(ICON_PATH))
        # Reuse MedicineDetailDialog if available


class CreateStockDialog(QDialog):
    def __init__(self, context):
        super().__init__()
        self.context = context
        load_ui_file(self, 'create_stock.ui')
        self.setWindowTitle("Create Stock Entry")
        self.setWindowIcon(QIcon(ICON_PATH))

        self.stock_date.setDate(QDate.currentDate())
        self.staff_name.setText(str(self.context.staff_id))
        self.staff_name.setReadOnly(True)
        self.stock_id.setReadOnly(True)
        self.stock_id.setPlaceholderText("Auto")

        self.save_button.clicked.connect(self.save_stock)
        self.cancel_button.clicked.connect(self.reject)
        self.add_medicine.clicked.connect(self.add_row)

        self.load_supplier_list()
        self.load_payment_methods()
        self.load_medicine_names()
        self.setup_table()

    def load_supplier_list(self):
        db = self.context.db
        db.execute("SELECT supplier_id, supplier_name FROM supplier")
        results = db.fetchall()
        self.supplier_map = {name: sid for sid, name in results}
        self.supplier.clear()
        self.supplier.addItems(self.supplier_map.keys())

    def load_payment_methods(self):
        db = self.context.db
        db.execute("SELECT payment_method_id, payment_name FROM payment_method")
        results = db.fetchall()
        self.payment_map = {name: pid for pid, name in results}
        self.payment_term.clear()
        self.payment_term.addItems(self.payment_map.keys())

    def load_medicine_names(self):
        db = self.context.db
        db.execute("SELECT DISTINCT medicine_name FROM medicine")
        results = db.fetchall()
        self.medicine_names = [row[0] for row in results]

    def setup_table(self):
        self.buy_list.setColumnCount(6)
        self.buy_list.setHorizontalHeaderLabels([
            "Tên thuốc", "Giá nhập", "Số lượng", "Số lô", "Hạn dùng", "Xóa"
        ])
        self.buy_list.setRowCount(0)

    def add_row(self):
        row = self.buy_list.rowCount()
        self.buy_list.insertRow(row)

        combo = QComboBox()
        combo.setEditable(True)
        combo.addItems(self.medicine_names)
        self.buy_list.setCellWidget(row, 0, combo)

        price_input = QDoubleSpinBox()
        price_input.setMinimum(0)
        price_input.setMaximum(1_000_000_000)
        self.buy_list.setCellWidget(row, 1, price_input)

        qty_input = QSpinBox()
        qty_input.setMinimum(1)
        self.buy_list.setCellWidget(row, 2, qty_input)

        self.buy_list.setCellWidget(row, 3, QComboBox())  # Số lô
        date_edit = QDateEdit()
        date_edit.setDate(QDate.currentDate())
        date_edit.setCalendarPopup(True)
        self.buy_list.setCellWidget(row, 4, date_edit)

        del_btn = QPushButton("X")
        del_btn.clicked.connect(lambda _, r=row: self.remove_row(r))
        self.buy_list.setCellWidget(row, 5, del_btn)

    def remove_row(self, row):
        self.buy_list.removeRow(row)

    def save_stock(self):
        try:
            db = self.context.db
            supplier_name = self.supplier.currentText()
            payment_name = self.payment_term.currentText()
            supplier_id = self.supplier_map.get(supplier_name)
            payment_id = self.payment_map.get(payment_name)
            staff_id = self.context.staff_id
            stock_date = self.stock_date.date().toString("yyyy-MM-dd")

            db.execute("""
                INSERT INTO stock (supplier_id, staff_id, payment_method_id, created_at)
                VALUES (%s, %s, %s, %s)
            """, (supplier_id, staff_id, payment_id, stock_date))
            db.commit()

            db.execute("SELECT LAST_INSERT_ID()")
            stock_id = db.fetchone()[0]

            for row in range(self.buy_list.rowCount()):
                name = self.buy_list.cellWidget(row, 0).currentText()
                price = self.buy_list.cellWidget(row, 1).value()
                qty = self.buy_list.cellWidget(row, 2).value()
                batch = self.buy_list.cellWidget(row, 3).currentText()
                exp_date = self.buy_list.cellWidget(row, 4).date().toString("yyyy-MM-dd")

                db.execute("SELECT medicine_id FROM medicine WHERE medicine_name = %s AND batch_number = %s",
                           (name, batch))
                med = db.fetchone()
                if med:
                    medicine_id = med[0]
                    db.execute("""
                        UPDATE medicine SET stock_quantity = stock_quantity + %s,
                                           unit_price = %s,
                                           expiration_date = %s
                        WHERE medicine_id = %s
                    """, (qty, price, exp_date, medicine_id))
                else:
                    db.execute("""
                        INSERT INTO medicine (medicine_name, supplier_id, stock_quantity,
                                              unit_price, batch_number, expiration_date)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (name, supplier_id, qty, price, batch, exp_date))
                    db.commit()
                    db.execute("SELECT LAST_INSERT_ID()")
                    medicine_id = db.fetchone()[0]

                db.execute("""
                    INSERT INTO stock_detail (stock_id, medicine_id, quantity, price,
                                              batch_number, expiration_date)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (stock_id, medicine_id, qty, price, batch, exp_date))

            db.commit()
            db.log_action(staff_id, f"Tạo phiếu nhập kho: {stock_id}")
            QMessageBox.information(self, "Thành công", "Đã lưu phiếu nhập kho thành công.")
            self.accept()

        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu phiếu nhập kho: {e}")
