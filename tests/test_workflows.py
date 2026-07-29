"""
Tests for the core pharmacy workflows: goods receipt, sales and stock control.

These exercise the same SQL the UI runs, so a schema or query regression fails
here rather than in front of a user.
"""

from datetime import datetime, timedelta

import pytest

from src.utils.constants import EXPIRY_WARNING_DAYS
from tests.factories import (
    add_customer, add_invoice, add_medicine, add_stock_entry, add_supplier,
    first_category_id,
)


def stock_of(db, medicine_id):
    db.execute("SELECT stock_quantity FROM medicine WHERE medicine_id = %s", (medicine_id,))
    return db.fetchone()[0]


class TestGoodsReceipt:
    def test_stock_entry_increases_quantity(self, db):
        supplier_id = add_supplier(db)
        medicine_id = add_medicine(db, quantity=10, supplier_id=supplier_id)

        add_stock_entry(db, supplier_id, [(medicine_id, 40, 1500)])

        assert stock_of(db, medicine_id) == 50

    def test_stock_detail_lines_are_linked_to_header(self, db):
        supplier_id = add_supplier(db)
        first = add_medicine(db, "Thuốc A", supplier_id=supplier_id)
        second = add_medicine(db, "Thuốc B", supplier_id=supplier_id, batch="LOT-B")

        stock_id = add_stock_entry(db, supplier_id, [(first, 10, 100), (second, 20, 200)])

        db.execute("SELECT COUNT(*) FROM stock_detail WHERE stock_id = %s", (stock_id,))
        assert db.fetchone()[0] == 2

    def test_stock_window_query_returns_receipt_lines(self, seeded):
        """The exact join StockWindow runs must resolve against the schema."""
        db = seeded.db_manager
        supplier_id = add_supplier(db, "NCC 2")
        medicine_id = add_medicine(db, "Thuốc C", supplier_id=supplier_id, batch="LOT-C")
        add_stock_entry(db, supplier_id, [(medicine_id, 15, 900)])

        db.execute("""
            SELECT s.stock_id, sd.medicine_id, m.medicine_name,
                   sd.quantity, sd.price, sd.batch_number,
                   sd.expiration_date, sup.supplier_name,
                   s.staff_id, s.created_at
            FROM stock_detail sd
            JOIN stock s ON s.stock_id = sd.stock_id
            JOIN medicine m ON sd.medicine_id = m.medicine_id
            JOIN supplier sup ON s.supplier_id = sup.supplier_id
            ORDER BY s.created_at DESC, s.stock_id DESC
        """)
        rows = db.fetchall()

        assert len(rows) == 1
        assert rows[0][2] == "Thuốc C"
        assert rows[0][3] == 15


class TestSales:
    def test_invoice_reduces_stock(self, seeded):
        db = seeded.db_manager
        ids = _ids(db)
        before = stock_of(db, ids['paracetamol'])

        add_invoice(db, ids['customer_id'], [(ids['paracetamol'], 10, 2000)])

        assert stock_of(db, ids['paracetamol']) == before - 10

    def test_invoice_total_matches_line_items(self, seeded):
        db = seeded.db_manager
        ids = _ids(db)

        invoice_id, total = add_invoice(db, ids['customer_id'], [
            (ids['paracetamol'], 3, 2000),
            (ids['amoxicillin'], 2, 5000),
        ])

        assert total == 16000

        db.execute("SELECT total_amount FROM invoice WHERE invoice_id = %s", (invoice_id,))
        assert float(db.fetchone()[0]) == 16000

        db.execute(
            "SELECT SUM(total_price) FROM invoice_detail WHERE invoice_id = %s",
            (invoice_id,)
        )
        assert float(db.fetchone()[0]) == 16000

    def test_only_in_stock_medicines_are_sellable(self, db):
        add_medicine(db, "Còn hàng", quantity=5)
        add_medicine(db, "Hết hàng", quantity=0, batch="LOT-EMPTY")

        db.execute(
            "SELECT medicine_name FROM medicine WHERE stock_quantity > 0 ORDER BY medicine_name"
        )
        names = [row[0] for row in db.fetchall()]

        assert "Còn hàng" in names
        assert "Hết hàng" not in names

    def test_invoice_detail_join_resolves(self, seeded):
        """The join InvoiceInformationDialog runs."""
        db = seeded.db_manager
        ids = _ids(db)
        invoice_id, _ = add_invoice(db, ids['customer_id'], [(ids['paracetamol'], 2, 2000)])

        db.execute("""
            SELECT m.medicine_name, d.quantity, d.sale_price, d.total_price
            FROM invoice_detail d
            JOIN medicine m ON d.medicine_id = m.medicine_id
            WHERE d.invoice_id = %s
        """, (invoice_id,))
        rows = db.fetchall()

        assert len(rows) == 1
        assert rows[0][0] == "Paracetamol 500mg"


