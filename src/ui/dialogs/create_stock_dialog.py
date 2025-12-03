"""
Create stock dialog for creating new stock entries
"""

from PyQt6.QtWidgets import (
    QTableWidgetItem, QComboBox, QDoubleSpinBox,
    QSpinBox, QDateEdit, QPushButton
)
from PyQt6.QtCore import Qt, QDate

from src.ui.base import BaseDialog
from src.ui.dialogs.medicine_add_dialog import MedicineAddDialog
from src.utils.constants import MSG_SUCCESS_ADD, MSG_ERROR_ADD


class CreateStockDialog(BaseDialog):
    """Dialog for creating new stock entry"""

    def __init__(self, context, parent=None):
        super().__init__(context, 'create_stock.ui', 'Create Stock Entry', parent)

        # Initialize default values
        self.stock_date.setDate(QDate.currentDate())
        self.staff_name.setText(str(self.context.staff_id))
        self.staff_name.setReadOnly(True)
        self.stock_id.setReadOnly(True)
        self.stock_id.setPlaceholderText("Auto")

        # Load dropdown data
        self.load_supplier_list()
        self.load_medicine_name_list()
        self.load_payment_methods()

        # Connect signals
        self.save_button.clicked.connect(self.save_stock)
        self.cancel_button.clicked.connect(self.reject)
        self.add_medicine.clicked.connect(self.add_row)
        self.add_new_medicine.clicked.connect(self.open_add_medicine_dialog)

        # Setup table
        self.buy_list.setRowCount(0)
        self.buy_list.setColumnCount(7)
        self.buy_list.setHorizontalHeaderLabels([
            "Medicine Name", "Unit Price", "Sale Price", "Quantity",
            "Batch Number", "Expiration Date", "Delete"
        ])
        self.buy_list.cellChanged.connect(self.update_sum_money)

    def load_supplier_list(self):
        """Load supplier list into combo box"""
        try:
            sql = "SELECT supplier_id, supplier_name FROM supplier ORDER BY supplier_name"
            self.db.execute(sql)
            results = self.db.fetchall()

            self.supplier_map = {}
            self.supplier.clear()

            for supplier_id, supplier_name in results:
                self.supplier.addItem(supplier_name)
                self.supplier_map[supplier_name] = supplier_id

        except Exception as e:
            self.show_error(f"Error loading suppliers: {e}")

    def load_payment_methods(self):
        """Load payment methods into combo box"""
        try:
            sql = """
                SELECT payment_method_id, payment_name
                FROM payment_method
                WHERE payment_name IN ('COD', 'prepayment')
                ORDER BY payment_name
            """
            self.db.execute(sql)
            results = self.db.fetchall()

            self.payment_method_map = {}
            self.payment_term.clear()

            for payment_method_id, payment_name in results:
                self.payment_term.addItem(payment_name)
                self.payment_method_map[payment_name] = payment_method_id

        except Exception as e:
            self.show_error(f"Error loading payment methods: {e}")

    def load_medicine_name_list(self):
        """Load medicine names for combo boxes"""
        try:
            sql = "SELECT DISTINCT medicine_name FROM medicine ORDER BY medicine_name"
            self.db.execute(sql)
            results = self.db.fetchall()

            self.medicine_names = [row[0] for row in results] if results else []

        except Exception as e:
            self.show_error(f"Error loading medicine names: {e}")

    def add_row(self):
        """Add a new row to the medicine table"""
        row = self.buy_list.rowCount()
        self.buy_list.insertRow(row)

        # Column 0: Medicine name (combobox)
        combo = QComboBox()
        combo.setEditable(True)
        combo.addItems(self.medicine_names)
        self.buy_list.setCellWidget(row, 0, combo)

        # Column 1: Unit price (spinbox)
        spin_price = QDoubleSpinBox()
        spin_price.setMinimum(0)
        spin_price.setMaximum(1_000_000_000)
        spin_price.setDecimals(2)
        spin_price.valueChanged.connect(lambda _: self.update_sale_price(row))
        self.buy_list.setCellWidget(row, 1, spin_price)

        # Column 2: Sale price (read-only)
        sale_item = QTableWidgetItem("")
        sale_item.setFlags(sale_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.buy_list.setItem(row, 2, sale_item)

        # Column 3: Quantity (spinbox)
        spin_quantity = QSpinBox()
        spin_quantity.setMinimum(1)
        spin_quantity.setMaximum(1_000_000)
        spin_quantity.valueChanged.connect(lambda _: self.update_sum_money())
        self.buy_list.setCellWidget(row, 3, spin_quantity)

        # Column 4: Batch number
        batch_item = QTableWidgetItem("")
        self.buy_list.setItem(row, 4, batch_item)

        # Column 5: Expiration date
        date_exp = QDateEdit()
        date_exp.setCalendarPopup(True)
        date_exp.setDate(QDate.currentDate())
        self.buy_list.setCellWidget(row, 5, date_exp)

        # Column 6: Delete button
        del_btn = QPushButton("X")
        del_btn.clicked.connect(lambda _, r=row: self.remove_row(r))
        self.buy_list.setCellWidget(row, 6, del_btn)

    def remove_row(self, row):
        """Remove a row from the medicine table"""
        self.buy_list.removeRow(row)
        self.update_sum_money()

    def open_add_medicine_dialog(self):
        """Open dialog to add new medicine"""
        dialog = MedicineAddDialog(self.context, self)
        if dialog.exec():
            # Reload medicine names
            self.load_medicine_name_list()

            # Update combo boxes in existing rows
            for row in range(self.buy_list.rowCount()):
                combo = self.buy_list.cellWidget(row, 0)
                if isinstance(combo, QComboBox):
                    current = combo.currentText()
                    combo.clear()
                    combo.addItems(self.medicine_names)
                    idx = combo.findText(current)
                    if idx >= 0:
                        combo.setCurrentIndex(idx)

    def update_sum_money(self):
        """Calculate and update total money"""
        total = 0.0

        for row in range(self.buy_list.rowCount()):
            spin_price = self.buy_list.cellWidget(row, 1)
            spin_quantity = self.buy_list.cellWidget(row, 3)

            if spin_price and spin_quantity:
                total += spin_price.value() * spin_quantity.value()

        self.sum_money.setText(f"{total:,.2f}")

    def update_sale_price(self, row):
        """Auto-calculate sale price (unit price * 1.2)"""
        spin_price = self.buy_list.cellWidget(row, 1)
        sale_item = self.buy_list.item(row, 2)

        if spin_price and sale_item:
            price = spin_price.value()
            sale_price = round(price * 1.2, 2)  # 20% markup
            sale_item.setText(str(sale_price))
            self.update_sum_money()

    def insert_stock(self, supplier_id, staff_id, payment_method_id, stock_date):
        """Insert new stock entry and return stock_id"""
        sql = """
            INSERT INTO stock (supplier_id, staff_id, payment_method_id, created_at)
            VALUES (%s, %s, %s, %s)
        """
        self.db.execute(sql, (supplier_id, staff_id, payment_method_id, stock_date))
        self.db.commit()

        # Get last insert ID (PostgreSQL)
        self.db.execute("SELECT lastval()")
        stock_id = self.db.fetchone()[0]
        return stock_id

    def insert_or_update_medicine(self, medicine_name, supplier_id, quantity,
                                   price, sale_price, batch, exp_date):
        """Insert new medicine or update existing one"""
        # Check if medicine with same name and batch exists
        self.db.execute(
            "SELECT medicine_id FROM medicine WHERE medicine_name = %s AND batch_number = %s",
            (medicine_name, batch)
        )
        med_exist = self.db.fetchone()

        if med_exist:
            # Update existing medicine
            medicine_id = med_exist[0]
            sql = """
                UPDATE medicine SET
                    stock_quantity = stock_quantity + %s,
                    unit_price = %s,
                    sale_price = %s,
                    expiration_date = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE medicine_id = %s
            """
            self.db.execute(sql, (quantity, price, sale_price, exp_date, medicine_id))
            self.db.commit()
        else:
            # Insert new medicine
            sql = """
                INSERT INTO medicine (medicine_name, supplier_id, stock_quantity,
                                     unit_price, sale_price, batch_number, expiration_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            self.db.execute(sql, (medicine_name, supplier_id, quantity,
                                 price, sale_price, batch, exp_date))
            self.db.commit()

            # Get last insert ID
            self.db.execute("SELECT lastval()")
            medicine_id = self.db.fetchone()[0]

        return medicine_id

    def insert_stock_detail(self, stock_id, medicine_id, quantity, price,
                           batch, exp_date, note=""):
        """Insert stock detail record"""
        sql = """
            INSERT INTO stock_detail (stock_id, medicine_id, quantity, price,
                                     batch_number, expiration_date, note)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        self.db.execute(sql, (stock_id, medicine_id, quantity, price, batch, exp_date, note))
        self.db.commit()

    def save_stock(self):
        """Save stock entry to database"""
        try:
            staff_id = self.context.staff_id
            supplier_name = self.supplier.currentText()
            supplier_id = self.supplier_map.get(supplier_name)
            payment_name = self.payment_term.currentText()
            payment_method_id = self.payment_method_map.get(payment_name)
            stock_date = self.stock_date.date().toString("yyyy-MM-dd")

            # Validate
            if not supplier_id:
                self.show_warning("Please select a valid supplier")
                return

            if not payment_method_id:
                self.show_warning("Please select a valid payment method")
                return

            # Insert stock entry
            stock_id = self.insert_stock(supplier_id, staff_id, payment_method_id, stock_date)

            # Process each medicine row
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

                batch_item = self.buy_list.item(row, 4)
                batch = batch_item.text().strip() if batch_item else ""

                exp_widget = self.buy_list.cellWidget(row, 5)
                exp_date = exp_widget.date().toString("yyyy-MM-dd") if exp_widget else None

                # Skip invalid rows
                if not medicine_name or quantity <= 0:
                    continue

                # Insert or update medicine
                medicine_id = self.insert_or_update_medicine(
                    medicine_name, supplier_id, quantity, price, sale_price, batch, exp_date
                )
                medicines.append((medicine_id, quantity, price, batch, exp_date))

            # Validate at least one medicine
            if not medicines:
                # Delete the stock entry if no medicines
                self.db.execute("DELETE FROM stock WHERE stock_id = %s", (stock_id,))
                self.db.commit()
                self.show_warning("Please add at least one valid medicine")
                return

            # Insert stock details
            for medicine_id, quantity, price, batch, exp_date in medicines:
                self.insert_stock_detail(stock_id, medicine_id, quantity, price, batch, exp_date)

            self.log_action(f"Created stock entry: {stock_id}")
            self.show_success(MSG_SUCCESS_ADD)
            self.accept()

        except Exception as e:
            self.db.rollback()
            self.show_error(f"{MSG_ERROR_ADD}: {e}")
