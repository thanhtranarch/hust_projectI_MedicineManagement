"""
Report export dialog - choose a report type and export it to PDF.
"""

import os
import subprocess
import sys

from PyQt6.QtCore import QDate

from src.services import ReportService
from src.ui.base import BaseDialog
from src.utils.constants import EXPIRY_WARNING_DAYS


class ReportDialog(BaseDialog):
    """Lets the user pick a report, a date range, and export to PDF."""

    def __init__(self, context, parent=None):
        super().__init__(context, 'report.ui', 'Xuất báo cáo', parent)

        self.report_service = ReportService(context)
        self.last_export = None

        today = QDate.currentDate()
        self.date_from.setDate(QDate(today.year(), today.month(), 1))
        self.date_to.setDate(today)
        self.expiry_days.setValue(EXPIRY_WARNING_DAYS)

        for radio in (self.radio_stock, self.radio_revenue,
                      self.radio_invoice, self.radio_expiry):
            radio.toggled.connect(self._update_input_state)

        self.export_button.clicked.connect(self.export_report)
        self.close_button.clicked.connect(self.reject)

        self._update_input_state()

    def _update_input_state(self):
        """Enable only the inputs that the selected report actually uses."""
        self.date_from.setEnabled(self.radio_revenue.isChecked())
        self.date_to.setEnabled(
            self.radio_revenue.isChecked() or self.radio_invoice.isChecked()
        )
        self.expiry_days.setEnabled(self.radio_expiry.isChecked())

    def _selected_export(self):
        """Return a no-argument callable that produces the chosen report."""
        start = self.date_from.date().toString("yyyy-MM-dd")
        end = self.date_to.date().toString("yyyy-MM-dd")

        if self.radio_revenue.isChecked():
            return lambda: self.report_service.export_revenue_report(start, end)
        if self.radio_invoice.isChecked():
            return lambda: self.report_service.export_invoice_report(end)
        if self.radio_expiry.isChecked():
            return lambda: self.report_service.export_expiry_warning_report(
                self.expiry_days.value()
            )
        return self.report_service.export_stock_report

    def export_report(self):
        """Generate the selected report and offer to open it."""
        if self.radio_revenue.isChecked() and self.date_from.date() > self.date_to.date():
            self.show_warning("'Từ ngày' phải trước 'Đến ngày'")
            return

        try:
            filepath = self._selected_export()()
        except Exception as e:
            self.show_error(f"Xuất báo cáo thất bại: {e}")
            return

        self.last_export = filepath
        self.status_label.setText(f"Đã lưu: {filepath}")

        if self.confirm_action(f"Đã xuất báo cáo:\n{filepath}\n\nMở tệp ngay?",
                               "Xuất báo cáo thành công"):
            self.open_file(filepath)

    @staticmethod
    def open_file(filepath):
        """Open a file with the platform's default application."""
        try:
            if sys.platform.startswith('darwin'):
                subprocess.Popen(['open', filepath])
            elif os.name == 'nt':
                os.startfile(filepath)  # noqa: S606 - Windows-only API
            else:
                subprocess.Popen(['xdg-open', filepath])
        except Exception as e:
            print(f"Could not open {filepath}: {e}")

    # Convenience entry points used by the dashboard's quick menu
    def export_stock_report(self):
        """Export the stock report directly."""
        self.radio_stock.setChecked(True)
        self.export_report()

    def export_revenue_report(self):
        """Export the revenue report directly."""
        self.radio_revenue.setChecked(True)
        self.export_report()

    def export_invoice_report(self, date=None):
        """Export the invoice report for a given day (defaults to today)."""
        self.radio_invoice.setChecked(True)
        if date:
            self.date_to.setDate(QDate.fromString(date, "yyyy-MM-dd"))
        else:
            self.date_to.setDate(QDate.currentDate())
        self.export_report()

    def export_expiry_report(self):
        """Export the expiry warning report directly."""
        self.radio_expiry.setChecked(True)
        self.export_report()