class TestExpiryWarning:
    def test_finds_medicine_inside_warning_window(self, db):
        add_medicine(db, "Sắp hết hạn", expires_in_days=30)
        add_medicine(db, "Còn lâu", expires_in_days=400, batch="LOT-FAR")

        names = _expiring_names(db)

        assert "Sắp hết hạn" in names
        assert "Còn lâu" not in names

    def test_excludes_already_expired(self, db):
        add_medicine(db, "Đã hết hạn", expires_in_days=-5)
        assert "Đã hết hạn" not in _expiring_names(db)

    def test_excludes_medicine_without_expiry_date(self, db):
        db.execute(
            "INSERT INTO medicine (medicine_name, stock_quantity) VALUES (%s, %s)",
            ("Không có hạn", 10)
        )
        db.commit()
        assert "Không có hạn" not in _expiring_names(db)

    @pytest.mark.parametrize("days,expected", [
        (0, True),                          # expires today
        (EXPIRY_WARNING_DAYS, True),        # exactly on the boundary
        (EXPIRY_WARNING_DAYS + 1, False),   # just outside
    ])
    def test_window_boundaries(self, db, days, expected):
        add_medicine(db, "Biên", expires_in_days=days)
        assert ("Biên" in _expiring_names(db)) is expected


class TestRevenue:
    def test_daily_revenue_totals(self, seeded):
        db = seeded.db_manager
        ids = _ids(db)
        today = datetime.now().strftime("%Y-%m-%d")

        add_invoice(db, ids['customer_id'], [(ids['paracetamol'], 5, 2000)], when=today)
        add_invoice(db, ids['customer_id'], [(ids['amoxicillin'], 2, 5000)], when=today)

        day = db.sql.date_of('invoice_date')
        db.execute(
            f"SELECT COUNT(*), SUM(total_amount) FROM invoice WHERE {day} = %s", (today,)
        )
        count, total = db.fetchone()

        assert count == 2
        assert float(total) == 20000

    def test_revenue_excludes_other_days(self, seeded):
        db = seeded.db_manager
        ids = _ids(db)
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        today = datetime.now().strftime("%Y-%m-%d")

        add_invoice(db, ids['customer_id'], [(ids['paracetamol'], 1, 2000)], when=yesterday)
        add_invoice(db, ids['customer_id'], [(ids['paracetamol'], 1, 2000)], when=today)

        day = db.sql.date_of('invoice_date')
        db.execute(f"SELECT SUM(total_amount) FROM invoice WHERE {day} = %s", (today,))
        assert float(db.fetchone()[0]) == 2000

    def test_best_selling_medicines_ranked_by_revenue(self, seeded):
        db = seeded.db_manager
        ids = _ids(db)

        add_invoice(db, ids['customer_id'], [(ids['paracetamol'], 2, 2000)])   # 4.000
        add_invoice(db, ids['customer_id'], [(ids['amoxicillin'], 5, 5000)])   # 25.000

        db.execute("""
            SELECT m.medicine_name, SUM(d.quantity), SUM(d.total_price)
            FROM invoice_detail d
            JOIN medicine m ON d.medicine_id = m.medicine_id
            GROUP BY m.medicine_name
            ORDER BY SUM(d.total_price) DESC
        """)
        rows = db.fetchall()

        assert rows[0][0] == "Amoxicillin 500mg"
        assert float(rows[0][2]) == 25000


class TestSearch:
    def test_medicine_listing_includes_uncategorised(self, db):
        """LEFT JOIN: a medicine with no category must still be listed."""
        categorised = add_medicine(db, "Có danh mục", category_id=first_category_id(db))
        uncategorised = add_medicine(db, "Không danh mục", batch="LOT-NC")

        db.execute("""
            SELECT m.medicine_id, m.medicine_name, c.category_name
            FROM medicine m
            LEFT JOIN category c ON m.category_id = c.category_id
        """)
        found = {row[0] for row in db.fetchall()}

        assert {categorised, uncategorised} <= found


def _ids(db):
    """Look up the ids created by the ``seeded`` fixture."""
    db.execute("SELECT medicine_id, medicine_name FROM medicine")
    medicines = {name: mid for mid, name in db.fetchall()}
    db.execute("SELECT customer_id FROM customer ORDER BY customer_id LIMIT 1")
    customer_id = db.fetchone()[0]

    return {
        'customer_id': customer_id,
        'paracetamol': medicines["Paracetamol 500mg"],
        'amoxicillin': medicines["Amoxicillin 500mg"],
    }


def _expiring_names(db, days=EXPIRY_WARNING_DAYS):
    """Run the dashboard's expiry-warning query and return the medicine names."""
    days_left = db.sql.days_until('expiration_date')
    db.execute(f"""
        SELECT medicine_name FROM medicine
        WHERE expiration_date IS NOT NULL
          AND {days_left} BETWEEN 0 AND {days}
    """)
    return [row[0] for row in db.fetchall()]
