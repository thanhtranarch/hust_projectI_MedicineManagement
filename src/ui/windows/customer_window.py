"""
Customer management window
"""

from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from src.ui.base import BaseWindow
from src.ui.dialogs.customer_information_dialog import CustomerInformationDialog


class CustomerWindow(BaseWindow):
    """Customer management window with table and search"""

    def __init__(self, context):
        super().__init__(context, 'customer.ui', 'Customer Management')

        # Connect UI elements
        self.back_button.clicked.connect(self.goto_main)
        self.search_input.textChanged.connect(self.search_customer)
        self.tableWidget.cellClicked.connect(self.handle_cell_click)
        self.tableWidget.setSortingEnabled(True)

        # Load data
        self.load_customer_data()

    def load_customer_data(self):
        """Load customer data into table"""
        try:
            sql = """
                SELECT customer_id, customer_name, customer_phone, customer_email
                FROM customer
                ORDER BY customer_name
            """
            self.db.execute(sql)
            results = self.db.fetchall()

            # Configure table
            self.tableWidget.setRowCount(len(results))
            self.tableWidget.setColumnCount(5)
            self.tableWidget.setHorizontalHeaderLabels(["ID", "Name", "Phone", "Email", "Details"])
            self.tableWidget.setColumnHidden(0, True)

            # Populate table
            for row_idx, row_data in enumerate(results):
                customer_id = row_data[0]

                for col_idx in range(4):
                    item = QTableWidgetItem(str(row_data[col_idx] or ''))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                    # Format name column (clickable)
                    if col_idx == 1:
                        font = QFont()
                        font.setBold(True)
                        font.setUnderline(True)
                        item.setFont(font)
                        item.setData(Qt.ItemDataRole.UserRole, customer_id)
                        item.setToolTip("Click to view customer details")

                    self.tableWidget.setItem(row_idx, col_idx, item)

                # Add "View Details" column
                detail_item = QTableWidgetItem("View Details")
                font = QFont()
                font.setUnderline(True)
                detail_item.setFont(font)
                detail_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                detail_item.setData(Qt.ItemDataRole.UserRole, customer_id)
                detail_item.setToolTip("Click to view customer details")
                self.tableWidget.setItem(row_idx, 4, detail_item)

        except Exception as e:
            self.show_error(f"Error loading customer data: {e}")

    def search_customer(self):
        """Search customers by name"""
        keyword = self.search_input.text().strip().lower()

        for row in range(self.tableWidget.rowCount()):
            name_item = self.tableWidget.item(row, 1)
            if name_item:
                match = keyword in name_item.text().lower()
                self.tableWidget.setRowHidden(row, not match)

    def handle_cell_click(self, row, column):
        """Handle cell click to open detail dialog"""
        if column in [1, 4]:  # Name or Details column
            item = self.tableWidget.item(row, column)
            if item:
                customer_id = item.data(Qt.ItemDataRole.UserRole)
                if customer_id:
                    self.show_customer_detail(customer_id)

    def show_customer_detail(self, customer_id):
        """Show customer detail dialog"""
        dialog = CustomerInformationDialog(self.context, customer_id, self)
        if dialog.exec():
            self.load_customer_data()

    def goto_main(self):
        """Return to main window"""
        from src.ui.windows.main_window import MainWindow
        self.main_window = MainWindow(self.context)
        self.main_window.show()
        self.close()

    def refresh_data(self):
        """Refresh table data"""
        self.load_customer_data()
