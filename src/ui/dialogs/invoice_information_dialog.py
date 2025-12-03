"""
Invoice information dialog (view-only)
"""

from PyQt6.QtWidgets import QTableWidgetItem, QTableWidget

from src.ui.base import BaseDialog


class InvoiceInformationDialog(BaseDialog):
    """Invoice detail dialog - view only"""

    def __init__(self, context, invoice_id, parent=None):
        super().__init__(context, 'create_invoice.ui', 'Invoice Details', parent)

        self.invoice_id_value = invoice_id

        # Set view mode
        self.set_view_mode()

        # Load data
        self.load_data()

    def set_view_mode(self):
        """Configure dialog for view-only mode"""
        self.save_button.setDisabled(True)
        self.cancel_button.setText("Close")
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
        """Load invoice data from database"""
        try:
            # Load invoice info
            sql = """
                SELECT invoice_id, invoice_date, customer_id, staff_id,
                       total_amount, payment_method_id, payment_status
                FROM invoice
                WHERE invoice_id = %s
            """
            self.db.execute(sql, (int(self.invoice_id_value),))
            invoice_info = self.db.fetchone()

            if not invoice_info:
                self.show_warning("Invoice not found")
                self.reject()
                return

            # Set invoice fields
            self.invoice_id.setText(str(invoice_info[0]))
            self.invoice_date.setDate(invoice_info[1])
            self.staff_name.setText(str(invoice_info[3]))
            self.sum_money.setText(str(invoice_info[4]))
            self.payment_term.setCurrentIndex(
                self.payment_term.findData(invoice_info[5])
            )

            # Load customer info
            self.db.execute(
                "SELECT customer_name, customer_phone FROM customer WHERE customer_id = %s",
                (invoice_info[2],)
            )
            cinfo = self.db.fetchone()
            if cinfo:
                self.customer_phone.setText(cinfo[1])
                self.label_6.setText(f"{cinfo[0]} ({cinfo[1]})")

            # Load invoice details (medicines)
            sql = """
                SELECT m.medicine_id, m.medicine_name, m.unit,
                       d.sale_price, d.quantity, d.total_price
                FROM invoice_detail d
                JOIN medicine m ON d.medicine_id = m.medicine_id
                WHERE d.invoice_id = %s
            """
            self.db.execute(sql, (invoice_info[0],))
            meds = self.db.fetchall()

            # Configure table
            self.buy_list.setRowCount(len(meds))
            self.buy_list.setColumnCount(6)
            self.buy_list.setHorizontalHeaderLabels([
                "Medicine Name", "Unit", "Sale Price", "Quantity", "Total Price", "ID"
            ])
            self.buy_list.setColumnHidden(5, True)  # Hide ID column

            # Populate table
            for i, med in enumerate(meds):
                self.buy_list.setItem(i, 0, QTableWidgetItem(str(med[1])))  # Name
                self.buy_list.setItem(i, 1, QTableWidgetItem(str(med[2])))  # Unit
                self.buy_list.setItem(i, 2, QTableWidgetItem(str(med[3])))  # Sale price
                self.buy_list.setItem(i, 3, QTableWidgetItem(str(med[4])))  # Quantity
                self.buy_list.setItem(i, 4, QTableWidgetItem(str(med[5])))  # Total price
                self.buy_list.setItem(i, 5, QTableWidgetItem(str(med[0])))  # ID (hidden)

            # Remove delete buttons from column 6 if they exist
            for i in range(self.buy_list.rowCount()):
                if self.buy_list.columnCount() > 6:
                    self.buy_list.setCellWidget(i, 6, None)

        except Exception as e:
            self.show_error(f"Error loading invoice data: {e}")
