"""
Report export dialog - Choose report type and export to PDF
"""

from datetime import datetime
from PyQt6.QtWidgets import QMessageBox

from src.ui.base import BaseDialog
from src.services import ReportService


class ReportDialog(BaseDialog):
    """Dialog for selecting and exporting reports"""

    def __init__(self, context, parent=None):
        super().__init__(context, 'main.ui', 'Export Reports', parent)  # Reuse main.ui or create dedicated one

        # Initialize report service
        self.report_service = ReportService(context)

        # This is a simplified version
        # In production, you'd create a dedicated report_dialog.ui with:
        # - Radio buttons for report type selection
        # - Date picker for invoice reports
        # - Export button

    def export_stock_report(self):
        """Export stock inventory report"""
        try:
            filepath = self.report_service.export_stock_report()
            self.show_success(f"Stock report exported successfully!\n{filepath}")
            self.log_action("Exported stock report")
        except Exception as e:
            self.show_error(f"Failed to export stock report: {e}")

    def export_invoice_report(self, date=None):
        """Export invoice report for specific date"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        try:
            filepath = self.report_service.export_invoice_report(date)
            self.show_success(f"Invoice report exported successfully!\n{filepath}")
            self.log_action(f"Exported invoice report for {date}")
        except Exception as e:
            self.show_error(f"Failed to export invoice report: {e}")

    def export_expiry_report(self):
        """Export expiring medicines report"""
        try:
            filepath = self.report_service.export_expiry_warning_report()
            self.show_success(f"Expiry warning report exported successfully!\n{filepath}")
            self.log_action("Exported expiry warning report")
        except Exception as e:
            self.show_error(f"Failed to export expiry report: {e}")
