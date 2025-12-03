"""
Activity logs window - View system activity history
"""

from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtCore import Qt

from src.ui.base import BaseWindow


class LogsWindow(BaseWindow):
    """Activity logs viewer window"""

    def __init__(self, context):
        super().__init__(context, 'logs.ui', 'Activity Logs')

        # Connect UI elements
        self.back_button.clicked.connect(self.goto_main)
        self.search_input.textChanged.connect(self.search_logs)
        self.tableWidget.setSortingEnabled(True)

        # Load logs
        self.load_logs()

    def load_logs(self):
        """Load activity logs from database"""
        try:
            sql = """
                SELECT log_id, staff_id, action, log_time
                FROM activity_log
                ORDER BY log_time DESC
                LIMIT 1000
            """
            self.db.execute(sql)
            results = self.db.fetchall()

            # Configure table
            self.tableWidget.setRowCount(len(results))
            self.tableWidget.setColumnCount(4)

            # Set column headers
            self.tableWidget.setHorizontalHeaderLabels(['ID', 'Staff ID', 'Action', 'Time'])

            # Set column widths
            self.tableWidget.setColumnWidth(0, 80)   # ID
            self.tableWidget.setColumnWidth(1, 120)  # Staff ID
            self.tableWidget.setColumnWidth(2, 400)  # Action
            self.tableWidget.setColumnWidth(3, 200)  # Time

            # Populate table
            for row_idx, row_data in enumerate(results):
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value or ''))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                    # Make read-only
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

                    self.tableWidget.setItem(row_idx, col_idx, item)

        except Exception as e:
            self.show_error(f"Error loading activity logs: {e}")

    def search_logs(self):
        """Search logs by staff ID or action"""
        keyword = self.search_input.text().strip().lower()

        for row in range(self.tableWidget.rowCount()):
            staff_item = self.tableWidget.item(row, 1)  # Staff ID
            action_item = self.tableWidget.item(row, 2)  # Action

            if staff_item and action_item:
                staff_text = staff_item.text().lower()
                action_text = action_item.text().lower()

                match = keyword in staff_text or keyword in action_text
                self.tableWidget.setRowHidden(row, not match)

    def goto_main(self):
        """Return to main window"""
        from src.ui.windows.main_window import MainWindow
        self.main_window = MainWindow(self.context)
        self.main_window.show()
        self.close()

    def refresh_data(self):
        """Refresh logs data"""
        self.load_logs()
