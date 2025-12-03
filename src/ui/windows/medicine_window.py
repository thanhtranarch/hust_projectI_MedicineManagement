"""
Medicine management window
"""

from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from src.ui.base import BaseWindow
from src.ui.dialogs.medicine_information_dialog import MedicineInformationDialog


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
            sql = """
                SELECT m.medicine_id, m.medicine_name, c.category_name,
                       m.created_at, m.updated_at
                FROM medicine m
                JOIN category c ON m.category_id = c.category_id
                ORDER BY m.medicine_name
            """
            cursor = self.db.execute(sql)
            results = cursor.fetchall()

            if not results:
                self.show_warning("No medicine data found")
                return

            # Configure table
            column_count = len(cursor.description) + 1  # +1 for "View Details"
            self.tableWidget.setRowCount(len(results))
            self.tableWidget.setColumnCount(column_count)

            # Set headers
            self.tableWidget.setHorizontalHeaderLabels([
                "ID", "Name", "Category", "Created At", "Updated At", "Details"
            ])

            # Set column widths
            self.tableWidget.setColumnWidth(0, 50)
            self.tableWidget.setColumnWidth(1, 200)
            self.tableWidget.setColumnWidth(2, 150)
            self.tableWidget.setColumnWidth(3, 150)
            self.tableWidget.setColumnWidth(4, 150)
            self.tableWidget.setColumnWidth(5, 150)

            # Populate table
            for row_idx, row_data in enumerate(results):
                medicine_id = row_data[0]

                for col_idx in range(column_count):
                    if col_idx < len(row_data):
                        value = row_data[col_idx]

                        if col_idx == 0:
                            # ID column - numeric sort
                            item = QTableWidgetItem()
                            item.setData(Qt.ItemDataRole.DisplayRole, int(value))
                            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        else:
                            item = QTableWidgetItem(str(value))

                            # Make name and category clickable
                            if col_idx in [1, 2]:
                                font = QFont()
                                font.setUnderline(True)
                                item.setFont(font)
                                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                                item.setData(Qt.ItemDataRole.UserRole, medicine_id)
                                item.setToolTip("Click to view medicine details")

                        self.tableWidget.setItem(row_idx, col_idx, item)
                    else:
                        # "View Details" column
                        detail_item = QTableWidgetItem("View Details")
                        font = QFont()
                        font.setUnderline(True)
                        detail_item.setFont(font)
                        detail_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        detail_item.setData(Qt.ItemDataRole.UserRole, medicine_id)
                        detail_item.setToolTip("Click to view medicine details")
                        self.tableWidget.setItem(row_idx, col_idx, detail_item)

            # Enable sorting after data is loaded
            self.tableWidget.setSortingEnabled(True)

        except Exception as e:
            self.show_error(f"Error loading medicine data: {e}")

    def search_medicine(self):
        """Search medicines by name"""
        keyword = self.search_input.text().strip().lower()

        for row in range(self.tableWidget.rowCount()):
            name_item = self.tableWidget.item(row, 1)
            if name_item:
                match = keyword in name_item.text().lower()
                self.tableWidget.setRowHidden(row, not match)

    def handle_cell_click(self, row, column):
        """Handle cell click to open detail dialog"""
        if column in [1, 5]:  # Name or Details column
            item = self.tableWidget.item(row, column)
            if item:
                medicine_id = item.data(Qt.ItemDataRole.UserRole)
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
