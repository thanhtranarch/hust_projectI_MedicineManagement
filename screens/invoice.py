from PyQt6.QtWidgets import QMainWindow, QDialog, QTableWidgetItem, QMessageBox, QComboBox, QPushButton, QDateEdit, QSpinBox, QDoubleSpinBox, QInputDialog
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt, QDate

from utils.helpers import load_ui_file
from constants import ICON_PATH


class InvoiceWindow(QMainWindow):
    def __init__(self, context):
        super().__init__()
        self.context = context
        load_ui_file(self, 'invoice.ui')
        self.setWindowTitle("Invoice Management")
        self.setWindowIcon(QIcon(ICON_PATH))
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.back_button.clicked.connect(self.goto_main)
        self.create_invoice.clicked.connect(self.open_create_dialog)
        self.tableWidget.cellClicked.connect(self.handle_cell_click)
        self.load_invoice_data()

    def load_invoice_data(self):
        try:
            query = "SELECT invoice_id, customer_id, total_amount, created_at FROM invoice"
            db = self.context.db
            db.execute(query)
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
            dialog = InvoiceDetailDialog(self.context, invoice_id)
            dialog.exec()

    def open_create_dialog(self):
        dialog = CreateInvoiceDialog(self.context)
        dialog.exec()

    def goto_main(self):
        from screens.main_window import MainWindow
        self.main_window = MainWindow(self.context)
        self.main_window.show()
        self.close()


class InvoiceDetailDialog(QDialog):
    def __init__(self, context, invoice_id):
        super().__init__()
        self.context = context
        self.invoice_id = invoice_id
        load_ui_file(self, 'create_invoice.ui')
        self.setWindowTitle("Invoice Detail")
        self.setWindowIcon(QIcon(ICON_PATH))

        self.set_fields_readonly()
        self.load_invoice_info()

        self.cancel_button.clicked.connect(self.accept)

    def set_fields_readonly(self):
        self.save_button.setDisabled(True)
        self.add_medicine.setDisabled(True)
        self.add_medicine_2.setDisabled(True)
        self.customer_phone.setReadOnly(True)
        self.staff_name.setReadOnly(True)
        self.invoice_date.setReadOnly(True)
        self.payment_term.setDisabled(True)
        self.buy_list.setEditTriggers(QTableWidgetItem.EditTrigger.NoEditTriggers)
        self.buy_list.setSelectionMode(QTableWidgetItem.SelectionMode.NoSelection)

    def load_invoice_info(self):
        try:
            db = self.context.db
            db.execute("""
                SELECT invoice_id, invoice_date, customer_id, staff_id, total_amount, payment_method_id
                FROM invoice WHERE invoice_id = %s
            """, (self.invoice_id,))
            info = db.fetchone()

            if not info:
                QMessageBox.warning(self, "Lỗi", "Không tìm thấy hóa đơn!")
                self.reject()
                return

            self.invoice_id_field.setText(str(info[0]))
            self.invoice_date.setDate(info[1])
            self.staff_name.setText(str(info[3]))
            self.sum_money.setText(str(info[4]))
            self.payment_term.setCurrentIndex(self.payment_term.findData(info[5]))

            db.execute("SELECT customer_name, customer_phone FROM customer WHERE customer_id = %s", (info[2],))
            customer = db.fetchone()
            if customer:
                self.customer_phone.setText(customer[1])
                self.label_6.setText(f"{customer[0]} ({customer[1]})")

            db.execute("""
                SELECT m.medicine_id, m.medicine_name, m.unit, d.sale_price, d.quantity, d.total_price
                FROM invoice_detail d
                JOIN medicine m ON d.medicine_id = m.medicine_id
                WHERE d.invoice_id = %s
            """, (self.invoice_id,))
            items = db.fetchall()

            self.buy_list.setRowCount(len(items))
            self.buy_list.setColumnCount(6)
            self.buy_list.setHorizontalHeaderLabels(["Tên thuốc", "Đơn vị", "Giá bán", "Số lượng", "Thành tiền", "ID"])
            self.buy_list.setColumnHidden(5, True)

            for i, item in enumerate(items):
                self.buy_list.setItem(i, 0, QTableWidgetItem(str(item[1])))
                self.buy_list.setItem(i, 1, QTableWidgetItem(str(item[2])))
                self.buy_list.setItem(i, 2, QTableWidgetItem(str(item[3])))
                self.buy_list.setItem(i, 3, QTableWidgetItem(str(item[4])))
                self.buy_list.setItem(i, 4, QTableWidgetItem(str(item[5])))
                self.buy_list.setItem(i, 5, QTableWidgetItem(str(item[0])))
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Lỗi khi tải thông tin hóa đơn: {e}")


