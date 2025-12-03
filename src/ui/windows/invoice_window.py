"""
Invoice management window
"""

from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtCore import Qt

from src.ui.base import BaseWindow
from src.ui.dialogs.invoice_information_dialog import InvoiceInformationDialog


class InvoiceWindow(BaseWindow):
    """Invoice management window with table and search"""

    def __init__(self, context):
        super().__init__(context, 'invoice.ui', 'Invoice Management')

        # Connect UI elements
        self.back_button.clicked.connect(self.goto_main)
        self.tableWidget.cellClicked.connect(self.handle_cell_click)
        self.tableWidget.setSortingEnabled(True)

        # Load data
        self.load_invoice_data()

    def load_invoice_data(self):
        """Load invoice data into table"""
        try:
            sql = """
                SELECT invoice_id, customer_id, total_amount, created_at
                FROM invoice
                ORDER BY created_at DESC
            """
            self.db.execute(sql)
            results = self.db.fetchall()

            # Configure table
            self.tableWidget.setRowCount(len(results))
            self.tableWidget.setColumnCount(4)
            self.tableWidget.setHorizontalHeaderLabels([
                "Invoice ID", "Customer ID", "Total", "Created At"
            ])

            # Populate table
            for row_idx, row_data in enumerate(results):
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value or ''))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tableWidget.setItem(row_idx, col_idx, item)

        except Exception as e:
            self.show_error(f"Error loading invoice data: {e}")

    def handle_cell_click(self, row, column):
        """Handle cell click to open detail dialog"""
        invoice_id_item = self.tableWidget.item(row, 0)
        if invoice_id_item:
            invoice_id = invoice_id_item.text()
            self.show_invoice_detail(invoice_id)

    def show_invoice_detail(self, invoice_id):
        """Show invoice detail dialog"""
        dialog = InvoiceInformationDialog(self.context, invoice_id, self)
        if dialog.exec():
            self.load_invoice_data()

    def goto_main(self):
        """Return to main window"""
        from src.ui.windows.main_window import MainWindow
        self.main_window = MainWindow(self.context)
        self.main_window.show()
        self.close()

    def refresh_data(self):
        """Refresh table data"""
        self.load_invoice_data()
