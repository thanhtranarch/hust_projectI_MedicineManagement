"""
Create invoice dialog for creating new invoices
"""

from PyQt6.QtWidgets import (
    QTableWidgetItem, QPushButton, QInputDialog
)
from PyQt6.QtCore import QDate

from src.ui.base import BaseDialog
from src.utils.constants import MSG_SUCCESS_ADD, MSG_ERROR_ADD


class CreateInvoiceDialog(BaseDialog):
    """Dialog for creating new invoice with customer and medicine selection"""

    def __init__(self, context, invoice_id=None, parent=None):
        super().__init__(context, 'create_invoice.ui', 'Create Invoice', parent)

        self.invoice_id_param = invoice_id  # None for new, int for view/edit
        self.customer_id = None
        self.medicine_list = []  # [(medicine_id, name, unit, sale_price, quantity, total_price)]

        # Set default values
        self.invoice_date.setDate(QDate.currentDate())
        self.invoice_date.setReadOnly(True)
        self.invoice_date.setEnabled(False)
        self.staff_name.setText(str(self.context.staff_id))
        self.staff_name.setReadOnly(True)
        self.invoice_id.setText("Auto")
        self.invoice_id.setReadOnly(True)
        self.invoice_id.setEnabled(False)

        # Load payment methods
        self.load_payment_methods()

        # Connect signals
        self.customer_phone.editingFinished.connect(self.lookup_customer)
        self.add_medicine.clicked.connect(self.show_add_medicine_dialog)
        self.add_medicine_2.clicked.connect(self.create_new_customer)
        self.save_button.clicked.connect(self.save_invoice)
        self.cancel_button.clicked.connect(self.reject)

    def load_payment_methods(self):
        """Load payment methods into combo box"""
        try:
            sql = """
                SELECT payment_method_id, payment_name
                FROM payment_method
                WHERE method_type = 'sale'
                ORDER BY payment_name
            """
            self.db.execute(sql)
            results = self.db.fetchall()

            self.payment_term.clear()
            self.payment_methods_map = {}

            for pid, name in results:
                self.payment_term.addItem(name, pid)
                self.payment_methods_map[name] = pid

        except Exception as e:
            self.show_error(f"Error loading payment methods: {e}")

    def _set_customer(self, customer_id, label, valid=True):
        """Update the selected customer and the phone field's status colour."""
        self.customer_id = customer_id
        self.label_6.setText(label)
        self.customer_phone.setStyleSheet(
            "background-color: #eaffea;" if valid else "background-color: #ffeaea;"
        )

    def _find_customer_by_phone(self, phone):
        """Return (customer_id, customer_name) for a phone number, or None."""
        self.db.execute(
            "SELECT customer_id, customer_name FROM customer WHERE customer_phone = %s",
            (phone,)
        )
        return self.db.fetchone()

    def _insert_customer(self, name, phone):
        """Create a customer and select them. Returns True on success."""
        try:
            self.db.execute(
                "INSERT INTO customer (customer_name, customer_phone) VALUES (%s, %s)",
                (name, phone)
            )
            customer_id = self.db.last_insert_id()
            self.db.commit()

            self._set_customer(customer_id, f"{name} ({phone})")
            self.log_action(f"Added new customer: {name} - {phone}")
            self.show_success(f"Customer {name} added successfully")
            return True
        except Exception as e:
            self.db.rollback()
            self.show_error(f"Error adding customer: {e}")
            self._set_customer(None, "Could not add customer", valid=False)
            return False

    def lookup_customer(self):
        """Look up the customer by phone, offering to create one if unknown."""
        phone = self.customer_phone.text().strip()

        if not phone:
            self.customer_id = None
            self.label_6.setText("No customer phone entered")
            self.customer_phone.setStyleSheet("")
            return

        try:
            result = self._find_customer_by_phone(phone)
        except Exception as e:
            self.show_error(f"Error looking up customer: {e}")
            return

        if result:
            self._set_customer(result[0], f"{result[1]} ({phone})")
            return

        name, ok = QInputDialog.getText(
            self, "Add Customer",
            f"Phone {phone} not found. Enter customer name:"
        )
        if ok and name.strip():
            self._insert_customer(name.strip(), phone)
        else:
            self._set_customer(None, "Customer name required", valid=False)

    def create_new_customer(self):
        """Create a customer from the dedicated button."""
        phone = self.customer_phone.text().strip()

        if not phone:
            self.show_warning("Please enter phone number first")
            return

        try:
            if self._find_customer_by_phone(phone):
                self.show_warning("This phone number already exists")
                return
        except Exception as e:
            self.show_error(f"Error looking up customer: {e}")
            return

        name, ok = QInputDialog.getText(self, "Add Customer", "Enter customer name:")
        if ok and name.strip():
            self._insert_customer(name.strip(), phone)

    def show_add_medicine_dialog(self):
        """Show dialog to select and add medicine to cart"""
        try:
            # Get available medicines
            self.db.execute(
                """SELECT medicine_id, medicine_name, unit, sale_price, stock_quantity
                   FROM medicine WHERE stock_quantity > 0
                   ORDER BY medicine_name"""
            )
            meds = self.db.fetchall()

            if not meds:
                self.show_warning("No medicines in stock")
                return

            # Create selection list
            med_names = [
                f"{row[1]} ({row[2]}) - Price: {row[3]} - Stock: {row[4]}"
                for row in meds
            ]

            # Show selection dialog
            idx, ok = QInputDialog.getItem(
                self, "Select Medicine", "Choose medicine:", med_names, 0, False
            )

            if ok and idx:
                med = meds[med_names.index(idx)]

                # Get quantity
                qty, ok2 = QInputDialog.getInt(
                    self, "Quantity",
                    f"Enter quantity (1 - {med[4]}):",
                    1, 1, med[4]
                )

                if ok2:
                    # Check if medicine already in cart
                    existed = False
                    for i, m in enumerate(self.medicine_list):
                        if m[0] == med[0]:
                            # Update quantity
                            new_qty = m[4] + qty
                            if new_qty > med[4]:
                                self.show_warning(f"Total quantity exceeds stock ({med[4]})")
                                return
                            self.medicine_list[i] = (
                                m[0], m[1], m[2], m[3], new_qty, m[3] * new_qty
                            )
                            existed = True
                            break

                    if not existed:
                        # Add new medicine to cart
                        self.medicine_list.append((
                            med[0], med[1], med[2], med[3], qty, med[3] * qty
                        ))

                    self.refresh_medicine_table()
                    self.update_total()

        except Exception as e:
            self.show_error(f"Error adding medicine: {e}")

    def refresh_medicine_table(self):
        """Refresh medicine table display"""
        self.buy_list.setRowCount(len(self.medicine_list))
        self.buy_list.setColumnCount(7)
        self.buy_list.setHorizontalHeaderLabels([
            "Medicine", "Unit", "Price", "Quantity", "Total", "ID", "Delete"
        ])
        self.buy_list.setColumnHidden(5, True)

        for i, med in enumerate(self.medicine_list):
            # medicine_id, name, unit, sale_price, quantity, total_price
            self.buy_list.setItem(i, 0, QTableWidgetItem(str(med[1])))
            self.buy_list.setItem(i, 1, QTableWidgetItem(str(med[2])))
            self.buy_list.setItem(i, 2, QTableWidgetItem(str(med[3])))
            self.buy_list.setItem(i, 3, QTableWidgetItem(str(med[4])))
            self.buy_list.setItem(i, 4, QTableWidgetItem(str(med[5])))
            self.buy_list.setItem(i, 5, QTableWidgetItem(str(med[0])))

            # Add delete button
            btn = QPushButton("Delete")
            btn.clicked.connect(lambda _, row=i: self.remove_medicine_row(row))
            self.buy_list.setCellWidget(i, 6, btn)

    def remove_medicine_row(self, row):
        """Remove medicine from cart"""
        if 0 <= row < len(self.medicine_list):
            del self.medicine_list[row]
            self.refresh_medicine_table()
            self.update_total()

    def update_total(self):
        """Calculate and update total amount"""
        total = sum(med[5] for med in self.medicine_list)
        self.sum_money.setText(str(total))

    def save_invoice(self):
        """Save invoice to database"""
        try:
            # Validate customer
            self.lookup_customer()

            if not self.customer_id:
                self.show_warning("Please select a customer")
                return

            if not self.medicine_list:
                self.show_warning("Please add at least one medicine")
                return

            # Get form data
            payment_method_id = self.payment_term.currentData()
            staff_id = self.context.staff_id
            total = sum(med[5] for med in self.medicine_list)

            # invoice_date is left out so the column default records the real
            # time of sale, not just the date.
            sql = """
                INSERT INTO invoice (customer_id, staff_id, total_amount,
                                     payment_method_id, payment_status)
                VALUES (%s, %s, %s, %s, %s)
            """
            self.db.execute(sql, (
                self.customer_id, staff_id, total, payment_method_id, "Đã thanh toán"
            ))
            invoice_id = self.db.last_insert_id()

            # Insert invoice details and update stock
            for med in self.medicine_list:
                # Insert detail
                self.db.execute(
                    """INSERT INTO invoice_detail (invoice_id, medicine_id, quantity,
                                                   sale_price, total_price)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (invoice_id, med[0], med[4], med[3], med[5])
                )

                # Update stock
                self.db.execute(
                    "UPDATE medicine SET stock_quantity = stock_quantity - %s WHERE medicine_id = %s",
                    (med[4], med[0])
                )

            self.db.commit()

            self.log_action(f"Created invoice: {invoice_id} (Customer: {self.customer_id}, Total: {total})")
            self.show_success(f"{MSG_SUCCESS_ADD} - Invoice #{invoice_id}")
            self.accept()

        except Exception as e:
            self.db.rollback()
            self.show_error(f"{MSG_ERROR_ADD}: {e}")
