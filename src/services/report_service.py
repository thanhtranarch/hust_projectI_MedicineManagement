"""
Report generation service - exports business reports to PDF.
"""

import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from src.config.settings import Settings
from src.core import sql
from src.utils.constants import EXPIRY_WARNING_DAYS

# Page layout constants (points, A4 portrait)
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 40
TOP = PAGE_HEIGHT - 60
BOTTOM = 60
LINE_HEIGHT = 16

_FONT_REGISTERED = None


def _font():
    """
    Register the bundled Unicode font once and return its name.

    Falls back to Helvetica when the font file is missing, so a stripped-down
    checkout still produces a (non-Vietnamese) PDF instead of crashing.
    """
    global _FONT_REGISTERED
    if _FONT_REGISTERED:
        return _FONT_REGISTERED

    for filename in ("arial.ttf", "Arial.ttf"):
        path = os.path.join(Settings.FONTS_DIR, filename)
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont("ReportFont", path))
                _FONT_REGISTERED = "ReportFont"
                return _FONT_REGISTERED
            except Exception:
                break

    _FONT_REGISTERED = "Helvetica"
    return _FONT_REGISTERED


def _money(value):
    """
    Format a number the Vietnamese way: dot as the thousands separator.

    The currency symbol is left off - report headers already name the unit.
    """
    try:
        return f"{float(value or 0):,.0f}".replace(',', '.')
    except (TypeError, ValueError):
        return str(value or '')


def _text(value):
    """Render a database value for display in a PDF cell."""
    if value is None:
        return ''
    if isinstance(value, datetime):
        return value.strftime("%d/%m/%Y")
    return str(value)