class CreateInvoiceDialog(QDialog):
    def __init__(self, context):
        super().__init__()
        self.context = context
        self.medicine_list = []
        load_ui_file(self, 'create_invoice.ui')
        self.setWindowTitle("Create Invoice")
        self.setWindowIcon(QIcon(ICON_PATH))

        self.invoice_date.setDate(QDate.currentDate())
        self.invoice_date.setEnabled(False)
        self.invoice_id_field.setText("Tự động")
        self.invoice_id_field.setEnabled(False)
        self.staff_name.setText(str(self.context.staff_id))
        self.staff_name.setReadOnly(True)

        self.customer_phone.editingFinished.connect(self.lookup_customer)
        self.add_medicine.clicked.connect(self.select_medicine)
        self.save_button.clicked.connect(self.save_invoice)
        self.cancel_button.clicked.connect(self.reject)

        self.load_payment_methods()

    def load_payment_methods(self):
        db = self.context.db
        db.execute("SELECT payment_method_id, payment_name FROM payment_method")
        results = db.fetchall()
        self.payment_term.clear()
        for pid, name in results:
            self.payment_term.addItem(name, pid)

    def lookup_customer(self):
        phone = self.customer_phone.text().strip()
        db = self.context.db
        db.execute("SELECT customer_id, customer_name FROM customer WHERE customer_phone = %s", (phone,))
        customer = db.fetchone()
        if customer:
            self.customer_id = customer[0]
            self.label_6.setText(f"{customer[1]} ({phone})")
        else:
            name, ok = QInputDialog.getText(self, "Thêm khách hàng", "Tên khách hàng mới:")
            if ok and name.strip():
                db.execute("INSERT INTO customer (customer_name, customer_phone) VALUES (%s, %s)", (name.strip(), phone))
                db.commit()
                db.execute("SELECT customer_id FROM customer WHERE customer_phone = %s", (phone,))
                self.customer_id = db.fetchone()[0]
                self.label_6.setText(f"{name.strip()} ({phone})")
            else:
                self.customer_id = None
                QMessageBox.warning(self, "Thiếu thông tin", "Bạn cần nhập tên khách hàng.")

    def select_medicine(self):
        db = self.context.db
        db.execute("SELECT medicine_id, medicine_name, unit, sale_price, stock_quantity FROM medicine")
        meds = db.fetchall()
        if not meds:
            QMessageBox.warning(self, "Không có thuốc", "Danh sách thuốc trống.")
            return

        items = [f"{m[1]} - {m[2]} - {m[3]} - SL: {m[4]}" for m in meds]
        choice, ok = QInputDialog.getItem(self, "Chọn thuốc", "Chọn:", items, 0, False)
        if ok:
            index = items.index(choice)
            med = meds[index]
            qty, ok = QInputDialog.getInt(self, "Số lượng", f"Nhập số lượng (1 - {med[4]}):", 1, 1, med[4])
            if ok:
                total = qty * float(med[3])
                self.medicine_list.append((med[0], med[1], med[2], med[3], qty, total))
                self.refresh_table()

    def refresh_table(self):
        self.buy_list.setRowCount(len(self.medicine_list))
        for i, m in enumerate(self.medicine_list):
            self.buy_list.setItem(i, 0, QTableWidgetItem(m[1]))
            self.buy_list.setItem(i, 1, QTableWidgetItem(m[2]))
            self.buy_list.setItem(i, 2, QTableWidgetItem(str(m[3])))
            self.buy_list.setItem(i, 3, QTableWidgetItem(str(m[4])))
            self.buy_list.setItem(i, 4, QTableWidgetItem(str(m[5])))
            self.buy_list.setItem(i, 5, QTableWidgetItem(str(m[0])))
        self.buy_list.setColumnHidden(5, True)
        self.update_total()

    def update_total(self):
        total = sum(m[5] for m in self.medicine_list)
        self.sum_money.setText(str(total))

    def save_invoice(self):
        if not hasattr(self, 'customer_id') or not self.medicine_list:
            QMessageBox.warning(self, "Thiếu thông tin", "Hãy nhập đủ thông tin khách hàng và thuốc.")
            return

        db = self.context.db
        try:
            date = self.invoice_date.date().toString("yyyy-MM-dd")
            staff_id = self.context.staff_id
            payment_id = self.payment_term.currentData()
            total = float(self.sum_money.text())

            db.execute("""
                INSERT INTO invoice (invoice_date, customer_id, staff_id, total_amount, payment_method_id, payment_status)
                VALUES (%s, %s, %s, %s, %s, 'Đã thanh toán')
            """, (date, self.customer_id, staff_id, total, payment_id))
            db.commit()
            db.execute("SELECT LAST_INSERT_ID()")
            invoice_id = db.fetchone()[0]

            for m in self.medicine_list:
                db.execute("""
                    INSERT INTO invoice_detail (invoice_id, medicine_id, quantity, sale_price, total_price)
                    VALUES (%s, %s, %s, %s, %s)
                """, (invoice_id, m[0], m[4], m[3], m[5]))
                db.execute("UPDATE medicine SET stock_quantity = stock_quantity - %s WHERE medicine_id = %s", (m[4], m[0]))

            db.commit()
            db.log_action(staff_id, f"Tạo hóa đơn: {invoice_id}")
            QMessageBox.information(self, "Thành công", f"Đã lưu hóa đơn #{invoice_id}")
            self.accept()

        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Lỗi", f"Lưu hóa đơn thất bại: {e}")
