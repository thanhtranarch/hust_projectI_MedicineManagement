"""
Staff management window
"""

from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from src.ui.base import BaseWindow
from src.ui.dialogs.staff_information_dialog import StaffInformationDialog


class StaffWindow(BaseWindow):
    """Staff management window with table and search"""

    def __init__(self, context):
        super().__init__(context, 'staff.ui', 'Staff Management')

        # Connect UI elements
        self.back_button.clicked.connect(self.goto_main)
        self.search_input.textChanged.connect(self.search_staff)
        self.tableWidget.cellClicked.connect(self.handle_cell_click)
        self.tableWidget.setSortingEnabled(True)

        # Load data
        self.load_staff_data()

    def load_staff_data(self):
        """Load staff data into table"""
        try:
            sql = """
                SELECT staff_id, staff_name, staff_position, created_at, updated_at
                FROM staff
                ORDER BY staff_name
            """
            self.db.execute(sql)
            results = self.db.fetchall()

            # Configure table
            self.tableWidget.setRowCount(len(results))
            self.tableWidget.setColumnCount(6)
            self.tableWidget.setHorizontalHeaderLabels(
                ["ID", "Name", "Position", "Created", "Updated", "Details"]
            )

            # Set column widths
            self.tableWidget.setColumnWidth(0, 50)
            self.tableWidget.setColumnWidth(1, 200)
            self.tableWidget.setColumnWidth(2, 100)
            self.tableWidget.setColumnWidth(3, 150)
            self.tableWidget.setColumnWidth(4, 150)
            self.tableWidget.setColumnWidth(5, 200)

            # Populate table
            for row_idx, row_data in enumerate(results):
                staff_id = row_data[0]

                for col_idx in range(5):
                    item = QTableWidgetItem(str(row_data[col_idx] or ''))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                    # Format name and position columns (clickable)
                    if col_idx in [1, 2]:
                        font = QFont()
                        font.setUnderline(True)
                        item.setFont(font)
                        item.setData(Qt.ItemDataRole.UserRole, staff_id)
                        item.setToolTip("Click to view staff details")

                    self.tableWidget.setItem(row_idx, col_idx, item)

                # Add "View Details" column
                detail_item = QTableWidgetItem("View Details")
                font = QFont()
                font.setUnderline(True)
                detail_item.setFont(font)
                detail_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                detail_item.setData(Qt.ItemDataRole.UserRole, staff_id)
                detail_item.setToolTip("Click to view staff details")
                self.tableWidget.setItem(row_idx, 5, detail_item)

        except Exception as e:
            self.show_error(f"Error loading staff data: {e}")

    def search_staff(self):
        """Search staff by name"""
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
                staff_id = item.data(Qt.ItemDataRole.UserRole)
                if staff_id:
                    self.show_staff_detail(staff_id)

    def show_staff_detail(self, staff_id):
        """Show staff detail dialog"""
        dialog = StaffInformationDialog(self.context, staff_id, self)
        if dialog.exec():
            self.load_staff_data()

    def goto_main(self):
        """Return to main window"""
        from src.ui.windows.main_window import MainWindow
        self.main_window = MainWindow(self.context)
        self.main_window.show()
        self.close()

    def refresh_data(self):
        """Refresh table data"""
        self.load_staff_data()