class ReportService:
    """Generates PDF reports from the operational database."""

    def __init__(self, context):
        self.context = context
        self.db = context.db_manager
        self.font = _font()

    # ------------------------------------------------------------------
    # PDF building blocks
    # ------------------------------------------------------------------

    def _new_document(self, filename):
        """Create a canvas under the exports directory."""
        Settings.ensure_exports_dir()
        filepath = os.path.join(Settings.EXPORTS_DIR, filename)
        return canvas.Canvas(filepath, pagesize=A4), filepath

    def _draw_heading(self, c, title, subtitle=None):
        """Draw the report title block and return the next free y position."""
        y = TOP
        c.setFont(self.font, 16)
        c.drawString(MARGIN, y, title)

        y -= 20
        c.setFont(self.font, 9)
        c.drawString(MARGIN, y, f"Xuất lúc: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

        if subtitle:
            y -= 14
            c.drawString(MARGIN, y, subtitle)

        return y - 24

    def _draw_row(self, c, y, columns, values, bold=False):
        """Draw one row of cells at the given column offsets."""
        c.setFont(self.font, 10 if bold else 9)
        for (x, _, align), value in zip(columns, values):
            if align == 'r':
                c.drawRightString(x, y, value)
            else:
                c.drawString(x, y, value)
        return y - LINE_HEIGHT

    def _draw_table(self, c, y, columns, rows):
        """
        Draw a table, repeating the header on every page.

        Args:
            columns: list of (x, header, align) where align is 'l' or 'r'
            rows: list of already-formatted string tuples
        """
        y = self._draw_row(c, y, columns, [h for _, h, _ in columns], bold=True)
        c.line(MARGIN, y + 10, PAGE_WIDTH - MARGIN, y + 10)

        for row in rows:
            if y < BOTTOM:
                c.showPage()
                y = TOP
                y = self._draw_row(c, y, columns, [h for _, h, _ in columns], bold=True)
                c.line(MARGIN, y + 10, PAGE_WIDTH - MARGIN, y + 10)
            y = self._draw_row(c, y, columns, row)

        return y

    def _finish(self, c, filepath, action):
        """Save the document and record the export in the activity log."""
        c.save()
        self.context.log_action(action)
        return filepath

    # ------------------------------------------------------------------
    # Reports
    # ------------------------------------------------------------------

    def export_stock_report(self):
        """Inventory on hand, with stock valued at sale price."""
        self.db.execute("""
            SELECT medicine_name, unit, stock_quantity, batch_number, sale_price
            FROM medicine
            ORDER BY medicine_name
        """)
        results = self.db.fetchall()

        c, filepath = self._new_document(
            f"report_stock_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        y = self._draw_heading(c, "BÁO CÁO TỒN KHO")

        columns = [
            (MARGIN, "Tên thuốc", 'l'),
            (MARGIN + 200, "Đơn vị", 'l'),
            (MARGIN + 300, "Tồn kho", 'r'),
            (MARGIN + 380, "Số lô", 'l'),
            (PAGE_WIDTH - MARGIN, "Giá bán", 'r'),
        ]
        rows = [
            (_text(name), _text(unit), _text(qty), _text(batch), _money(price))
            for name, unit, qty, batch, price in results
        ]
        y = self._draw_table(c, y, columns, rows)

        total_value = sum(float(qty or 0) * float(price or 0)
                          for _, _, qty, _, price in results)
        c.setFont(self.font, 10)
        c.drawString(MARGIN, y - 10, f"Tổng số mặt hàng: {len(results)}")
        c.drawString(MARGIN, y - 26, f"Tổng giá trị tồn kho: {_money(total_value)} VND")

        return self._finish(c, filepath, "Xuất báo cáo tồn kho")

    def export_invoice_report(self, date=None):
        """All invoices issued on a given day."""
        date = date or datetime.now().strftime('%Y-%m-%d')

        self.db.execute("""
            SELECT i.invoice_id, i.invoice_date, c.customer_name,
                   i.staff_id, i.total_amount, i.payment_status
            FROM invoice i
            LEFT JOIN customer c ON i.customer_id = c.customer_id
            WHERE date(i.invoice_date) = %s
            ORDER BY i.invoice_date DESC
        """, (date,))
        results = self.db.fetchall()

        c, filepath = self._new_document(f"report_invoice_{date}.pdf")
        y = self._draw_heading(c, "BÁO CÁO HÓA ĐƠN", f"Ngày: {date}")

        columns = [
            (MARGIN, "Mã HĐ", 'l'),
            (MARGIN + 60, "Thời gian", 'l'),
            (MARGIN + 160, "Khách hàng", 'l'),
            (MARGIN + 300, "Nhân viên", 'l'),
            (MARGIN + 430, "Tổng tiền", 'r'),
            (PAGE_WIDTH - MARGIN, "Trạng thái", 'r'),
        ]
        rows = [
            (_text(inv_id),
             dt.strftime('%H:%M') if isinstance(dt, datetime) else _text(dt),
             _text(customer), _text(staff), _money(total), _text(status))
            for inv_id, dt, customer, staff, total, status in results
        ]
        y = self._draw_table(c, y, columns, rows)

        total_amount = sum(float(row[4] or 0) for row in results)
        c.setFont(self.font, 10)
        c.drawString(MARGIN, y - 10, f"Số hóa đơn: {len(results)}")
        c.drawString(MARGIN, y - 26, f"Tổng doanh thu: {_money(total_amount)} VND")

        return self._finish(c, filepath, f"Xuất báo cáo hóa đơn ngày {date}")

    def export_expiry_warning_report(self, days=EXPIRY_WARNING_DAYS):
        """Medicines expiring within the warning window."""
        days_left = sql.days_until('expiration_date')
        self.db.execute(f"""
            SELECT medicine_name, stock_quantity, unit, batch_number,
                   expiration_date, {days_left} AS days_left
            FROM medicine
            WHERE expiration_date IS NOT NULL
              AND {days_left} BETWEEN 0 AND {int(days)}
            ORDER BY expiration_date ASC
        """)
        results = self.db.fetchall()

        c, filepath = self._new_document(
            f"report_expiring_{datetime.now().strftime('%Y%m%d')}.pdf"
        )
        y = self._draw_heading(
            c, "BÁO CÁO THUỐC SẮP HẾT HẠN", f"Ngưỡng cảnh báo: {int(days)} ngày"
        )

        columns = [
            (MARGIN, "Tên thuốc", 'l'),
            (MARGIN + 200, "SL", 'r'),
            (MARGIN + 240, "ĐV", 'l'),
            (MARGIN + 300, "Số lô", 'l'),
            (MARGIN + 400, "Hạn dùng", 'l'),
            (PAGE_WIDTH - MARGIN, "Còn lại (ngày)", 'r'),
        ]
        rows = [
            (_text(name), _text(qty), _text(unit), _text(batch),
             _text(exp), _text(left))
            for name, qty, unit, batch, exp, left in results
        ]
        y = self._draw_table(c, y, columns, rows)

        c.setFont(self.font, 10)
        c.drawString(MARGIN, y - 10, f"Số mặt hàng cần xử lý: {len(results)}")

        return self._finish(c, filepath, "Xuất báo cáo thuốc sắp hết hạn")

    def export_revenue_report(self, start_date=None, end_date=None):
        """
        Revenue over a date range: daily totals plus best-selling medicines.

        Args:
            start_date: 'YYYY-MM-DD', defaults to the first day of this month
            end_date: 'YYYY-MM-DD', defaults to today
        """
        today = datetime.now()
        start_date = start_date or today.replace(day=1).strftime('%Y-%m-%d')
        end_date = end_date or today.strftime('%Y-%m-%d')

        self.db.execute("""
            SELECT date(invoice_date) AS day, COUNT(*), SUM(total_amount)
            FROM invoice
            WHERE date(invoice_date) BETWEEN %s AND %s
            GROUP BY date(invoice_date)
            ORDER BY day
        """, (start_date, end_date))
        daily = self.db.fetchall()

        self.db.execute("""
            SELECT m.medicine_name, SUM(d.quantity), SUM(d.total_price)
            FROM invoice_detail d
            JOIN invoice i ON d.invoice_id = i.invoice_id
            JOIN medicine m ON d.medicine_id = m.medicine_id
            WHERE date(i.invoice_date) BETWEEN %s AND %s
            GROUP BY m.medicine_name
            ORDER BY SUM(d.total_price) DESC
        """, (start_date, end_date))
        top_products = self.db.fetchall()

        c, filepath = self._new_document(f"report_revenue_{start_date}_{end_date}.pdf")
        y = self._draw_heading(
            c, "BÁO CÁO DOANH THU", f"Từ ngày {start_date} đến ngày {end_date}"
        )

        total_revenue = sum(float(row[2] or 0) for row in daily)
        total_invoices = sum(int(row[1] or 0) for row in daily)
        average = total_revenue / total_invoices if total_invoices else 0

        c.setFont(self.font, 11)
        for line in (
            f"Tổng doanh thu: {_money(total_revenue)} VND",
            f"Số hóa đơn: {total_invoices}",
            f"Giá trị trung bình mỗi hóa đơn: {_money(average)} VND",
        ):
            c.drawString(MARGIN, y, line)
            y -= LINE_HEIGHT
        y -= 14

        c.setFont(self.font, 12)
        c.drawString(MARGIN, y, "Doanh thu theo ngày")
        y -= 20
        y = self._draw_table(c, y, [
            (MARGIN, "Ngày", 'l'),
            (MARGIN + 200, "Số hóa đơn", 'r'),
            (PAGE_WIDTH - MARGIN, "Doanh thu (VND)", 'r'),
        ], [(_text(day), _text(count), _money(amount)) for day, count, amount in daily])

        if top_products:
            y -= 20
            if y < BOTTOM + 80:
                c.showPage()
                y = TOP
            c.setFont(self.font, 12)
            c.drawString(MARGIN, y, "Thuốc bán chạy")
            y -= 20
            self._draw_table(c, y, [
                (MARGIN, "Tên thuốc", 'l'),
                (MARGIN + 280, "Số lượng bán", 'r'),
                (PAGE_WIDTH - MARGIN, "Doanh thu (VND)", 'r'),
            ], [(_text(name), _text(qty), _money(amount))
                for name, qty, amount in top_products])

        return self._finish(
            c, filepath, f"Xuất báo cáo doanh thu {start_date} - {end_date}"
        )
