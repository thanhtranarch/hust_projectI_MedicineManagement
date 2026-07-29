"""
Stock entry detail dialog (read-only).
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTableWidgetItem

from src.ui.base import BaseDialog
from src.utils.helpers import format_currency

DETAIL_HEADERS = ["Thuốc", "Số lượng", "Đơn giá", "Thành tiền",
                  "Số lô", "Hạn dùng", "Ghi chú"]


class StockInformationDialog(BaseDialog):
    """Shows one goods-receipt document and the medicines it brought in."""

    def __init__(self, context, stock_id, parent=None):
        super().__init__(context, 'stock_information.ui', 'Chi tiết phiếu nhập kho', parent)

        self.stock_id_value = stock_id
        self.close_button.clicked.connect(self.accept)

        self.detail_table.setColumnCount(len(DETAIL_HEADERS))
        self.detail_table.setHorizontalHeaderLabels(DETAIL_HEADERS)

        self.load_stock_data()

    def load_stock_data(self):
        """Load the header row and its detail lines."""
        try:
            self.db.execute("""
                SELECT s.stock_id, sup.supplier_name, st.staff_name,
                       p.payment_name, s.created_at
                FROM stock s
                LEFT JOIN supplier sup ON s.supplier_id = sup.supplier_id
                LEFT JOIN staff st ON s.staff_id = st.staff_id
                LEFT JOIN payment_method p ON s.payment_method_id = p.payment_method_id
                WHERE s.stock_id = %s
            """, (self.stock_id_value,))
            header = self.db.fetchone()

            if not header:
                self.show_warning("Không tìm thấy phiếu nhập kho")
                self.reject()
                return

            stock_id, supplier, staff, payment, created = header
            self.stock_id_field.setText(str(stock_id))
            self.supplier_field.setText(supplier or '')
            self.staff_field.setText(staff or '')
            self.payment_field.setText(payment or '')
            self.created_field.setText(
                created.strftime("%d/%m/%Y %H:%M") if hasattr(created, 'strftime')
                else str(created or '')
            )

            self.load_details()

        except Exception as e:
            self.show_error(f"Lỗi khi tải phiếu nhập kho: {e}")

    def load_details(self):
        """Fill the detail table and the total."""
        self.db.execute("""
            SELECT m.medicine_name, d.quantity, d.price,
                   d.batch_number, d.expiration_date, d.note
            FROM stock_detail d
            LEFT JOIN medicine m ON d.medicine_id = m.medicine_id
            WHERE d.stock_id = %s
            ORDER BY d.stock_detail_id
        """, (self.stock_id_value,))
        rows = self.db.fetchall()

        self.detail_table.setRowCount(len(rows))
        total = 0

        for row_idx, (name, quantity, price, batch, expiry, note) in enumerate(rows):
            line_total = float(quantity or 0) * float(price or 0)
            total += line_total

            values = [
                name or '',
                str(quantity or 0),
                format_currency(price),
                format_currency(line_total),
                batch or '',
                expiry.strftime("%d/%m/%Y") if hasattr(expiry, 'strftime') else str(expiry or ''),
                note or '',
            ]
            for col_idx, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.detail_table.setItem(row_idx, col_idx, item)

        self.detail_table.resizeColumnsToContents()
        self.total_label.setText(f"Tổng tiền: {format_currency(total)}")
