"""
Report generation service for PDF exports
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from ..config.settings import Settings


class ReportService:
    """Service for generating various reports"""

    def __init__(self, context):
        """
        Initialize report service

        Args:
            context: Application context with database connection
        """
        self.context = context
        self.db = context.db_manager

        # Register Vietnamese font
        font_path = os.path.join(Settings.FONTS_DIR, "Arial.ttf")
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('ArialUnicode', font_path))

    def export_stock_report(self, filepath=None):
        """
        Export stock inventory report to PDF

        Args:
            filepath (str, optional): Output file path

        Returns:
            str: Path to generated PDF file
        """
        if filepath is None:
            filename = f"report_stock_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            Settings.ensure_exports_dir()
            filepath = os.path.join(Settings.EXPORTS_DIR, filename)

        sql = """
            SELECT medicine_name, unit, stock_quantity, batch_number, sale_price
            FROM medicine
            ORDER BY medicine_name
        """
        self.db.execute(sql)
        results = self.db.fetchall()

        c = canvas.Canvas(filepath, pagesize=A4)
        c.setFont("ArialUnicode", 14)
        c.drawString(50, 800, "BÁO CÁO TỒN KHO")

        c.setFont("ArialUnicode", 10)
        y = 780
        headers = ["Tên thuốc", "Đơn vị", "Tồn kho", "Số lô", "Giá bán"]
        for i, header in enumerate(headers):
            c.drawString(50 + i * 100, y, header)

        y -= 20
        for row in results:
            if y < 50:
                c.showPage()
                y = 800
                c.setFont("ArialUnicode", 10)
            for i, value in enumerate(row):
                c.drawString(50 + i * 100, y, str(value or ''))
            y -= 20

        c.save()

        # Log action
        self.context.log_action(f"Exported stock report: {filename}")

        return filepath

    def export_invoice_report(self, date, filepath=None):
        """
        Export invoice report for specific date to PDF

        Args:
            date (str): Date in YYYY-MM-DD format
            filepath (str, optional): Output file path

        Returns:
            str: Path to generated PDF file
        """
        if filepath is None:
            filename = f"report_invoice_{date}.pdf"
            Settings.ensure_exports_dir()
            filepath = os.path.join(Settings.EXPORTS_DIR, filename)

        sql = """
            SELECT invoice_id, invoice_date, customer_id, total_amount, staff_id, payment_status
            FROM invoice
            WHERE DATE(invoice_date) = %s
            ORDER BY invoice_date DESC
        """
        self.db.execute(sql, (date,))
        results = self.db.fetchall()

        c = canvas.Canvas(filepath, pagesize=A4)
        c.setFont("ArialUnicode", 14)
        c.drawString(50, 800, f"BÁO CÁO HÓA ĐƠN NGÀY {date}")

        c.setFont("ArialUnicode", 10)
        y = 780
        headers = ["ID", "Thời gian", "KH", "Tổng tiền", "NV", "Trạng thái"]
        for i, header in enumerate(headers):
            c.drawString(50 + i * 80, y, header)

        y -= 20
        for row in results:
            if y < 50:
                c.showPage()
                y = 800
                c.setFont("ArialUnicode", 10)
            for i, value in enumerate(row):
                c.drawString(50 + i * 80, y, str(value or ''))
            y -= 20

        c.save()

        # Log action
        self.context.log_action(f"Exported invoice report for date: {date}")

        return filepath

    def export_expiry_warning_report(self, filepath=None):
        """
        Export expiring medicines report to PDF

        Args:
            filepath (str, optional): Output file path

        Returns:
            str: Path to generated PDF file
        """
        if filepath is None:
            filename = f"report_expiring_{datetime.now().strftime('%Y%m%d')}.pdf"
            Settings.ensure_exports_dir()
            filepath = os.path.join(Settings.EXPORTS_DIR, filename)

        sql = """
            SELECT medicine_name, stock_quantity, unit, batch_number, expiration_date,
                   (expiration_date::date - CURRENT_DATE) AS days_left
            FROM medicine
            WHERE (expiration_date::date - CURRENT_DATE) <= 60
              AND (expiration_date::date - CURRENT_DATE) >= 0
            ORDER BY expiration_date ASC
        """
        self.db.execute(sql)
        results = self.db.fetchall()

        c = canvas.Canvas(filepath, pagesize=A4)
        c.setFont("ArialUnicode", 14)
        c.drawString(50, 800, "BÁO CÁO THUỐC SẮP HẾT HẠN")

        c.setFont("ArialUnicode", 10)
        y = 780
        col_x = [50, 150, 200, 270, 370, 500]
        headers = ["Tên thuốc", "SL", "ĐV", "Số lô", "Hạn dùng", "Còn lại (ngày)"]
        for i, header in enumerate(headers):
            c.drawString(col_x[i], y, header)

        y -= 20
        for row in results:
            if y < 50:
                c.showPage()
                y = 800
                c.setFont("ArialUnicode", 10)
                for i, header in enumerate(headers):
                    c.drawString(col_x[i], y, header)
                y -= 20
            for i, value in enumerate(row):
                c.drawString(col_x[i], y, str(value or ''))
            y -= 20

        c.save()

        # Log action
        self.context.log_action("Exported expiry warning report")

        return filepath
