"""
Medicine management window
"""

from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from src.ui.base import BaseWindow
from src.ui.dialogs.medicine_information_dialog import MedicineInformationDialog
from src.utils.helpers import format_currency

MEDICINE_HEADERS = ["ID", "Tên thuốc", "Danh mục", "Tồn kho",
                    "Giá bán", "Hạn dùng", "Chi tiết"]

# Columns that open the detail dialog when clicked
CLICKABLE_COLUMNS = (1, 6)


class MedicineWindow(BaseWindow):
    """Medicine management window with table and search"""

    def __init__(self, context):
        super().__init__(context, 'medicine.ui', 'Medicine Management')

        # Connect UI elements
        self.back_button.clicked.connect(self.goto_main)
        self.search_input.textChanged.connect(self.search_medicine)
        self.tableWidget.cellClicked.connect(self.handle_cell_click)
        self.tableWidget.setSortingEnabled(True)

        # Load data
        self.load_medicine_data()

    def load_medicine_data(self):
        """Load medicine data into table"""
        try:
            # LEFT JOIN: medicines that have no category yet must still be listed
            sql = """
                SELECT m.medicine_id, m.medicine_name, c.category_name,
                       m.stock_quantity, m.sale_price, m.expiration_date
                FROM medicine m
                LEFT JOIN category c ON m.category_id = c.category_id
                ORDER BY m.medicine_name
            """
            self.db.execute(sql)
            results = self.db.fetchall()

            # Sorting must be off while filling, otherwise rows move mid-populate
            self.tableWidget.setSortingEnabled(False)
            self.tableWidget.setRowCount(len(results))
            self.tableWidget.setColumnCount(len(MEDICINE_HEADERS))
            self.tableWidget.setHorizontalHeaderLabels(MEDICINE_HEADERS)

            for row_idx, row_data in enumerate(results):
                self._fill_row(row_idx, row_data)

            self.tableWidget.resizeColumnsToContents()
            self.tableWidget.setSortingEnabled(True)

        except Exception as e:
            self.show_error(f"Error loading medicine data: {e}")

    def _fill_row(self, row_idx, row_data):
        """Populate one table row from a medicine record."""
        medicine_id, name, category, quantity, price, expiry = row_data

        # ID gets a numeric value so sorting is by number, not by string
        id_item = QTableWidgetItem()
        id_item.setData(Qt.ItemDataRole.DisplayRole, int(medicine_id))
        id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        cells = [
            id_item,
            QTableWidgetItem(name or ''),
            QTableWidgetItem(category or 'Chưa phân loại'),
            QTableWidgetItem(str(quantity if quantity is not None else 0)),
            QTableWidgetItem(format_currency(price)),
            QTableWidgetItem(
                expiry.strftime("%d/%m/%Y") if hasattr(expiry, 'strftime') else str(expiry or '')
            ),
            QTableWidgetItem("Xem chi tiết"),
        ]

        underline = QFont()
        underline.setUnderline(True)

        for col_idx, item in enumerate(cells):
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if col_idx in CLICKABLE_COLUMNS:
                item.setFont(underline)
                item.setToolTip("Nhấn để xem chi tiết thuốc")
            item.setData(Qt.ItemDataRole.UserRole, medicine_id)
            self.tableWidget.setItem(row_idx, col_idx, item)

    def search_medicine(self):
        """Search medicines by name"""
        keyword = self.search_input.text().strip().lower()

        for row in range(self.tableWidget.rowCount()):
            name_item = self.tableWidget.item(row, 1)
            if name_item:
                match = keyword in name_item.text().lower()
                self.tableWidget.setRowHidden(row, not match)

    def handle_cell_click(self, row, column):
        """Open the detail dialog when a clickable column is clicked"""
        if column not in CLICKABLE_COLUMNS:
            return

        item = self.tableWidget.item(row, column)
        medicine_id = item.data(Qt.ItemDataRole.UserRole) if item else None
        if medicine_id:
            self.show_medicine_detail(medicine_id)

    def show_medicine_detail(self, medicine_id):
        """Show medicine detail dialog"""
        dialog = MedicineInformationDialog(self.context, medicine_id, self)
        if dialog.exec():
            # Refresh data when dialog closes
            self.load_medicine_data()

    def goto_main(self):
        """Return to main window"""
        from src.ui.windows.main_window import MainWindow
        self.main_window = MainWindow(self.context)
        self.main_window.show()
        self.close()

    def refresh_data(self):
        """Refresh table data"""
        self.load_medicine_data()
