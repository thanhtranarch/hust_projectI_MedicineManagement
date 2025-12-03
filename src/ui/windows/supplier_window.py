"""
Supplier management window
"""

from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from src.ui.base import BaseWindow
from src.ui.dialogs.supplier_information_dialog import SupplierInformationDialog


class SupplierWindow(BaseWindow):
    """Supplier management window with table and search"""

    def __init__(self, context):
        super().__init__(context, 'supplier.ui', 'Supplier Management')

        # Connect UI elements
        self.back_button.clicked.connect(self.goto_main)
        self.search_input.textChanged.connect(self.search_supplier)
        self.tableWidget.cellClicked.connect(self.handle_cell_click)
        self.tableWidget.setSortingEnabled(True)

        # Load data
        self.load_supplier_data()

    def load_supplier_data(self):
        """Load supplier data into table"""
        try:
            sql = """
                SELECT supplier_id, supplier_name, created_at, updated_at
                FROM supplier
                ORDER BY supplier_name
            """
            self.db.execute(sql)
            results = self.db.fetchall()

            # Configure table
            self.tableWidget.setRowCount(len(results))
            column_count = 5  # ID (hidden), Name, Created, Updated, View Details
            self.tableWidget.setColumnCount(column_count)

            # Set column widths
            self.tableWidget.setColumnHidden(0, True)  # Hide ID column
            self.tableWidget.setColumnWidth(1, 300)  # Name
            self.tableWidget.setColumnWidth(2, 150)  # Created
            self.tableWidget.setColumnWidth(3, 150)  # Updated
            self.tableWidget.setColumnWidth(4, 200)  # View Details

            # Populate table
            for row_idx, row_data in enumerate(results):
                supplier_id = row_data[0]

                for col_idx in range(len(row_data)):
                    value = row_data[col_idx]
                    item = QTableWidgetItem(str(value or ''))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                    # Format supplier name column (clickable)
                    if col_idx == 1:
                        font = QFont()
                        font.setBold(True)
                        font.setUnderline(True)
                        item.setFont(font)
                        item.setToolTip("Click to view supplier details")
                        item.setData(Qt.ItemDataRole.UserRole, supplier_id)

                    self.tableWidget.setItem(row_idx, col_idx, item)

                # Add "View Details" column
                detail_item = QTableWidgetItem("View Details")
                font = QFont()
                font.setUnderline(True)
                detail_item.setFont(font)
                detail_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                detail_item.setData(Qt.ItemDataRole.UserRole, supplier_id)
                detail_item.setToolTip("Click to view supplier details")
                self.tableWidget.setItem(row_idx, 4, detail_item)

        except Exception as e:
            self.show_error(f"Error loading supplier data: {e}")

    def search_supplier(self):
        """Search suppliers by name"""
        keyword = self.search_input.text().strip().lower()

        for row in range(self.tableWidget.rowCount()):
            name_item = self.tableWidget.item(row, 1)  # Supplier name column
            if name_item:
                name_text = name_item.text().lower()
                match = keyword in name_text
                self.tableWidget.setRowHidden(row, not match)

    def show_supplier_detail(self, supplier_id):
        """Show supplier detail dialog"""
        detail_dialog = SupplierInformationDialog(self.context, supplier_id, self)
        if detail_dialog.exec():
            # Refresh table after dialog closes
            self.load_supplier_data()

    def handle_cell_click(self, row, column):
        """Handle cell click to open detail dialog"""
        # Column 1 (name) or column 4 (view details)
        if column in [1, 4]:
            item = self.tableWidget.item(row, column)
            if item:
                supplier_id = item.data(Qt.ItemDataRole.UserRole)
                if supplier_id:
                    self.show_supplier_detail(supplier_id)

    def goto_main(self):
        """Return to main window"""
        from src.ui.windows.main_window import MainWindow
        self.main_window = MainWindow(self.context)
        self.main_window.show()
        self.close()

    def refresh_data(self):
        """Refresh table data"""
        self.load_supplier_data()
