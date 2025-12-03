"""
Stock management window
"""

from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtCore import Qt

from src.ui.base import BaseWindow
from src.ui.dialogs.stock_information_dialog import StockInformationDialog
from src.ui.dialogs.create_stock_dialog import CreateStockDialog


class StockWindow(BaseWindow):
    """Stock management window with table and search"""

    def __init__(self, context):
        super().__init__(context, 'stock.ui', 'Stock Management')

        # Connect UI elements
        self.back_button.clicked.connect(self.goto_main)
        self.search_input.textChanged.connect(self.search_stock)
        self.tableWidget.cellClicked.connect(self.handle_cell_click)
        self.tableWidget.setSortingEnabled(True)
        self.add_stock.clicked.connect(self.show_create_stock)

        # Load data
        self.load_stock_data()

    def load_stock_data(self):
        """Load stock data into table"""
        try:
            sql = """
                SELECT s.stock_id, sd.medicine_id, m.medicine_name,
                       sd.quantity, sd.price, sd.batch_number,
                       sd.expiration_date, sup.supplier_name,
                       s.staff_id, s.created_at
                FROM stock_detail sd
                JOIN stock s ON s.stock_id = sd.stock_id
                JOIN medicine m ON sd.medicine_id = m.medicine_id
                JOIN supplier sup ON s.supplier_id = sup.supplier_id
                ORDER BY s.created_at DESC, s.stock_id DESC
            """
            self.db.execute(sql)
            results = self.db.fetchall()

            # Configure table
            self.tableWidget.setRowCount(len(results))
            self.tableWidget.setColumnCount(10)
            self.tableWidget.setHorizontalHeaderLabels([
                "Stock ID", "Medicine ID", "Medicine Name", "Quantity",
                "Price", "Batch", "Exp. Date", "Supplier", "Staff", "Created At"
            ])

            # Hide ID columns
            self.tableWidget.setColumnHidden(0, True)
            self.tableWidget.setColumnHidden(1, True)

            # Populate table
            for row_idx, row_data in enumerate(results):
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value or ''))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tableWidget.setItem(row_idx, col_idx, item)

        except Exception as e:
            self.show_error(f"Error loading stock data: {e}")

    def search_stock(self):
        """Search stock by medicine name"""
        keyword = self.search_input.text().strip().lower()

        for row in range(self.tableWidget.rowCount()):
            name_item = self.tableWidget.item(row, 2)  # Medicine name column
            if name_item:
                match = keyword in name_item.text().lower()
                self.tableWidget.setRowHidden(row, not match)

    def handle_cell_click(self, row, column):
        """Handle cell click to open detail dialog"""
        # Currently no specific detail dialog for stock
        # Could open medicine detail if needed
        pass

    def show_create_stock(self):
        """Show create stock dialog"""
        dialog = CreateStockDialog(self.context, self)
        if dialog.exec():
            self.load_stock_data()

    def goto_main(self):
        """Return to main window"""
        from src.ui.windows.main_window import MainWindow
        self.main_window = MainWindow(self.context)
        self.main_window.show()
        self.close()

    def refresh_data(self):
        """Refresh table data"""
        self.load_stock_data()
